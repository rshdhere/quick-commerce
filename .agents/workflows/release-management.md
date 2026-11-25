# Release Management

1. Identify the exact candidate revision and affected workspaces. Include schema and environment changes in the release notes.
2. In Codex Cloud, run affected lint, type checks and builds against that candidate. Record results and a rollback target.
3. Verify relevant shopper journeys and payment retry behavior in the intended staging environment. Report missing deployment configuration. Obtain explicit release authorization before publishing or deploying.
