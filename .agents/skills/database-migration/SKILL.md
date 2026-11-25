---
name: database-migration
description: Plan or implement a change to commerce persistence.
---

Read .agents/context/database.md and locate the actual schema and runner. If introducing the first database, record the choice in an ADR. Sequence compatible schema expansion, resumable backfill, verification and later cleanup. Exercise a fresh database and an upgrade from representative existing records. Document recovery before applying any production change.
