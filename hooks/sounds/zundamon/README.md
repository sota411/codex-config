# ずんだもんの通知音声

音声クレジット: **VOICEVOX:ずんだもん**

| ファイル | セリフ | タイミング |
| --- | --- | --- |
| complete.wav | 完了したのだ。 | メインの応答終了（途中報告を含む） |
| question.wav | 追加の質問があるのだ。 | request_user_input の質問画面を開く直前 |

声はノーマル、話速は1.15倍です。子エージェントと手動中断は無音です。返信本文の質問判定は行いません。再生時は `paplay` だけを使い、VOICEVOXは起動しません。

## 再生成

`template.json` のセリフや `speed_scale` を編集してから実行します。生成スクリプトはエンジンのバージョンと話者を確認し、異なる場合はエラーにします。

```bash
docker run --rm -d --network host --name codex-notification-voicevox \
  voicevox/voicevox_engine@sha256:eb8c7f46a7d01217d1ff2b6f018261faedeceded3cc756b4fbbf371791ad6c90 \
  gosu user /opt/voicevox_engine/run --host 127.0.0.1 --port 50021
```

この端末ではDockerのbridge作成が失敗するため、hostネットワークでループバックだけに待ち受けます。`curl --fail http://127.0.0.1:50021/version` で起動を確認してから生成し、終わったら生成用コンテナを停止します。

```bash
python3 "$HOME/.codex/hooks/codex_notification_sound.py" --generate
docker stop codex-notification-voicevox
paplay "$HOME/.codex/hooks/sounds/zundamon/complete.wav"
paplay "$HOME/.codex/hooks/sounds/zundamon/question.wav"
```

別のポートを使う場合は `--engine-url http://127.0.0.1:ポート番号` を指定できます。

## 出典

- [VOICEVOX ENGINE 0.25.2](https://github.com/VOICEVOX/voicevox_engine/tree/0.25.2)
- [VOICEVOX 利用規約](https://voicevox.hiroshiba.jp/term/)
- [ずんだもんの音声利用規約](https://zunko.jp/con_ongen_kiyaku.html)
