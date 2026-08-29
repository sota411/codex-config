---
name: review
description: Adversarially verify local changes through a fresh-context Reviewer-Critic loop. Use when the user asks for a local review, a repository explicitly requires it, or a change touches authentication or authorization, destructive data or schema changes, secrets, production operations, breaking public APIs, or security boundaries. Do not auto-invoke for ordinary implementation or documentation changes. For GitHub PR review comments, use `gh-review-autofix` instead.
---

# Review

Use this skill for local code review. Prefer changed lines and staged diffs over broad codebase review unless the user explicitly asks for a wider pass.

For GitHub PR review comments, do not use this skill as the primary workflow. Use `gh-review-autofix` to fetch review threads, judge comments, post replies, and implement accepted fixes.

## Workflow

1. Resolve the review scope first.
   Prefer `git diff --cached`, then `git diff`, then explicit files or ranges named by the user.
   If there is no diff and no explicit target, stop and ask what should be reviewed.
2. Read repository-specific rules before judging code.
   Search for `AGENTS.md`, `CLAUDE.md`, `CODING_GUIDELINE.md`, `PR_REVIEW_GUIDELINE.md`, `README.md`, and test-related docs that apply to the touched files.
3. Read only the minimal surrounding context needed to judge the changed code.
   Use `git diff --name-only`, `git diff --cached --name-only`, `rg`, `sed`, and `nl -ba` to keep the review evidence precise.
4. Apply the severity mapping and checklist from [references/review-policy.md](references/review-policy.md).
5. When subagents are available and allowed, run the sequential Reviewer-Critic workflow below.
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

## Independent Reviewer-Critic Loop

Keep the artifact unchanged throughout the inner loop. Only the main agent may edit it after the review has converged.

1. Start a new `reviewer_deep` as Reviewer with `fork_turns="none"`.
   Give it only the raw diff or artifact, acceptance criteria, applicable rules, surrounding code needed to judge the change, and reproduction commands. Do not provide the author's rationale, suspected defects, intended fix, or expected verdict.
2. Require Reviewer to give each candidate finding a stable ID and include severity, `file:line`, concrete evidence, demonstrated impact, and a minimal fix direction.
3. Start a separate new `reviewer_deep` as Critic with `fork_turns="none"`.
   Give it the same artifact context plus Reviewer's latest review and the prior inner-loop exchange.
4. Critic must end with exactly one verdict:
   - `AGREE`: every candidate is supported and no evidenced issue is missing.
   - `DISAGREE_EVIDENCE: <evidence>`: code, tests, rules, primary sources, or measurements contradict a candidate or prove a missed issue. Use this whenever at least one such item exists.
   - `DISAGREE_CONCERN: <missing evidence>`: no contrary evidence was found, but a candidate is not sufficiently proven. This is an internal evidence request, not a final finding.
5. Send Critic's response back to the same Reviewer thread. Reviewer must revise or drop a candidate contradicted by evidence. For `DISAGREE_CONCERN`, Reviewer must prove the issue with verifiable evidence or drop the candidate; any refuting evidence requires dropping it.
6. Send the revised review back to the same Critic thread. One Reviewer response plus one Critic response is one round. Stop on `AGREE` or after five rounds.
7. If five rounds do not converge, the main agent must inspect the cited evidence and adjudicate. Unsupported points become `前提・未確認事項`, not findings.

Use the named `reviewer_deep` profile for both roles. Do not substitute an unnamed or default agent that inherits the parent model. If subagents are unavailable, apply the same evidence gate in the current context and state that independent Critic verification was not run.

After any artifact edit, discard the prior approval and start a fresh Reviewer-Critic loop for the new version.

## Finding Revalidation

The main agent must try to disprove each finding before accepting it.

- Drop findings that depend on assumptions not supported by code, tests, docs, or local rules.
- Downgrade severity only when the evidence proves the release risk is lower.
- Keep `[must]` when the behavior is broken, a required check is missing, or an applicable rule proves a release blocker.
- Record any remaining uncertainty as `前提・未確認事項`, not as a speculative finding.
- For self-review, classify each finding as `受ける`, `弱めて受ける`, or `却下する` and record the evidence for that decision.

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

## Self-Review Loop

Use this loop when the skill is invoked as part of your own implementation work:

1. Run the fresh-context Reviewer-Critic loop on the current diff.
2. Revalidate every finding and classify it as `受ける`, `弱めて受ける`, or `却下する` with evidence.
3. Fix every accepted `[must]`.
4. Run the narrowest relevant validation.
5. Run a new fresh-context Reviewer-Critic loop on the updated diff.
6. Do not treat the work as complete until accepted `[must]` findings are 0.

## Validation Expectations

- Do not hide failing checks.
- Do not recommend skipping or deleting failing tests to make the review pass.
- If a rule conflict exists, cite both sources and explain which one is more specific.
