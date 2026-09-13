---
name: cloudflare-one
description: Cloudflare Oneの設計・設定・障害調査・レビューに使う。Access、Gateway、WARP、Tunnel、WAN、DLP、CASB、identityのうち対象製品と変更影響を確認する。
---

# Cloudflare One

Use current [Cloudflare One documentation](https://developers.cloudflare.com/cloudflare-one/), the docs MCP, or API schemas for limits, fields, category IDs, and exact UI paths.

## Workflow

1. Identify the request, affected product, traffic path, and change impact from available context. Ask only for missing information that changes the decision.
2. Inspect relevant existing account resources when access is available. Do not collect unrelated identity, network, or policy details.
3. Search [task-specific checks](references/guardrails.md) for the affected topic: Access/identity, Tunnel/private DNS, Gateway/TLS/DLP, device posture, CASB/risk, or WAN. Read only those sections and the official docs needed for them.
4. Prepare the concrete change, prerequisites, validation, and rollback. For risky changes, prefer a disabled or pilot-scoped policy unless a wider rollout has already been explicitly authorized.
5. Verify affected allowed/denied flows or device/network behavior. Distinguish configured state, observed logs, and an end-to-end device test; do not report an unperformed check as successful.

## Boundaries

- Access handles application authorization; Gateway handles traffic inspection/filtering. Private access also needs a supported network on-ramp, routes, and DNS; creating an Access app alone is insufficient.
- Group policies depend on verified identity claims/sync. TLS inspection and DLP need planned trust and inspection exceptions. Consult the corresponding reference before changing these boundaries.
- Never guess category IDs, resource IDs, selectors, or API bodies; retrieve the schema and relevant account objects.
- Do not enable broad production policies without explicit approval. Existing approval persists for the authorized scope; do not ask again at every reversible preparation step.
- Use the fully qualified available MCP tool names. Keep secrets in protected storage and out of transcripts or command arguments; preserve one-time credentials when the operation returns them.
