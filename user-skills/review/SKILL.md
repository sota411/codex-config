---
name: review
description: Review local changes with evidence-based triage and bounded follow-up verification. Use when the user asks for a local review, a repository explicitly requires it, or a change touches authentication or authorization, destructive data or schema changes, secrets, production operations, breaking public APIs, or security boundaries. Do not auto-invoke for ordinary implementation or documentation changes. For GitHub PR review comments, use `gh-review-autofix` instead.
---

# Review

Use this skill for local code review. Prefer changed lines and staged diffs over broad codebase review unless the user explicitly asks for a wider pass.

For GitHub PR review comments, do not use this skill as the primary workflow. Use `gh-review-autofix` to fetch review threads, judge comments, post replies, and implement accepted fixes.

## Workflow

1. Resolve the review scope first.
   Honor explicit files or ranges first; otherwise prefer `git diff --cached`, then `git diff`.
   If there is no diff and no explicit target, stop and ask what should be reviewed.
2. Read repository-specific rules before judging code.
   Search for `AGENTS.md`, `CLAUDE.md`, `CODING_GUIDELINE.md`, `PR_REVIEW_GUIDELINE.md`, `README.md`, and test-related docs that apply to the touched files.
3. Read only the minimal surrounding context needed to judge the changed code.
   Use `git diff --name-only`, `git diff --cached --name-only`, `rg`, `sed`, and `nl -ba` to keep the review evidence precise.
4. Apply the severity mapping and checklist from [references/review-policy.md](references/review-policy.md).
5. When subagents are available and allowed, run the bounded independent review below.
6. Revalidate the adversarial review's findings before finalizing them.
7. Report findings first.
   Order them as `[must]`, `[recommend]`, `[nits]`.
8. When no findings remain, say that explicitly and mention any residual verification gaps such as tests not run.

## Review Rules

- Base every finding on an applicable project rule, reachable current behavior, test or command output, a version-matched primary source, or measurement.
- General engineering principles, preferences, and untested possibilities may guide investigation but are not finding evidence.
- Prefer diff-focused review.
  Do not expand scope into unrelated files unless the change forces it.
- Be decisive.
  Do not write speculative review comments. Put the exact missing context in `前提・未確認事項` instead.
- Keep findings actionable.
  Every finding must include the file, line, problem, evidence, demonstrated impact, and a concrete fix direction.
- Respect existing patterns.
  When judging style or design, verify the local convention first.

## Bounded Independent Review

1. Freeze the review snapshot and start one `reviewer_deep` as Reviewer with `fork_turns="none"`.
   Give it the diff and base, requirements, non-goals, acceptance criteria, supported environments, applicable rules, necessary surrounding code, and reproduction commands. Include documented intentional tradeoffs as claims to verify, not proof of correctness. Do not suggest defects, fixes, or an expected verdict.
2. Reviewer returns actionable candidates with stable IDs, severity, `file:line`, trigger conditions, evidence, current impact, and a minimal fix direction. No finding quota; return no findings when none qualify.
3. The main agent adjudicates each candidate using the revalidation rules below. Reviewer agreement is not evidence and does not authorize edits.
4. Only for an important finding whose validity or applicability remains disputed, use one separate `reviewer_deep` as Critic with `fork_turns="none"`. Give it the disputed IDs, snapshot, requirements, and evidence from both sides. Ask for one finding-specific verdict: `成立`, `不成立`, or `未確認`, with evidence or the exact missing check. Do not commission another broad search for missed issues.
5. The main agent decides after that response; do not run a Reviewer-Critic dialogue until consensus. An incidentally discovered serious issue must still be reported with evidence, but does not automatically restart review.

Use the named profile for either role; do not silently substitute a default agent. If subagents are unavailable, apply the same evidence gate locally and state that independent review was not run. Only the main agent edits artifacts. A changed snapshot invalidates conclusions for affected paths, not all unaffected evidence.

## Finding Revalidation

The main agent must try to disprove each finding before accepting it.

- Drop findings that depend on assumptions not supported by code, tests, docs, or local rules.
- Downgrade severity only when the evidence proves the release risk is lower.
- Keep `[must]` when the behavior is broken, a required check is missing, or an applicable rule proves a release blocker.
- Record any remaining uncertainty as `前提・未確認事項`, not as a speculative finding.
- For self-review, classify each finding as `受ける`, `弱めて受ける`, or `却下する` and record the evidence for that decision.
- Judge separately whether the issue is real, whether it belongs in this task, and whether the proposed fix is appropriate. Use `範囲外` for a valid issue outside this task. Accepting an issue does not require accepting its suggested remedy.
- Apply the scope and proportionality gate in the policy before assigning severity. Do not weaken a proven issue merely to finish sooner.

## Output Format

Produce the review in Japanese with findings first.

```text
[must] path/to/file.ext:123
問題点を簡潔に記載
根拠: 参照した規約名、実装、テスト、差分の事実
影響: 現在の成果物で確認できる影響
修正案: 最小変更での修正方針
```

- `[must]`:
  バグ、仕様逸脱、セキュリティ問題、回帰、必須テスト不足、リリースを阻害する規約違反
- `[recommend]`:
  現在の保守性、性能、複雑性への具体的な影響を証明できる改善
- `[nits]`:
  適用範囲が確認できる明示的なローカル規約またはリンターへの軽微な違反

After the findings, include only these optional sections when needed:

- `前提・未確認事項`
- `反証を試みたが壊せなかった点`
- `短い総括`

## Fix Verification and Completion

For review-only requests, report the adjudicated findings without editing code.

For implementation work, default to one independent review plus at most one focused fix-verification pass:

1. Fix accepted `[must]` findings with the smallest appropriate remedy and run relevant checks. `[recommend]` and `[nits]` do not block completion or require automatic fixes.
2. Verify the fix delta and directly affected paths, preferably using the same Reviewer when independent verification is needed. Supply the new snapshot and prior decisions; do not repeat unchanged checks or reopen rejected findings without new evidence.
3. A full re-review requires a concrete new major risk or expanded impact, with its scope and stopping condition stated before starting. Editing alone, a no-finding result, and waiting for another agent are not reasons to restart review or rerun passing tests.
4. At the default pass limit, the main agent adjudicates remaining evidence instead of launching more automatic rounds. Resolve proven blockers or state the exact blocking condition; reaching the limit is not approval. Ask the user only when a requirement, safety decision, or authorization cannot be resolved from available evidence.
5. Finish when acceptance criteria and required checks are satisfied and accepted blockers are resolved. Missing required verification prevents a completion claim; disclose optional verification gaps. Do not require every reviewer to agree.

## Validation Expectations

- Do not hide failing checks.
- Do not recommend skipping or deleting failing tests to make the review pass.
- If a rule conflict exists, cite both sources and explain which one is more specific.
