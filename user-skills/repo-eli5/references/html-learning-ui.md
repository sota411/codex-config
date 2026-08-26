# HTML教材は、説明、図、根拠、4択を一つの流れにする

この参照は、調査後に成果物を組み立てるときだけ読む。CLIへ本文を重複させず、読者が開く教材を一つに保つ。

## 最初の画面で、このrepositoryが何をするか答える

`assets/learning-page-template.html`から、`data-repo-eli5-page="v2"`の自己完結型HTMLを作る。headerの`h1`にはrepository名だけでなく、誰のどの入力を何へ変えるものかを書く。repository名、root、branchまたはdiff範囲、revisionは、同じheader内の折りたたみ可能な調査情報へ置く。repository modeのrevisionには、treeやtagではなく、調査したcommit objectのSHAを置く。

本文は次の順にする。

1. **導入**: repositoryまたは差分を一文で説明する。
2. **三つの仕組み**: repository modeでは、説明と小さな図を組にした三章を置く。
3. **未検証事項**: 実行しなかったruntime確認を、事実と混ぜずに示す。
4. **4択クイズ**: repository modeでは、三章に対応する三問を一問ずつ表示する。

## 一章の順序を「説明、図、読み方、根拠」に固定する

各`article[data-teaching-unit]`には、次の要素を一つずつこの順に置く。

1. 結論を含む`h2`
2. `data-concept-intro`: 何があり、なぜ必要かを平易な言葉で説明する本文
3. `data-visual-kind="diagram"`: 直前の説明だけを示す小さな図
4. `data-diagram-reading`: 図をどこから読み、何が分かるかを述べる一文
5. `details[data-evidence-group]`: その章を支えるコード上の根拠

図より前の説明は五文以内とする。説明していない略語、クラス名、ファイル名を図の主ラベルへ置かない。図の`figcaption`には、図が示す範囲と省略したdetailを書く。

図は対象repository外の一時directoryで単体HTMLとして作る。各図を`diagram-design`の`self_check.py`とbrowser表示へ通してから、検証済みSVGを教材へ埋め込む。教材全体はクイズ用JavaScriptを含むため、`self_check.py`ではなく`validate_learning_html.py`で検証する。

## 単純な差分は表を使う

一行の変更、単純な追加・削除・rename、短いbefore/afterには、一つの`table[data-visual-kind="table"]`を使う。表には内容が分かる`caption`と`scope`を付けた見出しcellを置く。

複雑なdiffは、外から見える変化ごとに1〜3章へ分ける。一つの教材へtableとdiagramを混在させない。

## 根拠は、説明した仕組みのすぐ後ろへ置く

各章の`details`には、内容が分かる空でない`summary`と、最低一つの確認済み事実を置く。各`data-evidence-kind="fact"`の内側には、空でない`data-evidence-description`と、その主張を直接確認できる実処理またはassertionの`file:line`を対応させる。現在のfileは、表示文字列を`/absolute/path/to/file:line`とし、同じfact内でfile本体へ移動する`file:///absolute/path/to/file` linkを付ける。削除行は無効なfile linkを作らず、revision、path、diff hunkを文字で示す。

事実には`data-evidence-kind="fact"`、codeから導いた推論には`inference`、実行していないruntime挙動には`unverified`を使う。区分は色だけで伝えず、「確認済み」「推論」「未検証」という文字も表示する。

## クイズは四択で、その場に理由を返す

repository modeは三問、diff modeは二〜三問とする。全問を`data-question-kind="choice"`とし、空でない問題文を`legend`へ置く。同じ`name`を持つradioを四つ置き、各radioのlabelには空でない選択肢本文を置く。`data-correct`は実在する一つの`value`を参照する。

問題は、その章で説明した目的、流れ、条件を理解したかを確かめる。誤答へ架空のcomponentやbehaviorを加えない。選択肢は否定文を避け、選んだ内容をそのまま読める肯定文にする。

回答確認後は、選択肢を固定し、正誤と理由をボタンの近くへ表示する。正解・不正解のどちらでも「次の問題へ」を表示する。自動で次へ進めず、正解まで選び直すことも求めない。

- feedbackには`role="status"`、`aria-live="polite"`、`aria-atomic="true"`を付ける。
- 正誤は記号と文章でも示し、色だけに依存しない。
- keyboardだけで選択、回答確認、次の問題、やり直しを操作できるようにする。
- 回答を送信または保存しない。`fetch`、WebSocket、cookie、IndexedDB、Cache Storage、`localStorage`、`sessionStorage`を使わない。
- XP、点数、badge、時間制限を設けない。

HTMLは自己完結させる。外部script、stylesheet、画像、字幕track、inline styleの外部URL、meta refreshを使わない。CSS escapeは外部URL検査を曖昧にするため使わない。

`html`と`body`へ`min-width`を指定せず、本文全体を狭い画面でも折り返す。390px幅の画面を200%拡大した条件は195 CSS pxとして確認する。横スクロールが必要な図は、図の枠内だけへ閉じ込める。

## 生成から提示まで

1. target repository外に、既存fileと重ならないrun directoryを作る。
2. templateを`overview.html`または`diff.html`として複製し、調査結果で置き換える。
3. 図ごとに単体HTMLを作り、`diagram-design`の検証済みSVGだけを教材へ埋め込む。
4. `rg -n '\{\{[^}]+\}\}' <artifact>`でplaceholderが残っていないことを確かめる。
5. `python3 scripts/validate_learning_html.py <artifact>`をskill directoryから実行し、静的検査とsystem Chromiumによるquiz smokeを通す。templateの構造確認だけは`--template`を付ける。
6. browserでdesktop幅、mobile幅、200%拡大、focus表示、全問の正答・誤答・やり直しを確認する。
7. 作業前後の対象repositoryのGit状態が一致することを確認する。

検証が失敗した場合は、CLIの解説へ切り替えない。未完成のartifactを提示せず、失敗した検証と未作成であることを示す。

## CLIには入口だけを返す

完成後の応答は、artifactへのlink、固定した対象、検証結果、重要な未検証事項だけに絞る。図、解説、根拠一覧、問題文、模範解答をCLIへ再掲しない。
