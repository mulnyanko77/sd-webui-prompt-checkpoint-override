import re
from typing import List, Tuple

from modules import scripts, shared, sd_models


# Supported syntax:
#   1. %%ckpt:model_name%%
#   2. ckptalias_model_name
#
# The ckptalias_ syntax is recommended for Dynamic Prompts / wildcards,
# because symbols such as %% may cause issues in wildcard files.
CKPT_PATTERN = re.compile(
    r"(?:%%ckpt:([^%]+)%%|ckptalias_([A-Za-z0-9_.\-]+)[ \t]*)",
    re.IGNORECASE,
)


def strip_ckpt_tags(text: str) -> Tuple[str, List[str]]:
    """
    Detect checkpoint override tags in a prompt and remove them.

    Supported formats:
        %%ckpt:model_name%%
        ckptalias_model_name

    Returns:
        cleaned_text, checkpoint_names
    """
    if not text:
        return text, []

    names: List[str] = []

    def repl(match: re.Match) -> str:
        old_style = match.group(1)
        alias_style = match.group(2)

        name = old_style or alias_style
        if name:
            names.append(name.strip())

        return ""

    cleaned = CKPT_PATTERN.sub(repl, text).strip()
    return cleaned, names


def find_checkpoint(name: str):
    """
    Find a matching checkpoint from the WebUI checkpoint list.

    This first uses WebUI's built-in matcher, then falls back to partial
    matching against title, model_name, filename, and name.
    """
    if not name:
        return None

    # A1111 exposes this function with the original "closet" spelling.
    getter = getattr(sd_models, "get_closet_checkpoint_match", None)
    if getter is not None:
        try:
            info = getter(name)
            if info is not None:
                return info
        except Exception:
            pass

    name_lower = name.lower()

    for title, info in sd_models.checkpoints_list.items():
        candidates = [
            str(title),
            getattr(info, "title", ""),
            getattr(info, "model_name", ""),
            getattr(info, "filename", ""),
            getattr(info, "name", ""),
        ]

        for candidate in candidates:
            if candidate and name_lower in str(candidate).lower():
                return info

    return None


def current_checkpoint_info():
    """Return the currently loaded checkpoint info."""
    sd_model = getattr(shared, "sd_model", None)
    if sd_model is None:
        return None

    return getattr(sd_model, "sd_checkpoint_info", None)


def checkpoint_title(info) -> str:
    if info is None:
        return ""
    return getattr(info, "title", str(info))


def is_same_checkpoint(a, b) -> bool:
    if a is None or b is None:
        return False
    return checkpoint_title(a) == checkpoint_title(b)


def switch_checkpoint(checkpoint_info):
    """Switch to the specified checkpoint."""
    if checkpoint_info is None:
        return

    current_info = current_checkpoint_info()

    if is_same_checkpoint(current_info, checkpoint_info):
        return

    title = checkpoint_title(checkpoint_info)
    print(f"[Prompt Checkpoint Override] Switching checkpoint to: {title}")

    shared.opts.data["sd_model_checkpoint"] = title
    sd_models.reload_model_weights(shared.sd_model, checkpoint_info)


def extract_ckpt_from_prompts(prompts: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extract checkpoint override tags from multiple prompts.

    Returns:
        cleaned_prompts, checkpoint_names
    """
    cleaned_prompts: List[str] = []
    found_names: List[str] = []

    for prompt in prompts:
        cleaned, names = strip_ckpt_tags(prompt or "")
        cleaned_prompts.append(cleaned)
        found_names.extend(names)

    return cleaned_prompts, found_names


class PromptCheckpointOverrideScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.original_checkpoint = None
        self.switched = False
        self.current_override_title = None

    def title(self):
        return "Prompt Checkpoint Override"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return []

    def _set_original_checkpoint_if_needed(self):
        if self.original_checkpoint is None:
            self.original_checkpoint = current_checkpoint_info()

    def _apply_checkpoint_override(self, p, ckpt_names: List[str]):
        if not ckpt_names:
            return

        unique_names = list(dict.fromkeys([x.strip() for x in ckpt_names if x.strip()]))

        if not unique_names:
            return

        if len(unique_names) > 1:
            raise RuntimeError(
                "[Prompt Checkpoint Override] Multiple checkpoint overrides "
                "in a single generation batch are not supported: "
                + ", ".join(unique_names)
            )

        ckpt_name = unique_names[0]
        checkpoint_info = find_checkpoint(ckpt_name)

        if checkpoint_info is None:
            raise RuntimeError(
                f"[Prompt Checkpoint Override] Checkpoint not found: {ckpt_name}"
            )

        self._set_original_checkpoint_if_needed()

        switch_checkpoint(checkpoint_info)

        if hasattr(p, "sd_model"):
            p.sd_model = shared.sd_model

        self.switched = True
        self.current_override_title = checkpoint_title(checkpoint_info)

        try:
            p.extra_generation_params["Prompt checkpoint override"] = self.current_override_title
        except Exception:
            pass

    def process(self, p, *args):
        """
        Handle direct prompt usage before wildcard expansion.

        Examples:
            %%ckpt:model_name%%
            ckptalias_model_name
        """
        prompt = getattr(p, "prompt", "") or ""
        negative_prompt = getattr(p, "negative_prompt", "") or ""

        cleaned_prompt, positive_names = strip_ckpt_tags(prompt)
        cleaned_negative, negative_names = strip_ckpt_tags(negative_prompt)

        ckpt_names = positive_names + negative_names

        if not ckpt_names:
            return

        p.prompt = cleaned_prompt
        p.negative_prompt = cleaned_negative

        self._apply_checkpoint_override(p, ckpt_names)

    def process_batch(self, p, *args, **kwargs):
        """
        Handle prompts after Dynamic Prompts / wildcard expansion.

        Recommended wildcard syntax:
            ckptalias_modelName, masterpiece, best quality, 1girl
        """
        prompts = kwargs.get("prompts", None)
        negative_prompts = kwargs.get("negative_prompts", None)

        found_names: List[str] = []

        if prompts:
            cleaned_prompts, names = extract_ckpt_from_prompts(list(prompts))
            found_names.extend(names)

            try:
                prompts[:] = cleaned_prompts
            except Exception:
                kwargs["prompts"] = cleaned_prompts

            if hasattr(p, "all_prompts") and p.all_prompts:
                try:
                    p.all_prompts = cleaned_prompts
                except Exception:
                    pass

            if cleaned_prompts:
                try:
                    p.prompt = cleaned_prompts[0]
                except Exception:
                    pass

        if negative_prompts:
            cleaned_negative_prompts, names = extract_ckpt_from_prompts(list(negative_prompts))
            found_names.extend(names)

            try:
                negative_prompts[:] = cleaned_negative_prompts
            except Exception:
                kwargs["negative_prompts"] = cleaned_negative_prompts

            if hasattr(p, "all_negative_prompts") and p.all_negative_prompts:
                try:
                    p.all_negative_prompts = cleaned_negative_prompts
                except Exception:
                    pass

            if cleaned_negative_prompts:
                try:
                    p.negative_prompt = cleaned_negative_prompts[0]
                except Exception:
                    pass

        if found_names:
            self._apply_checkpoint_override(p, found_names)

    def postprocess(self, p, processed, *args):
        """Restore the original checkpoint after generation."""
        if not self.switched:
            return

        if self.original_checkpoint is None:
            return

        current_info = current_checkpoint_info()

        if is_same_checkpoint(current_info, self.original_checkpoint):
            self._reset_state()
            return

        title = checkpoint_title(self.original_checkpoint)
        print(f"[Prompt Checkpoint Override] Restoring checkpoint to: {title}")

        shared.opts.data["sd_model_checkpoint"] = title
        sd_models.reload_model_weights(shared.sd_model, self.original_checkpoint)

        if hasattr(p, "sd_model"):
            p.sd_model = shared.sd_model

        self._reset_state()

    def _reset_state(self):
        self.original_checkpoint = None
        self.switched = False
        self.current_override_title = None
