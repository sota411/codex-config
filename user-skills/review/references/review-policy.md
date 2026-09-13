# Review Policy

## Evidence Priority

1. Explicit user requirements, review scope, and acceptance criteria
2. Applicable repository-local instructions and guidelines
3. Reachable behavior, existing tests, command output, and documented contracts
4. Version-matched primary documentation and measurements

General engineering principles and preferences may guide investigation, but they are not evidence for a finding. Never let them override a project-specific documented rule.

## Evidence Gate

A final finding must show both the problem and its present impact through at least one of:

- a reachable code path and the resulting incorrect behavior
- a test, compiler, linter, or command result
- an explicit acceptance criterion or applicable repository rule
- a version-matched API contract or primary source tied to the changed code
- a measurement for performance or resource claims

Do not publish a finding based only on hypothetical language, an undocumented convention, a generic best practice, or missing context. Keep those as internal investigation prompts or `前提・未確認事項`.

## Scope and Proportionality Gate

Honor the explicit target first; otherwise review `git diff --cached`, then `git diff`. Include only surrounding code needed to establish the change's impact.

- In a diff review, report defects introduced or worsened by this change. Report serious pre-existing issues separately as `範囲外`; do not silently add their repair to this task. An explicitly requested wider audit can include existing issues.
- Require meaningful correctness, performance, security, or maintainability impact and a discrete, actionable issue that the author would reasonably fix under the stated requirements.
- Do not demand more rigor than the requirements, risk, and surrounding code warrant. This does not excuse broken contracts, security boundaries, or required validation.
- Do not depend on unstated assumptions about deployment, supported inputs, or author intent. Name the triggering conditions and the affected reachable path. A reproducible edge case can qualify even if it is uncommon; speculation alone cannot.
- An intentional behavior change is not itself a bug. Verify documented tradeoffs against requirements; intent does not excuse a demonstrated regression outside the intended change or an applicable safety violation.
- For claimed effects elsewhere, identify the affected callers or consumers and explain the causal path. Generic warnings about possible breakage are not findings.
- Ignore trivial style unless it obscures meaning or violates an applicable documented standard. If several designs satisfy the constraints, accept the author's choice.
- Return every qualifying finding, deduplicated by root cause. Prefer no findings over padding the review with suggestions.

Adapted from [Codex's review rubric](https://github.com/openai/codex/blob/52e73e3a548ae5310c7765995b9803dd538b82b0/codex-rs/prompts/templates/review/rubric.md). The local severity labels below remain authoritative for this skill.

## Severity Mapping

### `[must]`

Use `[must]` when the change has a concrete correctness or release risk.

- Broken behavior, runtime error, compile error, or failing requirement
- Security issue or secrets exposure
- Clear regression against existing behavior or tests
- Fail Fast violation that hides an error without explicit justification
- Missing validation that is required to prove the change is complete
- Applicable rule violation that blocks a required check or creates concrete release risk

### `[recommend]`

Use `[recommend]` only when the code can ship and evidence shows a current maintainability, performance, or complexity cost.

- Non-trivial duplication at cited locations with a concrete synchronization cost
- Unnecessary reachable complexity that demonstrably increases the change surface
- A measured performance or resource cost that is not a release blocker
- A violation of an applicable maintainability rule without release risk

### `[nits]`

Use `[nits]` only for a low-impact violation of an explicit, applicable local rule or configured linter.

- Naming, comment, formatting, or consistency violations named by that rule

Do not report subjective polish as `[nits]`. Do not downgrade a real bug into `[recommend]` or `[nits]`.

## Checklist

Review the diff against these categories when relevant:

1. Correctness and regressions
2. Security and secret handling
3. Error handling and Fail Fast behavior
4. Edge cases and boundary values
5. Performance and unnecessary complexity
6. DRY, KISS, YAGNI, SOLID, and consistency with existing patterns
7. Testability and validation coverage
8. Comments, docs, config, and schema alignment

Only report a category when the diff actually presents evidence for it.

## Bounded Independent Review

1. Freeze the review snapshot and start one `reviewer_deep` as Reviewer with `fork_turns="none"`.
   Give it the diff and base, requirements, non-goals, acceptance criteria, supported environments, applicable rules, necessary surrounding code, and reproduction commands. Include documented intentional tradeoffs as claims to verify, not proof of correctness. Do not suggest defects, fixes, or an expected verdict.
2. Reviewer returns actionable candidates with stable IDs, severity, `file:line`, trigger conditions, evidence, current impact, and a minimal fix direction. No finding quota; return no findings when none qualify.
3. The main agent adjudicates each candidate using the revalidation rules below. Reviewer agreement is not evidence and does not authorize edits.
4. Only for an important finding whose validity or applicability remains disputed, use one separate `reviewer_deep` as Critic with `fork_turns="none"`. Give it the disputed IDs, snapshot, requirements, and evidence from both sides. Ask for one finding-specific verdict: `成立`, `不成立`, or `未確認`, with evidence or the exact missing check. Do not commission another broad search for missed issues.
5. The main agent decides after that response; do not run a Reviewer-Critic dialogue until consensus. An incidentally discovered serious issue must still be reported with evidence, but does not automatically restart review.

Use the named profile for either role; do not silently substitute a default agent. If subagents are unavailable, apply the same evidence gate locally and state that independent review was not run. Only the main agent edits artifacts. A changed snapshot invalidates conclusions for affected paths, not all unaffected evidence.

## Fix Verification and Completion

For review-only requests, report the adjudicated findings without editing code.

For implementation work, default to one independent review plus at most one focused fix-verification pass:

1. Fix accepted `[must]` findings with the smallest appropriate remedy and run relevant checks. `[recommend]` and `[nits]` do not block completion or require automatic fixes.
2. Verify the fix delta and directly affected paths, preferably using the same Reviewer when independent verification is needed. Supply the new snapshot and prior decisions; do not repeat unchanged checks or reopen rejected findings without new evidence.
3. A full re-review requires a concrete new major risk or expanded impact, with its scope and stopping condition stated before starting. Editing alone, a no-finding result, and waiting for another agent are not reasons to restart review or rerun passing tests.
4. At the default pass limit, the main agent adjudicates remaining evidence instead of launching more automatic rounds. Resolve proven blockers or state the exact blocking condition; reaching the limit is not approval. Ask the user only when a requirement, safety decision, or authorization cannot be resolved from available evidence.
5. Finish when acceptance criteria and required checks are satisfied and accepted blockers are resolved. Missing required verification prevents a completion claim; disclose optional verification gaps. Do not require every reviewer to agree.

## Finding Revalidation

Before final output, the main agent must try to disprove every finding:

- Is the cited line actually in the active path?
- Does existing behavior or a local rule already justify the change?
- Is the finding based on a real failure mode rather than preference?
- Is the severity consistent with the release risk?

Lower severity only when evidence demonstrates lower release risk. Remove findings that fail this verification. Keep uncertainty in `前提・未確認事項`. For self-review, record `受ける`, `弱めて受ける`, `却下する`, or `範囲外` with evidence. Separate validity, task applicability, and remedy selection; a valid finding does not make its suggested implementation mandatory.

## Hook and Memo Guard Changes

When reviewing `codex_memo_guard.py`, hook configuration, or `memo.md` enforcement, treat these as required checks:

- `stop`, `summarize`, and `pre-commit` modes still agree on memo path resolution and marker validation.
- `stop` never blocks the turn and finishes within its timeout; heavy work stays in the detached `summarize` child.
- Plan Mode and subagent payloads still bypass memo writes.
- The summarizer `codex exec` call keeps recursion prevention (`-c features.hooks=false`) and `--ephemeral`.
- The per-turn state file prevents double spawn and double append; appending is also idempotent via the `done` marker check.
- Change-turn classification keeps unknown commands and unknown tools on the change side, and `#nomemo` always wins over `#memo`.
- Summarizer failures are raised and land in the per-turn log with a `failed:` state; they are never silently swallowed.
- `config.toml` hook entries match the script path, timeout, and enabled state, and `[hooks.state]` entries match the registered hooks.
- Tests cover any changed marker, state, classification, or memo path behavior.

Use `[must]` when a hook change blocks the main turn, breaks recursion prevention, lets a failed summary look successful, disables the configured hook by accident, or lacks tests for changed enforcement behavior.

## Finding Requirements

Every finding must include:

- severity
- file path and line reference
- concrete problem statement
- trigger conditions, expected versus actual behavior, and connection to the reviewed change
- evidence source
- demonstrated present impact
- minimal fix direction

Avoid vague comments such as `気になる`, `可能性があります`, or `検討してください`.

## No-Finding Case

If no findings exist, say so explicitly.

Recommended wording:

```text
指摘はありません。
未実施の確認: <あれば記載。なければ「なし」>
反証を試みたが壊せなかった点: <確認できた堅い点。なければ「なし」>
```

## Self-Review Completion Rule

Use [Fix Verification and Completion](#fix-verification-and-completion) as the single source for pass limits and completion. A disclosed missing required check or unresolved accepted blocker means the implementation is not complete; optional suggestions do not block it.
