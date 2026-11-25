# Changing cart or checkout

1. Start at apps/web/app/page.tsx or the storefront route that replaces it. Trace the action to the server write and identify who owns store stock, the quoted price and the order state. If adding the first server write, make that ownership explicit.
2. At order submission, revalidate store serviceability, quantities and the payable total on the server. Represent money in integer minor units. Present a changed quote to the shopper before charging.
3. For stock reservation, exercise two shoppers ordering the last unit. For order creation and payment callbacks, replay the same request and verify one order and one financial effect. Check that an expired or cancelled reservation releases stock once.
4. In apps/web run bun run lint and bun run check-types for storefront changes. Run heavier checks in Codex Cloud on the exact revision and working-tree changes. The starter has no checkout test script. When introducing checkout, add a focused behavioral check for the affected invariant and record its observed result.
