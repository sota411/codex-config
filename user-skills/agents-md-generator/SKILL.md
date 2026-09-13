---
name: agents-md-generator
description: Codexの個人共通・リポジトリ固有のAGENTS.mdを作成・更新し、適用範囲と根拠を保って重複や古い指示を整理する依頼に使う。
---

# AGENTS.md Generator

Keep instructions short and specific to the scope the user requested.

## Workflow

1. Identify the target from the request and existing files. Distinguish personal guidance (`~/.codex/AGENTS.md`) from repository-local instructions. Ask only if multiple plausible targets remain.
2. Read the existing target and relevant instructions. For repository work, verify only the commands, manifests, architecture, tests, or release documentation needed by the requested change. Use history as evidence of preferences, not as authority to restore superseded rules.
3. Use [agents-md-policy.md](references/agents-md-policy.md) to decide what belongs at that scope. Keep global preferences in personal guidance and repository facts in repository guidance.
4. Write concise UTF-8 instructions, normally in Japanese. State outcomes, decision boundaries, and completion criteria. Route detailed procedures to the existing skill or documentation that owns them.
5. Verify referenced paths and commands. For removed or moved instructions, identify the complete replacement or the evidence that makes the rule unnecessary. Do not remove a unique requirement merely because another instruction partly overlaps.

## Boundaries

Preserve explicit user requirements and existing authorization. Confirmations belong to unresolved decisions or unauthorized consequential actions, not every reversible step. Do not replace a requested deliverable with a plan or memo.

When scoped to Codex, keep Claude configuration unchanged. Read Claude history only when requested, and repository-local `CLAUDE.md` when relevant as project guidance. Resolve conflicts using current, applicable evidence and report unresolved material differences.
