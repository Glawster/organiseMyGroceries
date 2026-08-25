# ADR-003 — Command-line object model

**Status:** Accepted

**Date:** 2026-08-25

## Context

organiseMyGroceries is moving from a single-purpose Tesco shopping-list helper
towards a broader family grocery application with a shared catalogue,
independent user shopping lists, store integrations, a web application, and
production deployment.

Requirements 002–007 introduce several distinct domain concepts. Without a
stable CLI vocabulary, each increment could invent overlapping or conflicting
commands. In particular, the existing command `groceries list add` currently
means "send the current list to Tesco", but Requirement 003 makes `list add`
the natural command for adding a catalogue item to a user's shopping list.

The CLI should expose domain concepts rather than implementation details so the
same underlying services can later be used by the web application.

## Decision

Use the command shape:

```text
groceries <object> <action> [options]
```

The initial domain objects are:

- `catalogue`
- `list`
- `user`
- `store`
- `basket`
- `server`
- `system`

### Catalogue

The shared master grocery catalogue uses:

```text
groceries catalogue import
groceries catalogue list
groceries catalogue show <item-id>
groceries catalogue add
groceries catalogue update <item-id>
groceries catalogue deactivate <item-id>
groceries catalogue validate
```

Catalogue identities are stable. Prefer `deactivate` over destructive deletion
because user shopping lists may reference catalogue IDs.

### Shopping list

Per-user shopping-list management uses:

```text
groceries list list
groceries list show --user <user-id>
groceries list create --user <user-id>
groceries list add --user <user-id> <item-id>
groceries list remove --user <user-id> <item-id>
groceries list update --user <user-id> <item-id>
groceries list clear --user <user-id>
groceries list export --user <user-id>
```

`list add` means adding a catalogue item to a shopping list. It must not mean
sending the list to Tesco or another external store.

### User

Application user/profile maintenance uses:

```text
groceries user list
groceries user show <user-id>
groceries user create <user-id>
groceries user update <user-id>
groceries user disable <user-id>
```

Prefer `disable` over destructive deletion where lists or historical data may
reference the user. Application identity and authentication credentials are
separate concerns.

### Store

Store configuration and adapter maintenance uses:

```text
groceries store list
groceries store show <store-id>
groceries store add <store-id>
groceries store update <store-id>
groceries store disable <store-id>
groceries store test <store-id>
```

Tesco is the first store integration but must not define the application domain.
The store boundary should permit additional adapters such as Sainsbury's, Asda,
or Ocado later without changing catalogue or shopping-list semantics.

### Basket

Moving a user's shopping list towards an external store basket is a separate
workflow:

```text
groceries basket preview --user <user-id> --store <store-id>
groceries basket add --user <user-id> --store <store-id>
```

`basket preview` is the safe-by-default view of the intended external actions.
`basket add` performs the confirmed external-store action where supported.
Authentication, payment, and checkout remain outside the application unless a
future ADR explicitly changes that boundary.

### Server

Local web-application operation uses:

```text
groceries server run
```

Development options may include host and port values. Production process
management remains a deployment concern rather than a reason to expand the
server command unnecessarily.

### System

Cross-cutting application diagnostics and integrity checks use:

```text
groceries system status
groceries system validate
```

These commands may report or validate catalogue storage, user records,
shopping-list references, store configuration, and other application-level
state without absorbing domain-specific maintenance actions.

## Naming principles

1. Objects represent stable domain concepts, not modules or implementation
   technologies.
2. Actions should use consistent verbs across objects where the semantics are
   genuinely the same.
3. Use `show` for one identified record and `list` for collections.
4. Prefer reversible lifecycle actions such as `deactivate` and `disable` over
   destructive deletion when stable references may exist.
5. External-store actions belong under `basket` or `store`, not under `list` or
   `catalogue`.
6. All mutating CLI commands remain subject to OMP safe-by-default behaviour and
   explicit confirmation where required.

## Consequences

### Positive

- Requirement 003 can use `list add` naturally for list maintenance.
- Store integrations remain replaceable and do not leak into the catalogue
  domain.
- The CLI and future web application can share the same domain services.
- New stores can be introduced without redefining shopping-list commands.
- Safe preview of external basket changes has a clear home.
- Later agents have a stable vocabulary instead of inventing command structures
  increment by increment.

### Negative

- The current meaning of `groceries list add` must change before it becomes a
  stable public interface.
- `groceries list list` is slightly repetitive, but it preserves a consistent
  object/action grammar.
- Some actions listed here will not exist until later requirements are
  implemented.

## Deferred concepts

A future `product` object may be introduced if the application needs to model
store-specific purchasable products separately from generic catalogue items.
For example, a generic catalogue item such as "Semi Skimmed Milk" may map to
multiple Tesco or Sainsbury's product SKUs.

If that model is introduced, store-specific preferred products and substitution
rules should belong to the store-product relationship rather than the shared
catalogue item. This ADR does not introduce the `product` object yet.

## Alternatives considered

### Keep Tesco actions under `list`

Rejected because Requirement 003 makes `list` a first-class user-owned shopping
list. Sending a list to a store is a different concern and would make `list add`
ambiguous.

### Make Tesco a top-level object

Rejected because Tesco is one store implementation, not a stable application
domain concept. Use `store` and `basket` instead.

### Use implementation-oriented objects

Commands based on `json`, `playwright`, `fastapi`, or storage modules were
rejected because implementation choices may change while the domain concepts
remain stable.

## Related requirements and decisions

- [002 — Grocery Catalogue](../requirements/features/002-groceryCatalogue.md)
- [003 — User Shopping Lists](../requirements/features/003-userShoppingLists.md)
- [004 — Grocery Web Application](../requirements/features/004-groceryWebApplication.md)
- [005 — Tesco Integration](../requirements/features/005-tescoIntegration.md)
- [006 — Authentication and User Isolation](../requirements/features/006-authentication.md)
- [007 — Production Deployment](../requirements/features/007-deployment.md)
- [ADR-001 — Web Application Architecture](001-webApplicationArchitecture.md)
- [ADR-002 — Grocery Catalogue Schema](002-groceryCatalogueSchema.md)
