# Development stack

The root manifest specifies Node >=24 and Bun 1.2.3. Both apps use the Next.js App Router, React and TypeScript. Web runs on port 3000 and docs on 3001. Use the scripts declared in the relevant package.json. Shared ESLint and TypeScript packages live in tooling/. Bun resolves apps/*, packages/* and tooling/* as workspaces.
