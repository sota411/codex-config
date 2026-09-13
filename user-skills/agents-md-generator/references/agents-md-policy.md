# AGENTS.md Policy

## Personal Guidance

For `~/.codex/AGENTS.md`, keep durable user preferences, evidence and quality requirements, authorization boundaries, completion criteria, and pointers to specialized skills. Preserve necessary safety and operational invariants across models; a model upgrade alone is not evidence that a rule can be deleted.

Avoid repository-specific commands, full tool catalogs, fixed document-reading lists, and procedures already maintained in a skill. Explicit user choices prevail over a generic simplification recommendation.

## Repository Guidance

The remaining include/exclude rules concern repository-local files.

## Include

- Repository purpose and important directory layout when it changes day-to-day work.
- Build, test, lint, format, migration, and local development commands that are actually present.
- Language, framework, package manager, and runtime constraints that differ from global defaults.
- Coding conventions that are visible in current code or documented locally.
- Test expectations, acceptance checks, and review workflow that the repository requires.
- Secrets, deployment, data, or destructive-operation cautions that affect implementation safety.
- Memo or planning rules only when the repository has a specific file path or format.

## Exclude

- Global Codex rules that already live in `~/.codex/AGENTS.md`, unless a narrower repository override is necessary.
- Long examples that belong in a skill, README, or docs page.
- Tool installation manuals unless the repository itself requires a nonstandard setup.
- Aspirational best practices with no local evidence.
- Old Claude global configuration. Repository-local `CLAUDE.md` can supply relevant project facts; do not duplicate facts already covered by `AGENTS.md`.

## Conflict Handling

- Prefer `AGENTS.md` closest to the edited file.
- Prefer documented repository commands over inferred commands.
- Prefer current manifests and config files over stale prose.
- If current evidence cannot resolve a material conflict, ask for the intended rule. Record non-blocking assumptions and continue independent work.

## Recommended Shape

Use short sections. Avoid nesting unless the repository has multiple independent packages.

```markdown
# AGENTS.md

## Project
- <purpose and important boundaries>

## Commands
- `<command>`: <when to run it>

## Coding Rules
- <repo-specific rule>

## Testing
- <required checks>

## Notes
- <security, deployment, memo, or review constraints>
```

## Verification

Before finishing, verify these facts from the repository:

- Mentioned files and directories exist.
- Commands match package scripts, Makefile targets, task files, or documented tooling.
- Repository instructions do not duplicate global guidance; personal instructions do not absorb repository-specific procedures.
- Every removal has a complete replacement or an evidence-backed reason, while unique user requirements remain.
- The file is concise enough to be read every turn.
