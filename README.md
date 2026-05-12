# sd-webui-prompt-checkpoint-override

A lightweight extension for AUTOMATIC1111 Stable Diffusion WebUI that allows you to switch checkpoints from inside the prompt or wildcard using `ckptalias_` tags.

プロンプトや Dynamic Prompts / wildcard の中から、checkpoint を一時的に切り替えるための拡張機能です。

---

# 日本語

## 概要

`sd-webui-prompt-checkpoint-override` は、AUTOMATIC1111 Stable Diffusion WebUI 用の軽量拡張機能です。

プロンプト内に専用タグを書くことで、画像生成時に使用する checkpoint を一時的に切り替えることができます。

特に Dynamic Prompts / wildcard と組み合わせて、プロンプトごとに異なる checkpoint を使い分けたい場合に便利です。

生成後は、元の checkpoint に自動で戻します。

---

## 主な機能

### プロンプトから checkpoint を切り替え

プロンプト内に以下のようなタグを書くことで、指定した checkpoint に切り替えて生成できます。

```txt
ckptalias_modelName
masterpiece, best quality, 1girl
```

例：

```txt
ckptalias_Illustrious-XL
masterpiece, best quality, anime coloring, 1girl, solo
```

`ckptalias_` の後ろに書いた文字列をもとに、WebUI に登録されている checkpoint を検索します。

wildcard 内で checkpoint 名とプロンプト傾向をセットにしておくことで、モデルごとの比較やランダム生成がしやすくなります。

---

### 別形式にも対応

以下の形式にも対応しています。

```txt
%%ckpt:modelName%%
masterpiece, best quality, 1girl
```

ただし、Dynamic Prompts / wildcard 内では `%%` を含む形式が不具合の原因になる場合があります。

そのため、wildcard で使用する場合は以下の形式を推奨します。

```txt
ckptalias_modelName
```

---

### Positive / Negative 両方から検出

checkpoint 指定タグは、Positive prompt と Negative prompt の両方から検出されます。

検出されたタグは、生成前にプロンプトから自動的に削除されます。

そのため、最終的な画像生成プロンプトには `ckptalias_` タグ自体は残りません。

---

### 生成後に元の checkpoint へ復元

checkpoint を一時的に切り替えた場合、生成後に元の checkpoint へ自動で戻します。

普段使っている checkpoint を手動で戻す必要はありません。

---

## インストール方法

### URLからインストール

AUTOMATIC1111 WebUI の拡張機能画面から、GitHub URLを指定してインストールできます。

1. AUTOMATIC1111 WebUI を開く
2. `Extensions` タブを開く
3. `Install from URL` を開く
4. `URL for extension's git repository` に以下のURLを貼り付ける

```txt
https://github.com/mulnyanko77/sd-webui-prompt-checkpoint-override
```

5. `Install` を押す
6. インストール完了後、AUTOMATIC1111 WebUI を再起動する

この方法でインストールすると、通常は以下の場所に拡張機能が配置されます。

```txt
stable-diffusion-webui/extensions/sd-webui-prompt-checkpoint-override/
```

---

### 手動インストール

このリポジトリをダウンロードして、AUTOMATIC1111 WebUI の `extensions` フォルダに配置します。

```txt
stable-diffusion-webui/extensions/
```

期待されるフォルダ構成：

```txt
stable-diffusion-webui/
└─ extensions/
   └─ sd-webui-prompt-checkpoint-override/
      └─ scripts/
         └─ prompt_checkpoint_override.py
```

配置後、AUTOMATIC1111 WebUI を再起動してください。

---

## 注意点

* 1回の生成バッチ内で指定できる checkpoint は1つだけです。
* 同じ生成バッチ内に複数の異なる checkpoint 指定がある場合、エラーで停止します。
* `ckptalias_` 形式では、スペースを含む checkpoint 名を直接指定することは想定していません。
* スペースを含む名前の場合は、スペースを含まない一意な部分文字列で指定してください。
* checkpoint 名は部分一致で検索されるため、似た名前のモデルが複数ある場合は意図しない checkpoint が選ばれる可能性があります。
* wildcard で使用する場合は、`%%ckpt:modelName%%` 形式ではなく `ckptalias_modelName` 形式を推奨します。
* checkpoint の切り替えにはモデルの再読み込みが発生するため、通常の生成より時間がかかる場合があります。
* この拡張は小規模な個人利用向け拡張として作成されています。
* 環境や AUTOMATIC1111 WebUI / Forge のバージョンによっては、動作が変わる可能性があります。

---

## License

MIT License

---

# English

## Overview

`sd-webui-prompt-checkpoint-override` is a lightweight extension for AUTOMATIC1111 Stable Diffusion WebUI.

By writing a special tag inside the prompt, you can temporarily switch the checkpoint used for image generation.

This is especially useful when combined with Dynamic Prompts / wildcards, allowing you to use different checkpoints for different prompt patterns.

After generation, the extension automatically restores the original checkpoint.

---

## Features

### Switch checkpoints from the prompt

You can switch to a specified checkpoint by writing a tag like this inside the prompt:

```txt
ckptalias_modelName
masterpiece, best quality, 1girl
```

Example:

```txt
ckptalias_Illustrious-XL
masterpiece, best quality, anime coloring, 1girl, solo
```

The extension searches the checkpoints registered in WebUI using the string written after `ckptalias_`.

By placing checkpoint names and prompt styles together inside wildcard files, it becomes easier to compare models or generate randomized outputs with matching model-specific prompts.

---

### Alternative syntax support

The following syntax is also supported:

```txt
%%ckpt:modelName%%
masterpiece, best quality, 1girl
```

However, syntax containing `%%` may cause issues inside Dynamic Prompts / wildcard files.

For wildcard usage, the following syntax is recommended:

```txt
ckptalias_modelName
```

---

### Detection from both Positive and Negative prompts

Checkpoint override tags are detected from both the Positive prompt and the Negative prompt.

Detected tags are automatically removed from the prompt before generation.

As a result, the `ckptalias_` tag itself will not remain in the final generation prompt.

---

### Restore the original checkpoint after generation

When the checkpoint is temporarily switched, the extension automatically restores the original checkpoint after generation.

You do not need to manually switch back to the checkpoint you normally use.

---

## Installation

### Install from URL

You can install this extension from the Extensions page in AUTOMATIC1111 WebUI by specifying the GitHub URL.

1. Open AUTOMATIC1111 WebUI
2. Go to the `Extensions` tab
3. Open `Install from URL`
4. Paste the following URL into `URL for extension's git repository`

```txt
https://github.com/mulnyanko77/sd-webui-prompt-checkpoint-override
```

5. Click `Install`
6. Restart AUTOMATIC1111 WebUI after installation

When installed this way, the extension is usually placed in the following folder:

```txt
stable-diffusion-webui/extensions/sd-webui-prompt-checkpoint-override/
```

---

### Manual installation

Download this repository and place it inside the `extensions` folder of AUTOMATIC1111 WebUI.

```txt
stable-diffusion-webui/extensions/
```

Expected folder structure:

```txt
stable-diffusion-webui/
└─ extensions/
   └─ sd-webui-prompt-checkpoint-override/
      └─ scripts/
         └─ prompt_checkpoint_override.py
```

After placing the files, restart AUTOMATIC1111 WebUI.

---

## Notes

* Only one checkpoint can be specified in a single generation batch.
* If multiple different checkpoint overrides are detected in the same generation batch, generation will stop with an error.
* The `ckptalias_` syntax is not intended to directly specify checkpoint names that contain spaces.
* If a checkpoint name contains spaces, use a unique substring that does not contain spaces.
* Checkpoint names are matched by partial matching, so if multiple models have similar names, an unintended checkpoint may be selected.
* When using wildcards, `ckptalias_modelName` is recommended instead of `%%ckpt:modelName%%`.
* Switching checkpoints requires reloading model weights, so generation may take longer than usual.
* This extension was created as a small personal-use extension.
* Behavior may vary depending on your environment and the version of AUTOMATIC1111 WebUI / Forge.

---

## License

MIT License
