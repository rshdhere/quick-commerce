# Architecture

apps/frontend/app/page.tsx serves the customer home page and consumes @repo/ui/button from packages/ui. packages/types declares shared TypeScript contracts and packages/validators validates input with Zod. packages/services and packages/drizzle are Bun library workspaces. packages/api contains independent API libraries under v1 (TypeScript), v2 (Go) and v3 (Rust). Trace an actual caller before placing new logic in a shared package. Keep authoritative checkout mutations on the server.
