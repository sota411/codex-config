# テンプレートの注意点

対象は上流revision `a88a952d3934180b74d5bdc8f567a256ae63ad20`。既存プロジェクトや別revisionでは該当コードを確認し、修正済みなら繰り返さない。修正は動画プロジェクト内で、依頼に必要な経路へ限定する。

## 音声生成とタイミング

初回の音声生成前に、次の制約を確認する。

- **音声の読み取り**：`scripts/generate-voices.ts`は生成済みTSを正規表現で読み、`id`、`character`、`text`の順序に依存する。二重引用符やエスケープを含むセリフも正しく読めない。台本の表現を制限して回避せず、必要な場合は既存依存の`yaml`で`config/script.yaml`を読み、話者は`config/characters.yaml`から取得する。入力の件数・ID・話者を検証し、不正な入力や生成失敗では処理を失敗させる。
- **フレーム数**：同スクリプトは現在`ceil(WAV秒数 × 30 × 1.2)`を保存するが、`src/Main.tsx`は配置時にも再生速度で割り、音声も倍速再生する。その結果、音声終了後にも口パクが残る。音声生成時には生音声の`ceil(WAV秒数 × fps)`を保存し、配置時にだけ再生速度で割るよう、該当コードを修正する。fpsと速度は`src/config.ts`の設定に合わせる。
- **動画全体の長さ**：`src/Root.tsx`は速度調整前のフレーム数を合計し、さらに120フレームを加える。一方、`src/Main.tsx`のセリフは0フレームから始まる。Compositionの長さを実際の配置計算と一致させ、冒頭・末尾の余白は依頼に合わせて明示的に扱う。
- **生成結果**：`durations.json`はWAVファイル名をキー、フレーム数を値とするオブジェクト。古いWAVの残存を今回の成功と取り違えず、生成ログ・台本・出力を照合する。欠落した計測値を同期処理の既定値で埋めた状態は完成ではない。

タイミングを修正した場合は、長さが分かる音声を使った短い掛け合いで、実測音声長、表示区間、MP4全体の長さが一致することを確認する。文字数からの見積もりだけで検証しない。

根拠：上流の`scripts/generate-voices.ts`、`scripts/sync-script.ts`、`src/Main.tsx`、`src/Root.tsx`。

## BGM・シーン・話者・設定

- `scripts/sync-script.ts`は毎回`bgmConfig = null`と固定の3シーンを生成する。BGMやシーンを変更する依頼では、編集可能な設定元と生成処理を接続する。`src/data/script.ts`だけを書き換えない。
- `config/characters.yaml`へ話者を追加するだけでは、音声生成のハードコードされた話者一覧や`src/Main.tsx`のキャラクター表示は増えない。話者を増やす場合に限り、生成・表示の両方を合わせる。
- `video-settings.yaml`にある動画設定がすべて再生へ反映されるわけではない。解像度・fps・速度は`src/config.ts`、VOICEVOXの接続先は生成スクリプト内の参照も確認する。
- 画像は`public/images`を起点にスキャンされ、描画時にはRemotionの`staticFile()`を使う。OSの絶対パスをそのまま画像URLとして渡さない。
- `npm run init`は旧TS、WAV、出力MP4を対象とし、`config/script.yaml`をリセットしない。新規台本はYAMLで作る。

## GUIエディターを使う場合

ユーザーがGUI編集を求めた場合や、既にGUIを使用しているプロジェクトで利用する。

```bash
npm run editor:install
npm run editor
```

標準のUIは`http://localhost:3001`、APIは`http://localhost:3002`。実際の待受先は起動ログで確認する。

| 用途 | API |
|---|---|
| キャラクター・表情・表示種別の確認 | `GET /api/metadata/all` |
| 台本の取得 | `GET /api/script` |
| セリフの更新 | `PUT /api/script/:id` |
| スタイルの取得・更新 | `GET /api/settings`、`PUT /api/settings` |

台本APIの更新はYAML保存までで、TSの同期を行わない。音声生成前に`npm run sync`が必要。`POST /api/actions/build-video`の成功応答は書き出しの開始を示すため、完了判定には使わない。Codexからは完了まで追跡できる`npm run build`を優先する。

根拠：上流の`editor/server/services/scriptService.ts`、`editor/server/routes/actions.ts`、`editor/vite.config.ts`。
