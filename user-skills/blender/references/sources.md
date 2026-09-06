# 調査出典と確認範囲

調査日: 2026-09-06。公式仕様を判断の根拠とし、X の投稿と公開スキルは実践例として参照した。本文は各資料を要約している。投稿された画像・動画の見た目や、記載された制作時間は独立に検証していない。

## 公式の Geometry Nodes 仕様

<a id="official-geometry"></a>

Blender Manual の HTML を直接取得できない場合があったため、以下は公式の `blender-v5.2-release` ブランチにある文書原文も取得して確認した。

| 資料 | 確認した仕様 |
| --- | --- |
| [Geometry Nodes Modifier](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/modeling/modifiers/geometry_nodes.rst) | 共有グループでも各 Modifier に別の公開入力値を設定できる |
| [Realize Instances](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/modeling/geometry_nodes/instances/realize_instances.rst) | 実体化で個別の形状を加工できる一方、大量の複製では負荷が増え得る |
| [Random Value](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/modeling/geometry_nodes/utilities/random_value.rst) | ID は `id` 属性、なければ Index を使用。Seed は同じ ID に対する乱数を変える |
| [Distribute Points on Faces](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/modeling/geometry_nodes/point/distribute_points_on_faces.rst) | 密度変更や変形後も、残った点の ID は維持される |

## Python・CLI は実行版に合わせる

<a id="python-cli"></a>

- [Using Operators — 5.2 文書原文](https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/doc/python_api/rst/info_gotchas_operators.rst): Context への依存と、Operator の返値が実行状態であることを確認した。
- [CLI 引数 — 5.2 Manual](https://docs.blender.org/manual/fr/5.2/advanced/command_line/arguments.html): 引数の実行順と `--python-exit-code` の対象を公式ページの検索取得本文で確認した。
- [4.0 Python API](https://developer.blender.org/docs/release_notes/4.0/python_api/): Node Group の Interface API と Principled BSDF の変更。過去コードを点検するための資料であり、全変更の一覧をこのスキルに転記していない。
- [5.0 Python API](https://developer.blender.org/docs/release_notes/5.0/python_api/): Action Slot と Channelbag に対応する API の確認先。
- [5.2 Python API 原文](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.2/python_api.md): Modifier の入力が RNA に移行し、Compare と Random Value のソケット識別子も変更された。文書原文を取得し、Modifier 入力の設定・読戻しは 5.2.1 でも確認した。
- [Scene.frame_set](https://docs.blender.org/api/5.2/bpy.types.Scene.html#bpy.types.Scene.frame_set): フレームを移動し、シーンの状態を更新する API。

## 描画と視覚的な反復

<a id="rendering"></a>

| 資料 | 採用した知見 |
| --- | --- |
| [Viewport Shading — 5.2 原文](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/editors/3dview/display/shading.rst) | Material Preview とシーンの照明・World は一致するとは限らない |
| [Color Spaces — 5.2 原文](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/render/color_management/color_spaces.rst) | Normal 等は Non-Color。色管理と出力形式を用途に合わせる |
| [Rendering Animations — 5.2 原文](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/render/output/animation.rst) | 代表フレームによる時間見積もりと、連番による長時間描画・再開 |
| [BlenderAlchemy](https://arxiv.org/abs/2404.17672) — Ian Huang、Guandao Yang、Leonidas Guibas、2024-04-26 公開、2024-08-02 改訂 | 画像を参照する編集と視覚評価の反復。研究内の結果であり、現在の Codex の性能保証には使わない |

## 既存データを再利用する

<a id="reuse"></a>

- [Link & Append — 5.2 原文](https://projects.blender.org/blender/blender-manual/raw/branch/blender-v5.2-release/manual/files/linked_libraries/link_append.rst): Link は元データへの参照を保ち、Append は独立したコピーを作る。既にリンク済みのデータの扱いなど、詳細は原文を確認する。
- [Easily use complex geometry nodes in Blender python scripts](https://matthewhilton.dev/blog/easy-geo-nodes/) — Matthew Hilton、2026-02-25: 複雑なノードグループを `.blend` から取り込む制作例。

## X で見つかった実践例

<a id="x-observations"></a>

投稿本文を `bird search` と `bird read` で確認した。時刻は UTC。次の検索語を使い、紹介記事だけでなく投稿者自身の体験があるものを抽出した。

```text
blender codex -filter:retweets -from:fujikawa
"geometry nodes" (codex OR claude OR agent) -filter:retweets -from:fujikawa
Blender (Codex OR AI) (ノード OR プロシージャル) -filter:retweets -from:fujikawa
```

| 投稿者・日時 | 投稿から得た示唆と採用範囲 |
| --- | --- |
| [にゃんねこ / nyanneco9](https://x.com/nyanneco9/status/2096285945549279578)、2026-09-05 17:14:51 | Geometry Nodes で後から扱いやすい成果物にするという提案。すべてのモデリングへの必須条件にはしない |
| [アキナリ / akinari_net](https://x.com/akinari_net/status/2096103759780938006)、2026-09-05 05:10:54 | 自分で作った `.blend` を参考に渡し、パラメトリックな制作を指示した例 |
| [アキナリ / akinari_net](https://x.com/akinari_net/status/2096075006409375768)、2026-09-05 03:16:39 | 瓦の格子を保ち、形状候補を切り替える提案。ばらつきは参考物の性質に合わせる |
| [射当ユウキ / grdr42](https://x.com/grdr42/status/2094572579898216626)、2026-08-31 23:46:32 | Codex の生成グラフが複雑になりすぎたという報告。ノードの整理を確認項目に加える |
| [Bobby Georgiev / GeorgievBoyan](https://x.com/GeorgievBoyan/status/2094438501857022327)、2026-08-31 14:53:46 | MCP 経由で正弦波の動きを持つ複製ツールを作ったという体験。一般的な成功率の根拠にはしない |

## 公開スキルと操作経路の採否

<a id="existing-skills"></a>

GitHub API で確認した各リポジトリは、調査時点で未アーカイブ、MIT License。最終 push 日は保守状況を調べる手掛かりとして記録しており、品質の保証ではない。

| 候補 | 最終 push 日 (UTC) | 採否と理由 |
| --- | --- | --- |
| [nodecue/blender-node-skills](https://github.com/nodecue/blender-node-skills) | 2026-07-31 | ノード・ソケットの実データ確認を参考にする。固定ノード数による分割や命名の一律制限は採用しない |
| [ifBars/blender-agent-studio](https://github.com/ifBars/blender-agent-studio) | 2026-08-18 | 形状から仕上げへの段階分け、プレビュー、保存後・書き出し後の確認を参考にする。全プラグインの導入や特定の造形スタイルは要求しない |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | 2026-09-05 | 操作経路の候補。標準 CLI で始められるため、このスキルの必須依存にしない |

参照した実装本文: [Geometry Nodes](https://github.com/nodecue/blender-node-skills/blob/main/skills/geometry-nodes/SKILL.md)、[Modeling](https://github.com/ifBars/blender-agent-studio/blob/main/plugins/blender-agent-studio/skills/blender-modeling-workflow/SKILL.md)、[Rendering](https://github.com/ifBars/blender-agent-studio/blob/main/plugins/blender-agent-studio/skills/blender-rendering-workflow/SKILL.md)。スキル本体や補助コードの転載・インストールは行っていない。

[公式 MCP Server](https://www.blender.org/lab/mcp-server/) の検索取得本文は、Blender 5.1 以降と別途導入する Add-on・Client・Server を案内していた。本文の直接取得と導入は未確認。第三者 README の「5.2 に同梱」という記載は採用していない。接続方法を新たに設定する際は公式の現行手順を確認する。

## このスキルの実機確認

調査環境は Arch Linux、Blender 5.2.1 LTS、build hash `9e2066aef7ef`。CLI から背景プロセスを起動し、Python API と主要な Geometry Nodes 型が利用できることを確認した。この確認だけでは、制作・描画結果や他の Blender の版での互換性は保証しない。

制作テストは一時ディレクトリで行い、生成用コードと検証用の assert を残した。以下は 2026-09-06 の確認結果。

| シナリオ | 確認した結果 |
| --- | --- |
| Geometry Nodes の柵を独立して制作 | 別の Codex にスキルと制作依頼を渡し、幅3 m・縦板8本・Seed 17 の柵を生成。保存後の別プロセスで幅4 m・11本への変更と復元、Seed の変更と復元を確認。再生成時の配置と色材質の並びも一致した |
| 柵の見た目と編集可能性 | Cycles、12 samples、640×400 の正面・背面画像で形状・色・接地を確認。背面で見つかった浮きを修正した。ノードの公開入力とインスタンスを保持し、外部画像への依存はない |
| 既存シーンの部分編集 | 共通の材質を使う2物体のうち、対象だけに材質変更・Bevel・キーフレームを追加。保存後の別プロセスで、他の物体の形状・変換・材質とカメラ・照明が保持されていることを比較した |
| 短いアニメーション | Cycles CPU、16 samples、320×240、24 FPS で24フレームを描画。連続画像の一覧で対象の回転と他物体の静止を確認。H.264 MP4 の1秒・24フレームを ffprobe で確認し、全フレームを ffmpeg でデコードした |

部分編集の確認は、未編集のファイルで Bevel 不在の assert が失敗し、編集・再読み込み後に通ることも確認した。描画テストでは、保存後に指定した画像が実際に生成されたことまで確かめた。汎用的な造形品質、他の Blender の版、MCP 接続、ゲームや Web での書き出し結果は未検証。

柵の制作では、旧式の Modifier 入力代入が失敗した。実行版の RNA と公式の5.2変更内容を照合し、`getattr(modifier.properties.inputs, identifier).value` で設定・読戻し・再代入・形状の再評価が通ることを確認して、手順へ反映した。GUI 上で入力欄を操作するテストは行っていない。
