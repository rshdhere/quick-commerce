# Working in this checkout

The repository currently contains two Next.js starter apps. Use apps/web for the customer storefront and apps/docs for documentation. The web home route in apps/web/app/page.tsx imports @repo/ui/button from packages/ui/src/button.tsx. Keep store-specific behavior in the consuming app and reusable presentation in packages/ui.

Node 24 or newer and Bun 1.2.3 are declared in package.json. The root workspace globs cover apps/*, packages/* and tooling/*. Shared ESLint and TypeScript manifests live under tooling/. Check resolution from a clean checkout before relying on either shared config.

Treat serviceability, store selection, catalog, inventory, payment and delivery as proposed domains. Locate the actual data owner and persistence boundary before extending one. For a browsing change, trace the selected delivery area through store selection to product availability. A change of address should trigger a fresh availability and price check for the selected store.
