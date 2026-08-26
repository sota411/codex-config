# HTML教材は、図・解説・根拠・クイズを一画面にまとめる

この参照は、調査後に成果物を組み立てるときだけ読む。読者はHTMLを上から読み進めても、目次から必要な区画へ移動してもよい。CLIへ本文を重複させない。

## 一つのHTMLで学習を完結させる

完成物は、次の四区画をこの順に持つ自己完結型HTMLとする。

1. **全体像**: repositoryの構造や処理を示す図、または単純な変更を比べる表
2. **流れ**: 入力から結果までの責任の受け渡しを3〜5段階で説明する
3. **根拠**: 確認済みの事実、推論、未検証事項を分け、`file:line`を示す
4. **クイズ**: 一問ずつ表示し、回答した場所で根拠を返す

`assets/learning-page-template.html`を出発点にする。見た目と操作を毎回作り直さず、調査対象に応じて本文、図、根拠、問題だけを差し替える。残った`{{PLACEHOLDER}}`、使わない推論欄、使わない未検証欄は完成前に削除する。

## 全体像には、図か表のどちらか一つを置く

構造、依存、処理順、分岐が理解の中心なら図を選ぶ。target外の一時directoryで単体の図HTMLを作り、`diagram-design`の`self_check.py`とブラウザ表示を通してから、検証済みのSVGを教材へ埋め込む。教材全体にはクイズ用JavaScriptがあるため、`diagram-design`の`self_check.py`を完成教材へ直接実行しない。図単体で図の規約を検証し、完成教材は`validate_learning_html.py`で検証する。完成後のrun directoryには、提示する教材だけを残す。

一行の変更、単純な追加・削除、短いbefore/afterには表を使う。表には内容が分かる`caption`と、`scope`を付けた見出しcellを置く。表で足りる内容を図へ膨らませない。

図は`data-visual-kind="diagram"`、表は`data-visual-kind="table"`で識別する。一つの教材に両方を詰め込まない。

## 根拠はブラウザから追える形にする

現在のfileを根拠にする場合は、表示文字列を`/absolute/path/to/file:line`とし、file本体へ移動する`file:///absolute/path/to/file` linkを付ける。削除行は無効なfile linkを作らず、revision、path、diff hunkを文字で示す。

事実の項目には`data-evidence-kind="fact"`を付ける。codeから導いた推論には`inference`、実行していないruntime挙動には`unverified`を使う。区分は色だけで伝えず、「確認済み」「推論」「未検証」という文字も表示する。

## クイズは、説明と応用を一問ずつ進める

最初の問題では、主要な流れを自分の言葉で説明してもらう。textareaへ回答してから確認ボタンを押すと、模範文ではなく照合すべき観点を表示する。文字数による合否判定はしない。

次の問題では、条件を一つ変えた場合の影響を選んでもらう。正答と誤答は、実装で確認した境界から作る。もっともらしさだけで架空のcomponentやbehaviorを選択肢へ加えない。必要な場合だけ三問目を追加する。

操作には次の制約を設ける。

- 回答確認と次の問題への移動を分け、自動で進めない。
- feedbackは押したボタンの近くへ置き、`role="status"`と`aria-live="polite"`を付ける。
- 正誤は記号と文章でも示し、色だけに依存しない。
- keyboardだけで回答、確認、移動、やり直しができるようにする。
- 回答を送信または保存しない。`fetch`、WebSocket、`localStorage`、`sessionStorage`を使わない。
- XP、点数、badge、時間制限を設けない。読者が戻って根拠を読み直せる状態を保つ。

## 生成から提示まで

1. target repository外に、既存fileと重ならないrun directoryを作る。
2. templateを`overview.html`または`diff.html`として複製し、調査結果で置き換える。
3. 図を選んだ場合は、図単体を`diagram-design`の手順で検証してからSVGを埋め込む。
4. `rg -n '\{\{[^}]+\}\}' <artifact>`でplaceholderが残っていないことを確かめる。
5. `python3 scripts/validate_learning_html.py <artifact>`をskill directoryから実行し、静的検査とsystem Chromiumによるquiz smokeを通す。template自体の構造確認だけは`--template`を付ける。
6. browserでdesktop幅とmobile幅を表示する。本文の欠け、横方向のはみ出し、200%拡大、focus表示、二問の回答確認とやり直しを確かめる。
7. 作業前後のGit状態が一致することを確認する。

検証が失敗した場合は、CLIの解説へ切り替えない。未完成のartifactを提示せず、失敗した検証と未作成であることを示す。

## CLIには入口だけを返す

完成後の応答は、artifactへのlink、固定した対象、検証結果、重要な未検証事項だけに絞る。図、解説、根拠一覧、問題文、模範解答をCLIへ再掲しない。読者が開くべき場所を一つに保つ。
