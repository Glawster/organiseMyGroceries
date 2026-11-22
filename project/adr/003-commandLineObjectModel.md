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
groceries list send --user <user-id> --store <store-id>
groceries list import --source <list>.txt
```

The shopping-list terminal UI is opened with the top-level option
`groceries --ui [<list>]` rather than an object/action pair, because it is an
interactive front end over the `list` actions rather than another action.
Without a list it opens a picker over the lists in `output/`.

Until users exist (006), a list is identified by name: `weekly` means
`output/weekly.json`, and an explicit path is still accepted.

`list add` means adding a catalogue item to a shopping list. It must not mean
sending the list to Tesco or another external store; that is `list send`.

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

### Sending a list to a store

Sending a user's shopping list to an external store basket is the `list send`
action:

```text
groceries list send --user <user-id> --store <store-id>
groceries list send --user <user-id> --store <store-id> --confirm
```

Without `--confirm`, `list send` is the safe-by-default preview of the intended
external actions. With `--confirm` it performs the external-store action where
supported. No other `list` action may interact with an external store.
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
5. Sending a list to an external store is `list send`; store configuration
   belongs under `store`. No other action may interact with an external store.
6. All mutating CLI commands remain subject to OMP safe-by-default behaviour and
   explicit confirmation where required.

## Consequences

### Positive

- Requirement 003 can use `list add` naturally for list maintenance.
- Store integrations remain replaceable and do not leak into the catalogue
  domain.
- The CLI and future web application can share the same domain services.
- New stores can be introduced without redefining shopping-list commands.
- Safe preview of external basket changes has a clear home in `list send`.
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

### Use `list add` to send a list to a store

Rejected because Requirement 003 makes `list` a first-class user-owned shopping
list, and `list add` naturally means adding a catalogue item to it. Using the
same verb for sending to a store would be ambiguous; `list send` is used instead.

### Separate `basket` object

Originally accepted (`basket preview` and `basket add`), then replaced by
`list send` on 2026-11-22. Sending acts on a user's list, so a separate object
added a concept to learn without adding behaviour, and preview is already the
default of every mutating command.

### Make Tesco a top-level object

Rejected because Tesco is one store implementation, not a stable application
domain concept. Use `store` and `list send` instead.

### Use implementation-oriented objects

Commands based on `json`, `playwright`, `fastapi`, or storage modules were
rejected because implementation choices may change while the domain concepts
remain stable.

## Amendments

- 2026-11-22: replaced `basket preview` and `basket add` with `list send`
  (preview by default, `--confirm` to send).
- 2026-11-22: added `list import` and the top-level `--ui` option that opens
  the shopping-list terminal UI (Requirement 003).
- 2026-11-22: lists are identified by name (`output/<name>.json`); `--ui`
  without a list opens a list picker; `list send` and `list export` require
  `--source`; `list import` accepts `--output NAME` (Requirement 003).

## Related requirements and decisions

- [002 — Grocery Catalogue](../requirements/features/002-groceryCatalogue.md)
- [003 — User Shopping Lists](../requirements/features/003-userShoppingLists.md)
- [004 — Grocery Web Application](../requirements/features/004-groceryWebApplication.md)
- [005 — Tesco Integration](../requirements/features/005-tescoIntegration.md)
- [006 — Authentication and User Isolation](../requirements/features/006-authentication.md)
- [007 — Production Deployment](../requirements/features/007-deployment.md)
- [ADR-001 — Web Application Architecture](001-webApplicationArchitecture.md)
- [ADR-002 — Grocery Catalogue Schema](002-groceryCatalogueSchema.md)
