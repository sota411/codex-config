---
name: cloudflare
description: Cloudflareの製品選定・横断的な構成設計や、専門skillで扱わない製品の開発・設定に使う。既存構成と必要な公式資料から判断する。
---

# Cloudflare

Use this skill for product selection, cross-product architecture, and products without a more specific installed skill.

## Route by the task

| Work | Guidance |
|---|---|
| Workers code and runtime behavior | `workers-best-practices` |
| Durable Objects and stateful coordination | `durable-objects` |
| Wrangler commands or configuration | `wrangler` |
| Access, Gateway, WARP, Tunnel, WAN, identity | `cloudflare-one` |
| Other products, such as Pages, D1, R2, or Workers AI | The relevant product's [official documentation](https://developers.cloudflare.com/) |

Use another skill only when the task crosses its boundary. Do not load every Cloudflare skill for a single-product change.

## Decisions and sources

- Read the existing project, dependencies, and relevant account resources first. Choose products against the actual requirements; do not introduce infrastructure for a speculative need.
- Verify changing limits, pricing, APIs, flags, and configuration fields in the relevant official docs or schema. Search only the product and issue in question; the [changelog](https://developers.cloudflare.com/changelog/) is useful when compatibility or a recent change matters.
- Prefer installed Workers types and `node_modules/wrangler/config-schema.json` for the installed version. Resolve differences against version-matched official documentation before changing code.
- Preserve authorization and existing production resources. Make the intended environment and resource changes concrete, verify affected behavior, and disclose checks that require unavailable account or device access.
