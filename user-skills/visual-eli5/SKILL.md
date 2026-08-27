---
name: visual-eli5
description: 任意の話題を、知識ゼロの読者向けに大きな図と少ない言葉で説明する自己完結HTMLへまとめる。`$visual-eli5`と明示されたときだけ使う。
---

# Visual ELI5

一つの自己完結HTMLで、話題の核心を大きく見せる。説明本文を会話へ分散させない。

## 原文と優先順位

1. [Anthropic community版eli5原文](references/eli5-original.md)を最初から最後まで読む。対象読者、言葉の量、大きな絵、HTML artifactという契約は、この原文をそのまま適用する。
2. [HumanLayer版show-me原文](references/show-me-original.md)を最初から最後まで読む。現在の話題に合う最小の視覚表現を選ぶために使う。
3. このwrapperは、二つの原文をCodexで一つの成果物へ統合する方法だけを定める。show-meにあるMarkdown、Mermaid、単体code blockの例も、最終的には同じHTML内へ描画する。

`$ARGUMENTS`には、`$visual-eli5`の後ろに書かれた話題を対応させる。話題が省略されても現在の会話から一意に決まる場合は、その話題を使う。一意に決まらない場合は、HTMLを作る前に説明対象を一つだけ質問する。

## 事実を理解する

- 提示された文章、URL、file、code、errorがあれば、必要な範囲を先に確認する。表面上の語句だけで説明を作らない。
- 確認済みの事実と推論を区別し、簡単にするために誤った因果関係や架空のdataを作らない。
- 出典、重要な条件、未検証事項が必要な場合は、主図を邪魔しない`details`へ分ける。
- 成果物の言語はユーザーの依頼言語へ合わせる。

## 最小の視覚表現を選ぶ

最初に一つの核心を決め、その核心を最短で伝える表現を一つ選ぶ。

| 話題の形 | 表現 |
|---|---|
| 単一の概念や日常の比喩 | 大きな一枚絵またはラベル付き模式図 |
| 比較や短いbefore/after | 横並び比較またはsemantic table |
| logicやalgorithm | pseudocodeまたは小さなflow |
| code、component、file責務 | 注釈付きcode、component tree、file tree |
| 既存形状の変更 | 対象に合うdiff |
| 処理順、状態、相互作用、依存関係 | flowchart、sequence、state、architectureなどの正式な図 |
| 数量、分布、傾向 | 確認済みdataだけを使うchart |

- 通常は主図を一つにする。異なる軸を一図へ詰めると核心を誤って伝える場合だけ、二つ目を加える。
- 三列の表で同じことが伝わる場合は、箱と矢印の図を作らない。
- Mermaid runtimeは埋め込まない。Mermaidが適切な話題は、検証可能な静的SVGへ描き直す。
- decoration、一般的なdashboard card、理解に寄与しないicon、架空の数値を加えない。

## 正式な図を作る

処理フロー、状態、相互作用、依存関係など、文章や表より図が明確な場合は、利用可能なskill catalogから`diagram-design`を読み、そのworkflowを使う。

- `$visual-eli5`の明示呼び出しは、図種、size、contentの自動選定とneutral default profileの使用を許可したものとして扱う。図種確認やstyle onboardingでは停止せず、target projectのstyle guideを変更しない。
- このwrapperでは、`diagram-design`の描画前planを会話へ提示せず、redirect待ちでもpauseしない。説明対象が一意なら、そのまま描画と検証まで進める。
- `doc-inline`、`simplified`、`mixed`、静的表示を既定にし、意味に合うtype referenceを読んでから描く。
- 単体diagramを一時directoryへ作り、installed `diagram-design/scripts/self_check.py`を通す。
- 検証済みSVGだけを最終HTMLへ埋め込む。SVGには`role="img"`、固有IDを持つ`title`と`desc`を含める。
- connectorを文字、label、非端点node、注記、装飾図形と重ねない。接続元・接続先nodeへのarrowhead接触は許容するが、node内の文字や意味領域を覆わない。
- `self_check.py`の成功だけで重なりなしと判定しない。描画後のSVGでconnectorのstroke領域と文字・labelの境界を確認し、交差した場合は再配置する。label背景がconnectorを隠す配置も重なりとして扱う。
- connector labelはopaque maskを持たせ、maskの最近接端からconnector strokeの最近接端までを6–10px空ける。横線では上下、縦線では左右へ置き、10pxを超えて離さない。SVG user座標と各表示幅のrendered CSS座標で確認する。
- 主図のSVGには内容全体を含む`viewBox`を持たせ、containerとSVGを可変幅にする。固定`min-width`、切り抜き、本文全体の横scrollで横長の図を押し込まない。
- 390px幅でlabelが読めない場合は、同じ意味と順序を保ったmobile用の縦配置へ切り替える。desktop図を縮小するだけで済ませない。

## 一つのHTMLへまとめる

成果物は`~/.codex/artifacts/visual-eli5/<timestamp>-<safe-topic-slug>/index.html`へ保存する。run directoryは毎回新しく作り、既存fileを上書きしない。

- `DOCTYPE`、依頼言語の`lang`、viewport、一つの`main`、一つの`h1`を持たせる。
- CSSとSVGをinlineにし、外部stylesheet、font、script、image、iframeを読み込まない。
- JavaScriptとanimationは既定で使わない。静的な状態だけで意味が完結するようにする。
- 主図を最も大きくし、言葉は図の意味を決めるtitle、短い説明、必要なlabelだけに絞る。
- subjectに合うpalette、type scale、layoutを選び、色とfontの役割を増やしすぎない。
- mobileでは一画面の役割を絞り、390px幅と200%文字拡大でも欠け、重なり、本文全体の横scrollを起こさない。
- responsiveな積み替えでも、矢印の向き、処理順、接続元と接続先、labelとの対応を変えない。横向きの接続を縦向きへ変える場合は、すべての矢印を一律に回転させず、各接続の意味に合わせて向きを割り当てる。
- desktop用とmobile用の表現をCSSで切り替える場合は、selector specificityを含むcomputed styleを各breakpointで確認し、両方を同時表示しない。
- URL、file path、識別子などの長い連続文字列は`overflow-wrap: anywhere`などで折り返し、閉じた`details`だけを見て合格にしない。
- 読み上げ可能な名前、十分なcontrast、色以外の手掛かり、見えるfocusを用意する。
- quiz、score、badge、進捗保存、browser storage、外部送信を加えない。

## 開いて確認する

利用可能な場合は`browser:control-in-app-browser`を読み、完成HTMLをin-app Browserで開く。

1. desktop幅で、核心、主図、読む順序が一目で分かることを確認する。
2. 390px幅と200%文字拡大で、欠け、重なり、本文全体の横scrollがないことを確認する。
3. responsiveな表示variantがある場合は、各幅のcomputed styleで意図したvariantだけが表示されることを確認する。
4. すべての`details`を開き、長いURL、table、codeを含む状態でも`documentElement.scrollWidth`が`clientWidth`を超えないことを確認する。
5. 図のlabel、table、code、source detailsを実際に読み、原文の「big pictures and few words」を満たすまで不要な要素を削る。

Browserを利用できない場合はartifactを作成した事実と、視覚確認を実施できなかった事実を分けて示す。確認していない表示を合格と報告しない。

## 返答

完成後の会話には、HTMLへのlink、選んだ視覚表現、実施した検証、理解に影響する未検証事項だけを短く返す。HTML作成に失敗した場合は、会話内の長文説明へ黙示的に切り替えず、失敗した段階を示す。
