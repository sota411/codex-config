# 2026-08-20 skill棚卸し

## 対象

Git管理している `user-skills/` と、個別に導入されていた `skills/` 直下のskillを対象にした。Codex同梱の `skills/.system/` と、plugin cache内のskillは各配布元が管理するため対象外とした。

## 判定方法

保存済みの全年度のセッションを対象に、配置移行前後のskillパスを含むツール呼び出しとassistantの使用宣言を照合した。名前が利用可能skill一覧へ掲載されただけの記録、導入時の棚卸し、skill作成本体の作業、今回の棚卸しとレビューによる参照は実使用に含めていない。

`unused/` には、実タスクで使った証跡が確認できなかったskillを保存する。`replaced/` には、役割を別のskillへ引き継いだ旧版を保存する。

## 置換

- `stop-ai-slop-jp`を`natural-japanese`へ置換した。
- `natural-japanese`の取得元は [`coji/natural-japanese`](https://github.com/coji/natural-japanese/tree/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/skills/natural-japanese) の `skills/natural-japanese/`、導入時のmainは `0f1cc1c5a4e2aa7590598c88a15c213a60d9545a` である。
- 配布条件を保持するため、同じcommitのリポジトリルートにあるMIT `LICENSE`も導入先へ同梱した。

## 未使用としてアーカイブ

- `agents-sdk`
- `cloudflare-email-service`
- `cloudflare-one-migrations`
- `hatch-pet`
- `sandbox-sdk`
- `turnstile-spin`

`skills/hatch-pet`には`user-skills/hatch-pet`と同一内容の重複があったため、有効ルート外のバックアップにも退避した。

## 復元

復元対象を一つ選び、`user-skills/`直下へ戻す。既に同名skillがある場合は上書きせず、内容を比較してから扱う。

```bash
git -C "$HOME/.codex" mv \
  "archived-user-skills/2026-08-20/<理由>/<skill名>" \
  "user-skills/<skill名>"
```
