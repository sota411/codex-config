---
name: workers-best-practices
description: Cloudflare Workersのコード・設定を実装またはレビューするときに使う。変更に関係するruntime API、bindings、非同期処理、streaming、state、secretsを確認する。
---

# Workers Best Practices

Ground Workers changes in the supported runtime and the existing project. Read enough of affected handlers and callers to establish reachable behavior; do not audit unrelated files for an ordinary edit.

## Sources for the changed concern

- Check API signatures and binding shapes in installed Workers types. Check config fields in the installed Wrangler schema.
- Retrieve the relevant [Workers documentation](https://developers.cloudflare.com/workers/) when the API, configuration, limit, or compatibility behavior needs verification. Do not fetch a full type package for changes that do not require it.
- Use [rules.md](references/rules.md) for the affected topic: streaming, `waitUntil`, request state, secrets, bindings, randomness, or observability.
- For a Workers review, read the applicable sections of [review.md](references/review.md). The user's scope and the local `review` evidence and severity policy remain authoritative.
- Use `durable-objects` for object state and `wrangler` for CLI operations. Do not load all platform skills automatically.

## Work and verification

Preserve request isolation, handle asynchronous work through supported lifetime mechanisms, and keep secrets out of code and output. Verify input and binding assumptions at the relevant boundary. Follow the detailed rules only where that behavior is involved.

Use existing checks and validate the changed request path. Report demonstrated problems with file/line and evidence; unverified API assumptions require checking, not speculative findings. Working local examples do not prove a deployed service healthy.
