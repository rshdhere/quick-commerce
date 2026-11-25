# Feature Development

1. Identify the route, actor, acceptance example and failure case using the architecture and product guides.
2. Trace the owning workspace and server boundary. For cart or order changes follow .agents/workflows/checkout.md when available and apply the database and security guides.
3. Implement a vertical slice. Run the affected workspace lint and check-types scripts, then exercise the acceptance example. Record any unavailable checks.
