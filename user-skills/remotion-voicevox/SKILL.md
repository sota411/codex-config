---
name: remotion-voicevox
description: RemotionとVOICEVOXで、ずんだもん・四国めたんの掛け合い解説動画を作成・編集する。台本、字幕、立ち絵の口パク、音声生成、MP4出力を扱う。nyanko3141592/remotion-voicevox-templateを使う動画制作に適用し、通知音や音声だけの読み上げには使わない。
license: MIT
metadata:
  upstream: https://github.com/nyanko3141592/remotion-voicevox-template
  upstream-revision: a88a952d3934180b74d5bdc8f567a256ae63ad20
---

# Remotion + VOICEVOXで解説動画を作る

[nyanko3141592/remotion-voicevox-template](https://github.com/nyanko3141592/remotion-voicevox-template/tree/a88a952d3934180b74d5bdc8f567a256ae63ad20)のスキルをCodex向けに調整したもの。上記revisionのコードに基づく。作成した動画プロジェクトを作業場所とし、以降の相対パスとnpmコマンドはすべてそのルートを基準とする。

## プロジェクトを準備する

- テーマ、視聴者、長さ、素材、出力先を依頼から把握する。指定がなければ、ずんだもんを説明役、四国めたんを聞き役とする。
- 既存プロジェクトでは`package.json`と対象ファイルを確認し、そのプロジェクトの設定や変更を優先する。
- 新規作成では、空いている出力先へ次のテンプレートを取得する。`my-video`は依頼に合うディレクトリ名へ置き換える。スキルのインストール先に動画プロジェクトを作らない。

```bash
git clone https://github.com/nyanko3141592/remotion-voicevox-template.git my-video
cd my-video
git checkout a88a952d3934180b74d5bdc8f567a256ae63ad20
npm ci
npm run sync
```

Node.js、npm、Python 3とVOICEVOX Engineが必要。音声生成時には既存のEngineを利用し、`http://localhost:50021/version`と`/speakers`で起動状態と話者を確認する。OSに合う起動方法を使う。通常のCLI操作にはGUIエディターやClaude Codeの導入は不要。

`npm run init`は通常の初期設定に使わない。このrevisionでは台本の正本をリセットせず、既存の音声・出力動画を削除する。

## 編集するファイル

| 対象 | 編集元・役割 |
|---|---|
| 台本、字幕用の表記、画像・文字の表示、効果音 | `config/script.yaml` |
| 字幕、立ち絵、色などの見た目 | `video-settings.yaml` |
| 台本行の既定値 | `config/defaults.yaml` |
| キャラクター設定 | `config/characters.yaml`。話者追加にはコード側の対応も必要 |
| 解像度、fps、再生速度 | `src/config.ts`の`VIDEO_CONFIG`。生成・再生側も確認する |
| 生成される台本・設定 | `src/data/script.ts`、`src/settings.generated.ts`。直接編集しない |
| 音声と計測フレーム数 | `public/voices/*.wav`、`public/voices/durations.json` |
| 最終出力 | `out/video.mp4` |

初回の音声生成前に[テンプレートの注意点](references/template-notes.md)の「音声生成とタイミング」を読む。BGM、話者追加、再生速度変更、GUIを扱う場合は同資料の該当節も読む。上流の`SKILL.md`や`CLAUDE.md`には旧手順が残っているため、現在のコードと一致するか確認する。

## 掛け合い台本を作る

説明役がテーマを示し、聞き役が質問し、具体例を挟んで要点をまとめる。ユーザーの構成やキャラクター指定がある場合はそれに合わせる。ずんだもんは「〜なのだ」、めたんは「〜ね」「〜かしら？」を基本とする。解説内容は資料に基づいて書き、推測や未確認の情報を事実として読ませない。

`config/script.yaml`の例：

```yaml
- id: 1
  character: zundamon
  text: エーピーアイの仕組みを紹介するのだ！
  displayText: APIの仕組みを紹介するのだ！
  scene: 1
  pauseAfter: 15
  emotion: normal
  visual:
    type: text
    text: APIの仕組み
    fontSize: 80
    animation: fadeIn

- id: 2
  character: metan
  text: どんなときに使うのかしら？
  scene: 1
  pauseAfter: 15
```

- `id`は重複しない整数にする。既定の音声対象は`zundamon`と`metan`。
- 読み間違える語は`text`を読みやすい表記にし、字幕に出す表記を`displayText`に分ける。発音は実際の音声で確かめる。
- `voiceFile`と`durationInFrames`は同期処理と音声計測から生成する。推定秒数だけで完成としない。
- `pauseAfter`はセリフ後の間を表すフレーム数。速度による調整も踏まえ、聞いて自然な間にする。`0`にしても二人の同時発声にはならない。
- 画像は`visual: {type: image, src: example.png, animation: fadeIn}`で指定し、`public/content/example.png`へ置く。効果音は`se: {src: point.mp3, volume: 0.8}`で指定し、`public/se/point.mp3`へ置く。

## 素材と見た目を整える

解説の画像や図を大きく表示し、字幕を下部、立ち絵を左右下部に配置する。字幕で重要な内容を隠さず、見切れがあれば配置や余白を調整する。サイズや色は`video-settings.yaml`から変更し、反映されない項目は対応コンポーネントの参照先を確認する。

立ち絵は`public/images/{characterId}/`へ配置し、`video-settings.yaml`の`character.useImages`を`true`にする。

```text
mouth_open.png       通常の口開き
mouth_close.png      通常の口閉じ
happy_open.png       表情差分の口開き（任意）
happy_close.png      表情差分の口閉じ（任意）
```

`surprised`、`thinking`、`sad`も同じ命名で追加できる。表情差分や効果音は要点や反応に合わせて使う。素材の配置後に`npm run sync`を実行する。

立ち絵はユーザーが提供した素材や、利用条件を確認できる素材を使う。[東北ずん子・ずんだもん公式](https://zunko.jp/con_illust.html)などの配布元と、音声・各素材の必要なクレジットを確認する。同梱のプレースホルダーを使うプレビューでは、仮素材であることを明示する。

## 音声生成から書き出しまで

台本の変更後は、必ず同期してから音声を生成する。`npm run voices`は生成済みのTSを先に読むため、この順序が必要になる。

```bash
npm run sync
curl --fail --silent --show-error --max-time 5 http://localhost:50021/version
npm run voices
```

音声生成後は、処理したセリフ数と台本の件数を照合する。全行のWAVが生成され、`durations.json`に対応する正のフレーム数があることを確かめる。このrevisionは一部の生成失敗でも成功終了するため、終了コードだけで完了としない。

`npm start`でプレビューを起動し、実際の表示と音声を確認する。冒頭、話者の切り替わり、長い字幕、最後のセリフを確認し、字幕のはみ出し、読み間違い、口パクの継続、不要な無音を修正する。確認できなかった項目は報告に残す。

```bash
npm run build
```

書き出しはプロセス終了まで待ち、MP4の存在、映像・音声トラック、長さ、解像度を`ffprobe`などで確かめる。実際の再生も確認してから完成とし、出力パスと編集元を渡す。台本だけの依頼では台本まで、見た目だけの変更では直接影響する表示を検証する。
