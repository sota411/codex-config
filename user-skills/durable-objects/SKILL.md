---
name: durable-objects
description: Cloudflare Durable Objectsの設計・実装・レビュー、bindings・migrations・テストの変更に使う。状態の整合性、並行処理、永続化を対象にする。
---

# Durable Objects

Use Durable Objects for per-entity coordination, strongly consistent state, or persistent connections. A stateless handler or simple high-volume key lookup may not need an object.

## Read for the change

Confirm the relevant API or configuration in the [Durable Objects docs](https://developers.cloudflare.com/durable-objects/), using the installed types and compatibility settings.

| Changed concern | Reference and search terms |
|---|---|
| Storage, concurrency, RPC, alarms, WebSockets | [rules.md](references/rules.md): `blockConcurrencyWhile`, `sql.exec`, `setAlarm`, RPC, WebSocket |
| Workers integration, bindings, migrations, types | [workers.md](references/workers.md) |
| Tests, storage persistence, alarms | [testing.md](references/testing.md) |

Read only the relevant sections. For CLI operations, use `wrangler`; do not load unrelated platform guidance.

## Invariants

- Keep one coordination scope per object; choose identity and sharding against real consistency requirements.
- Do not extend `blockConcurrencyWhile` across requests or slow external I/O. Inspect concurrency and storage semantics before changing shared state.
- Do not expose an in-memory state change as durable before persistence succeeds. Account for eviction/restart and retry behavior where the change depends on them.
- An object has one scheduled alarm; coordinate uses of it rather than silently replacing unrelated work.
- Preserve existing object identity and data. Treat migrations or deletion as data-affecting operations with explicit scope, verification, and a recovery strategy.
- Verify the externally observable behavior with the existing test setup. Local tests do not establish live deployment correctness.
