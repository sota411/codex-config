---
name: wrangler
description: Wranglerのコマンド実行・設定変更・障害調査に使う。プロジェクトの固定バージョンと実行方法を優先し、対象のhelp・schema・公式資料で確認する。
---

# Wrangler CLI

Use the project's Wrangler installation and existing package scripts. A missing global command does not mean the project lacks Wrangler.

## Resolve the command

1. Check the package manager, manifest, lockfile, relevant scripts, Wrangler version, and target config/environment.
2. Use that project's command runner or script. Inspect the installed command's `--help`, `node_modules/wrangler/config-schema.json`, or [Wrangler documentation](https://developers.cloudflare.com/workers/wrangler/) for the operation being performed.
3. Install Wrangler only when the requested work actually needs it and no usable installation exists. Follow the project's dependency policy and package manager; do not automatically install or upgrade to `@latest`.
4. Prefer supported Wrangler operations over custom API calls when they cover the requirement. Resolve incompatible flags or fields for the installed version instead of silently changing versions.

## Configuration and validation

- Preserve the existing configuration format and `compatibility_date` unless the task requires a change. For new config or a compatibility change, check the relevant [configuration docs](https://developers.cloudflare.com/workers/wrangler/configuration/).
- Check the effective environment and binding names. Generate types when binding/config changes affect them, and run the existing checks for the changed behavior.
- Use existing local test/development scripts. Local development can still use remote bindings or Workers AI; inspect their external access and cost implications before running them.
- For deployment, confirm the account, environment, resources, relevant health, and rollback path; use the version's dry-run validation before switching. Apply existing authorization without asking again, and obtain approval for unapproved destructive or consequential external changes.
- A successful dry run or local test does not prove production health. Check the deployed version and affected behavior when deployment is part of the request.

## Secrets

Keep secrets out of config, source, logs, and command arguments. Use supported secure interactive input, a protected input file, or CI secret injection. Local `.dev.vars` files must remain outside version control. Do not print credential values while diagnosing authentication.
