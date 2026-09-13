---
name: review
description: ローカルレビューの依頼・リポジトリ規約、認証認可・破壊的なデータ変更・秘密情報・本番操作・公開API破壊・セキュリティ境界の変更に使う。通常の実装や文書変更では自動起動しない。PRコメント対応はgh-review-autofixを使う。
---

# Review

Review local changes using evidence and the requested scope. For GitHub PR review comments, use `gh-review-autofix`.

## Workflow

1. Honor explicit files or ranges; otherwise prefer `git diff --cached`, then `git diff`. If neither a diff nor an explicit target exists, ask for the target.
2. Check instructions applying to the touched files. Read surrounding code and other documentation only as needed to establish requirements, supported environments, and reachable impact.
3. Use [review-policy.md](references/review-policy.md) as the source of truth for evidence, proportionality, severity, adjudication, independent review, and completion. Do not turn preference or missing context into a finding.
4. When delegation is available and allowed, run one `reviewer_deep` as Reviewer using the policy's bounded procedure. Use a separate Critic only for a disputed important finding. Only the main agent edits artifacts and adjudicates findings.
5. Report all qualifying findings, deduplicated by root cause, in Japanese. Put uncertainty in `前提・未確認事項`. If none qualify, say so and disclose relevant verification gaps.
6. For review-only requests, report without editing. For implementation, fix accepted blockers and verify affected paths according to the policy; do not automatically fix every recommendation or repeat broad reviews.

## Output

Order findings as `[must]`, `[recommend]`, `[nits]`, using the definitions in the policy. Each finding must identify its trigger, evidence, demonstrated impact, and a concrete fix direction.

```text
[must] path/to/file.ext:123
問題: どの条件で何が壊れるか
根拠: 適用規約、到達可能な実装、テスト、差分、一次情報
影響: 現在の成果物で確認できる影響
修正案: 要件に合う最小の修正方針
```

Add `前提・未確認事項`, `反証を試みたが壊せなかった点`, or a brief summary only when useful. Do not hide failing checks or propose skipping/deleting them to pass. If rules conflict, cite both sources and explain which applies.
