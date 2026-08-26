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

## 三つの仕組みを選ぶ

ユーザーが機能やmoduleを指定した場合は、その機能を中心に三つの仕組みを選ぶ。指定がない場合は、primary flowから次の三つを選ぶ。

1. **何をするrepositoryか**: 誰のどの入力が、どの出力へ変わるか。
2. **中心で何が起きるか**: 入力が結果へ変わるまでの、最も重要な変換または受け渡し。
3. **結果を左右する規則**: state、queue、分岐、capacity、永続化など、動きを理解するために欠かせない仕組み。

三つ目に相当する仕組みが実装から確認できない場合は、似た概念を作らない。公開entrypoint、状態境界、testを調べ直し、それでも見つからなければ焦点を狭めるよう求める。

複数applicationを持つmonorepoでは、primary applicationを一つ選び、その入出力、中核処理、結果を左右する規則を扱う。primaryを実装から一意に決められない場合は選択を求める。

## 可視化する

- repository全体を一枚へ詰めず、三つの仕組みを一枚ずつに分ける。
- componentと接続が中心ならarchitectureを使う。
- dependencyの向き、fan-in、cycleが中心ならdependency graphを使う。
- actor間の時間順が中心ならsequenceを使う。
- stateと切り替わる条件が中心ならstate machineを使う。
- 分岐と判断条件が中心ならflowchartを使う。
- nodeはfile名やクラス名ではなく、読者が見て分かる入力、仕事、結果を表す。
- 一枚は3〜5 nodeを目安とする。説明していない略語を主ラベルに使わず、technical sublabelは必要な場合だけ置く。

## HTML教材の本文と問題を作る

- 最初の一文は、誰のどの入力が、どの結果へ変換されるrepositoryかを述べ、`data-repo-summary`へ置く。
- 各章は、仕組みを平易な言葉で説明してから図を置く。directory構造の読み上げはしない。
- 専門用語は、現象や機能を説明した後に「コードでは、これを〜と呼びます」と渡す。
- 各章の根拠には、entrypoint、境界、state、testのうち、その図を直接支える実処理またはassertionの`file:line`を対応させる。関数宣言やtest宣言だけの行で代用しない。
- 各章に対応する四択を一問ずつ作る。第一問は目的と出力、第二問は中核の変換、第三問はstateやqueueなどの規則を確認する。
- 誤答は実装で確認した境界から作り、架空のcomponentやbehaviorを使わない。
- 問題、feedback、回答後の根拠はHTML内へ置く。CLIには再掲しない。
