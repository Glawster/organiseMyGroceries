# Current increment

## Objective

Deliver requirement [003 — User Shopping Lists](requirements/features/003-userShoppingLists.md): persist independent per-user selections against the shared grocery catalogue.

## Scope

- Persist per-user selections against catalogue identifiers.
- Keep one user's list from affecting another.
- Handle inactive or removed catalogue items predictably.
- Keep list loading, modification, and saving testable without a UI.

## Status

Ready to start. Requirement 002, the shared grocery catalogue, was completed on
2026-08-24. The catalogue import path and versioned JSON document are in place.

Use the [003 agent prompt](requirements/prompt/003-userShoppingLists.md) for implementation handoff.

## Next increments

1. [004 — Grocery Web Application](requirements/features/004-groceryWebApplication.md)
2. [005 — Tesco Integration](requirements/features/005-tescoIntegration.md)
3. [006 — Authentication and User Isolation](requirements/features/006-authentication.md)
4. [007 — Production Deployment](requirements/features/007-deployment.md)

See [ADR-001](adr/001-webApplicationArchitecture.md) and
[ADR-002](adr/002-groceryCatalogueSchema.md) for the architecture and catalogue
schema these increments depend on.
