# Current increment

## Objective

Deliver requirement [002 — Grocery Catalogue](requirements/features/002-groceryCatalogue.md): establish the persistent shared grocery catalogue and a repeatable import path from the existing one-item-per-line grocery list.

## Scope

- Define and validate the catalogue JSON model.
- Import and normalise the existing plain-text grocery list.
- Assign and preserve stable catalogue item identifiers.
- Detect duplicates explicitly.
- Keep user-specific selection and quantity state out of the catalogue.
- Keep catalogue logic independent of UI/browser frameworks.
- Add automated tests and maintained documentation for the durable behaviour.

## Status

Ready to start. Requirement 001, the OMP alignment increment, was completed on 2026-08-24. Requirements 002–007 now describe the planned path from shared catalogue through multi-user web application and production deployment.

Use the [002 agent prompt](requirements/prompt/002-groceryCatalogue.md) for implementation handoff.

## Next increments

1. [003 — User Shopping Lists](requirements/features/003-userShoppingLists.md)
2. [004 — Grocery Web Application](requirements/features/004-groceryWebApplication.md)
3. [005 — Tesco Integration](requirements/features/005-tescoIntegration.md)
4. [006 — Authentication and User Isolation](requirements/features/006-authentication.md)
5. [007 — Production Deployment](requirements/features/007-deployment.md)

See [ADR-001](adr/001-webApplicatinArchitecture.md) for the accepted architecture linking these increments.
