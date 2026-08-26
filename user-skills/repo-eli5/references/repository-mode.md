# Repository mode

repository全体を一度にfile一覧へ変換せず、読者が最初に理解すべき一つの公開flowを根拠付きで追う。

## 調査する

1. repository rootと現在位置に適用される`AGENTS.md`を確認する。subdirectoryを調査するときは、その範囲に追加規約がないかも確認する。
2. `GIT_OPTIONAL_LOCKS=0 git status --short --branch`、`git rev-parse HEAD`、top-levelのfileとdirectoryを確認する。unborn branchでは、`HEAD`がないことを明示する。
3. `rg --files`で候補を絞り、採用済みframeworkと既存のextension pointをmanifestとlockfileから確認する。
4. READMEと主要documentからrepositoryの目的候補を得る。ただし、実装と食い違う場合は実装を優先し、食い違いを示す。
5. 次のうち存在するものを調べる。
   - executable、application、libraryのentrypoint
   - HTTP、CLI、UI、event、jobなどの公開境界
   - configurationとdependency injection
   - schema、database、file、cacheなどのstate境界
   - integrationまたはacceptance test
6. 公開入力から結果まで、一つの代表flowをsymbol単位で追う。各hopについてresponsibilityと次へ渡すdataを確認する。
7. 実装から判断できないruntimeの事実だけ、対象リポジトリへ書き込まない既存のcheck commandで確かめる。buildやtestが不要なら実行しない。

## 焦点を選ぶ

ユーザーが機能やmoduleを指定した場合は、それを優先する。指定がない場合は次の順で一つを選ぶ。

1. primary executableまたはserviceの通常利用flow
2. libraryの主要なpublic API
3. document、configuration、generator repositoryの主要な変換flow

複数applicationを持つmonorepoでは、全体の位置関係を短く示した後、primary applicationを一つだけ詳しく扱う。primaryを実装から一意に決められない場合は選択を求める。

## 可視化する

- componentと接続が中心ならarchitectureを使う。
- dependencyの向き、fan-in、cycleが中心ならdependency graphを使う。
- actor間の時間順が中心ならsequenceを使う。
- 分岐と判断条件が中心ならflowchartを使う。
- nodeはfile名ではなく役割を表し、必要な場合だけtechnical sublabelに代表pathまたはsymbolを置く。
- 最大9 nodeへ収まらなければ、overviewからdetailを削る。二枚目を自動生成しない。

## HTML教材の本文と問題を作る

- 最初の一文は、誰のどの入力が、どの結果へ変換されるrepositoryかを述べ、`data-repo-summary`へ置く。
- 主要flowの各点には、可能な限りentrypoint、境界、state、testの`file:line`を対応させ、HTMLの根拠区画から追えるようにする。
- directory構造の読み上げではなく、responsibilityとdata flowを説明する。
- 最初のreflection問題では、入力から結果までを2〜4段階で説明してもらい、回答後に照合観点を表示する。
- application問題では、入力条件または一つのcomponentを変えたとき、影響する境界や調べるべきfileを選んでもらう。
- 問題、feedback、回答後の根拠はHTML内へ置く。CLIには再掲しない。
