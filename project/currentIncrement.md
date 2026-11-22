# Current increment

## Objective

Deliver requirement [003 — User Shopping Lists](requirements/features/003-userShoppingLists.md): import text lists into JSON lists and maintain them in a Textual terminal UI.

## Scope

- Import a text list into `output/<list>.json` with `groceries list import`.
- Keep several named lists and choose between them in a list picker.
- Edit a JSON list (add, edit, activate/deactivate, remove, save) with
  `groceries --ui`, using the shared OMP TUI theme.
- Keep one user's list document from affecting another.
- Keep list loading, modification, and saving testable without a UI.
- Catalogue-linked lists are deferred (see the requirement).

## Status

In progress on `release/0.2`, started 2026-11-22. Version 0.2a1 delivered the
list document model, `list import`, the terminal UI and the `list send` rename
(ADR-003 amendment). Version 0.2a2 (branch `feature/003-listPicker`) adds named
lists and the list picker. Review and acceptance remain.

Use the [003 agent prompt](requirements/prompt/003-userShoppingLists.md) for implementation handoff.

## Next increments

1. [004 — Grocery Web Application](requirements/features/004-groceryWebApplication.md)
2. [005 — Tesco Integration](requirements/features/005-tescoIntegration.md)
3. [006 — Authentication and User Isolation](requirements/features/006-authentication.md)
4. [007 — Production Deployment](requirements/features/007-deployment.md)

See [ADR-001](adr/001-webApplicationArchitecture.md) and
[ADR-002](adr/002-groceryCatalogueSchema.md) for the architecture and catalogue
schema these increments depend on.
