# Quick-commerce CMS agent guide

This repository is the foundation for a Blinkit/Zepto-style grocery platform. Trace each change from the person taking the action (shopper, catalog editor or store operator) to the store, SKU and order it can affect. The storefront and API packages are scaffolds. Check the implementation before assuming a checkout, payment provider or fulfillment flow exists.

<!-- BEGIN:turborepo-agent-rules -->

# This is NOT the Turborepo you know

Turborepo configuration, task behavior, and CLI commands can vary between installed versions and may differ from your training data. Resolve the `turbo` package from this file's directory or relevant workspace; in monorepos, it may not be visible from the repository root. For example, run `node -p "require.resolve('turbo/package.json')"` from a workspace that depends on `turbo`.

Read `docs/README.md` inside that installed package first, then read the relevant pages from its `docs/` directory before changing Turborepo configuration or commands. Heed deprecation notices. These bundled docs match the installed package version and are available without network access.

This block is written and re-added by `turbo` before repository-scoped commands when an AI agent is detected. In the Turborepo source repository, its template is defined in `crates/turborepo-cli/src/cli/agent_guidance.rs`. Removing the managed block while updates are enabled means a later qualifying invocation will add it again. Set `"agentGuidance": true` in the root `turbo.json` or `turbo.jsonc` to opt in; this does not remove an existing block. Keep the block committed with your work to avoid an uncommitted change on the next agent invocation.
<!-- END:turborepo-agent-rules -->

## Where changes belong

| Area | Starting point |
| --- | --- |
| Storefront and shared UI | Start at `apps/frontend/app/page.tsx`. Keep route behavior in the app and reusable presentation in `packages/ui`. Use `apps/frontend` for storefront commands in the project guides. |
| Types and validation | Declare shared TypeScript contracts in `packages/types`. Validate external input with Zod in `packages/validators`. The existing store-item contract pairs a store ID with a SKU. |
| Services and persistence | Put shared service implementations in `packages/services`. Use `packages/drizzle` for database access once a dialect and driver are selected. Record that choice before adding migrations. |
| Versioned APIs | Work in `packages/api/v1` for TypeScript, `packages/api/v2` for Go and `packages/api/v3` for Rust. Identify the consuming client and affected version before changing a contract. When versions promise the same behavior, verify them with the same request and response examples. |

## Commerce behavior

- **Catalog and store operations.** Distinguish shared product details from each store’s assortment, price and stock. Authorize CMS writes against the operator’s store scope on the server. For a store-specific edit, verify what shoppers see at both the edited store and a second store carrying the same SKU.
- **Serviceability and checkout.** When a shopper changes address, resolve the fulfilling store again and refresh the cart quote. At submission, recheck stock, serviceability and totals on the server. Calculate money in integer minor units with explicit currency and obtain confirmation for a changed price before charging.
- **Inventory and payments.** Exercise two shoppers requesting the last unit. Only one reservation can succeed. Replaying a checkout request or payment callback must produce one order and one financial effect. Expiry and cancellation must release a reservation at most once.
- **Fulfillment and privacy.** Validate order transitions against the current state and acting role. Keep delivery addresses, phone numbers and payment payloads out of logs and test fixtures. Confirm product policy before introducing substitutions, refunds or delivery-time promises.

## Task routing and verification

For storefront work, start with `.agents/context/quick-commerce.md`. For cart, stock, pricing, payment or order changes, follow `.agents/workflows/checkout.md`. Use `commerce-reviewer` for explicitly delegated commerce reviews.

Start with .agents/context/architecture.md, product.md and tech-stack.md in the same directory. Consult database.md for persistence and decisions.md for open architecture choices. Apply the relevant files in .agents/rules/ for coding, security, testing, performance and Git changes.

Use the matching project skill in .agents/skills/ for feature implementation, bug fixes, code review, migrations, security audits and releases. Detailed procedures live in .agents/workflows/ and drafting aids in .agents/templates/. Use .codex/agents/ for explicitly delegated work. For upstream issue discovery and PR preparation, use oss-contribution after identifying the upstream.

Run .agents/scripts/verify.sh to validate the setup and .agents/scripts/health-check.sh to inspect local prerequisites. Monitor available RAM and swap before and during local work. If memory pressure threatens desktop stability, stop the task’s own heavy processes and move the work to Codex Cloud. Run heavy tests, builds and browser sessions in Codex Cloud against the exact current changes. If cloud access is unavailable, report the blocker and continue lightweight work.
