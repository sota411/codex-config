# Diff mode

diffだけを要約せず、指定範囲を固定し、周辺実装とtestを読んで観測可能なbehaviorの変化を説明する。

## 範囲を解決する

解決したbase、target、working tree区分を最初に記録する。存在しないreferenceを似た名前へ置き換えない。

- 「現在の差分」「未commitの差分」は`HEAD`から現在のworking treeまでとする。tracked fileはstagedとunstagedを区別し、untracked fileは`git ls-files --others --exclude-standard`で別に列挙する。
- 「staged」「index」は`git diff --cached`を使う。
- 明示された`A..B`または`A...B`は、両endpointを`git rev-parse --verify`してから、指定どおりのsemanticsで使う。
- 「mainとの差分」は`main...HEAD`を使う。local `main`が存在しない場合に`origin/main`へ黙示的に置き換えず、候補を示して確認する。
- commit IDまたは二つのbranchが明示された場合は、その指定をbaseとtargetとして固定する。
- `HEAD`が存在しないrepositoryでは、`HEAD`を必要とするmodeを停止し、unborn branchであることを示す。

## 変更を調査する

1. `GIT_OPTIONAL_LOCKS=0 git status --short`、`git diff --stat`、`git diff --name-status --find-renames`に相当する情報で規模と変更種別を把握する。
2. stagedとunstagedを含む場合は、それぞれのdiffを分けて読む。untracked fileは内容が必要なものだけを対象にする。
3. rename、delete、binary、submodule、generated fileを区別する。binaryやgenerated contentを読めたふりをしない。
4. 変更hunkの前後にあるfunction、type、route、schema、configurationを読む。diff内の行だけでcontrol flowを推定しない。
5. 関連するintegrationまたはacceptance testを探し、変更後に外部から観測できる結果を確認する。
6. commit messageやcommentに書かれた目的は「記載された意図」とし、実装から確認できる結果と分ける。
7. 説明に必要な場合だけ既存testを実行し、command、結果、未実行の環境を示す。

## 変化を整理する

次の順でまとめる。

1. 以前の公開behavior
2. 現在の公開behavior
3. その変化を生むcontrol flowまたはdata flow
4. 変更を固定するtestまたは未検証事項

これはcode reviewではない。severity、修正提案、網羅的なrisk一覧は、理解に必要な場合またはユーザーが明示した場合だけ扱う。

## 可視化する

- actor間の呼出順が変わるならsequenceを使う。
- 分岐、validation、fallbackが変わるならflowchartを使う。
- component間の依存または責任が移るならarchitectureかdependency graphを使う。
- 単純な追加、削除、rename、設定値変更、短いbefore/afterは表を使う。
- 変更file一覧そのものをnodeへ変換しない。図はbehaviorの変化を示す。

## 根拠と問題を作る

- 現在存在する行は絶対pathの`file:line`へlinkする。
- 削除行は`<revision>:<path>`とdiff hunk headerを示す。存在しないcurrent lineへlinkしない。
- 説明の先頭にbase、target、両方のcommit ID、working tree区分を示す。
- 最初の問題では、変更前後で利用者に見える差を説明してもらう。
- 応用問題では、条件を一つ変えた場合に通るbranch、影響するtest、または調べるべき境界を答えてもらう。
