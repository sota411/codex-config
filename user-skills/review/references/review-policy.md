# Review Policy

## Evidence Priority

1. Repository-local instructions and guidelines
2. Reachable behavior in the current diff and surrounding implementation
3. Existing tests, command output, and documented behavior
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

## Scope Selection

Review targets in this order:

1. `git diff --cached`
2. `git diff`
3. Files, directories, or code snippets explicitly named by the user

If the user asks for a review of a PR or commit range, use that exact scope instead.

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

## Independent Adversarial Review Policy

When subagents are available and allowed, use one fresh-context Reviewer and one separate fresh-context Critic. Give both the frozen artifact, acceptance criteria, applicable rules, and required surrounding context. Do not pass the author's reasoning, suspected defects, or expected verdict.

Critic must classify the review as `AGREE`, `DISAGREE_EVIDENCE`, or `DISAGREE_CONCERN`. Evidence-backed disagreement causes Reviewer to revise or drop the affected finding. A concern without contradicting evidence requires Reviewer to prove the finding with verifiable evidence or drop it; it never becomes a final finding by itself.

Reuse the same two threads for at most five inner rounds. Do not edit the artifact during those rounds. If the artifact changes, start both roles again in fresh context. If the fifth round does not converge, the main agent adjudicates from the cited evidence and moves unsupported points to `前提・未確認事項`.

## Finding Revalidation

Before final output, the main agent must try to disprove every finding:

- Is the cited line actually in the active path?
- Does existing behavior or a local rule already justify the change?
- Is the finding based on a real failure mode rather than preference?
- Is the severity consistent with the release risk?

Remove findings that fail this verification. Keep uncertainty in `前提・未確認事項`. For self-review, classify each finding as `受ける`, `弱めて受ける`, or `却下する` and record the evidence for the decision.

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

When reviewing your own implementation, the review is complete only when:

- `[must]` is 0
- accepted fixes are reflected in the diff
- every finding has an evidence-backed `受ける`, `弱めて受ける`, or `却下する` decision
- relevant checks were run or the exact missing check is stated
