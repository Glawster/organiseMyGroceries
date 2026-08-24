# ADR-002 — Grocery catalogue schema

**Status:** Accepted

**Date:** 2026-08-24

## Context

Requirement 002 introduces a persistent shared grocery catalogue imported from a
plain-text grocery list. Later user-list and web increments will reference
catalogue identities rather than copying product definitions. The existing
shopping-list JSON is a bare array that includes quantity and unit, which must
not appear in shared catalogue data.

## Decision

1. Persist the catalogue as a versioned JSON document `{version, items}` behind
   the `catalogue` module, not as a bare array.
2. Identify items with stable `item-N` values, zero-padded to at least three
   digits, allocated as one higher than the current maximum.
3. Detect duplicates by normalised, case-insensitive display name. Report them
   explicitly. Fail when a name is ambiguous across two existing items.
4. Keep user selection, quantity, and profile data out of the catalogue schema.
5. Treat import as additive: existing identifiers and enrichment are preserved
   when the same source is imported again.

## Consequences

### Positive

- User lists can reference `id` without depending on array position or display
  name spelling.
- Catalogue JSON cannot be mistaken for a shopping list that contains quantity.
- A document version supports later storage migration without rewriting callers
  that go through the catalogue module.

### Negative

- Hand-edited catalogues must include every documented field.
- Name-based duplicate detection will not merge distinct spellings of the same
  product unless they normalise to the same key.

## Alternatives considered

### Reuse the shopping-list JSON array

Rejected because that schema includes quantity and unit and would mix shared
product data with user-list state.

### SQLite immediately

Deferred, consistent with ADR-001. JSON is sufficient for this increment if
persistence stays behind the catalogue module.

## Related requirements

- [002 — Grocery Catalogue](../requirements/features/002-groceryCatalogue.md)
- [003 — User Shopping Lists](../requirements/features/003-userShoppingLists.md)
- [ADR-001 — Web Application Architecture](001-webApplicatinArchitecture.md)
