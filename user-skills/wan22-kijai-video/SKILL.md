---
name: wan22-kijai-video
description: Wan2.2 I2VをKijai WanVideoWrapperとLightX2V 4-step LoRAで安全に準備・実行・再開・診断する。ユーザーが「動画生成したい」「Wanで動画を作って」「Kijaiで生成」「Wan2.2を回して」、RTX3080上のComfyUI生成、KaggleでのKijai事前確認、またはこの環境のWan動画生成エラー修正を依頼したときに使う。
---

# Wan2.2 Kijai Video

`references/environment.md` を読み、現在のモデルpin、template、runner、Kaggleの制約を確認してから操作する。

## 対話と実行の境界

- ユーザーが実際に「生成する」と依頼した場合だけ、ComfyUIへpromptを送信する。設定確認・性能相談・エラー診断では送信しない。
- config、profile、beat、開始画像、プロンプトが既存設定で一意でない場合だけ、必要な値を短く確認する。既存configが指定されている場合は推測で置換しない。
- productionのbeat 1は、runnerが要求する承認済みpreview manifestなしに開始しない。
- 1回の `run-beat` は1 beat（21 frames）だけである。人間のmotion auditと承認なしに次beatやfinalizeを進めない。

## 実行前の安全確認

1. 対象configを読み、backend、モデルSHA、profile、run journalを確認する。
2. RTX3080のComfyUI `/queue` を読み取る。running/pending promptが1件でもあれば、restart、`/free`、新規prompt送信を行わない。自分のpromptはjournal/historyの照合だけを許可し、空いた後に再開する。
3. Kijai backendでは、WanVideoWrapper commit、`WanVideoConditioningLimit`、high/low LoRA、template SHAをpreflightで検証する。欠損やSHA不一致はFail Fastで止める。
4. 再起動はComfyUIがidleであり、かつcustom nodeやwrapperを新規導入・更新した場合だけ行う。グローバル `/free` は使わない。

## Kijai生成

- `wanvideowrapper` backendでは、high/lowをそれぞれ2 stepsにし、合計4 steps、CFG 1、Euler、LightX2V sigma scheduleを厳守する。
- ネイティブT5 embeddingは必ず `CLIPTextEncode → WanVideoConditioningLimit(max_tokens=512) → WanVideoTextEmbedBridge` と接続する。長文を文字列で勝手に短縮して回避しない。
- 実行前にrunnerの `dry-run`、実行時は `run-beat --beat N` を使う。中断後はjournalとComfyUI historyを照合し、submission outcomeが不明なら `--resume` で再送しない。
- 完了後は21枚のraw frames、local QA、journalを確認して報告する。承認コマンドはユーザーが明示的に判断した場合だけ実行する。

## Kaggle

Kaggle artifactはモデルとKijai nodeのpreflight専用であり、現在は動画生成runnerではない。Kaggle生成を約束・実行しない。private `wan22-i2v-models` inputが未接続なら、必要なlayoutを示して停止する。

## 完了報告

backend、wrapper commit、LoRA SHA、実行したbeat、出力先、実測時間、失敗時のjournal/history prompt IDを示す。実機生成をしていない場合は、その理由と次の安全な操作を明記する。
