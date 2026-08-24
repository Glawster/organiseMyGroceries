# Current increment

## Objective

Deliver requirement [002 — Grocery Catalogue](requirements/features/002-groceryCatalogue.md): establish the persistent shared grocery catalogue and a repeatable import path from the existing one-item-per-line grocery list.

## Scope

- Persist per-user selections against catalogue identifiers.
- Keep one user's list from affecting another.
- Handle inactive or removed catalogue items predictably.
- Keep list loading, modification, and saving testable without a UI.

## Status

Ready to start. Requirement 002, the shared grocery catalogue, was completed on
2026-08-24. The catalogue import path and versioned JSON document are in place.

Use the [002 agent prompt](requirements/prompt/002-groceryCatalogue.md) for implementation handoff.

## Next increments

1. [004 — Grocery Web Application](requirements/features/004-groceryWebApplication.md)
2. [005 — Tesco Integration](requirements/features/005-tescoIntegration.md)
3. [006 — Authentication and User Isolation](requirements/features/006-authentication.md)
4. [007 — Production Deployment](requirements/features/007-deployment.md)

See [ADR-001](adr/001-webApplicatinArchitecture.md) and
[ADR-002](adr/002-groceryCatalogueSchema.md) for the architecture and catalogue
schema these increments depend on.
