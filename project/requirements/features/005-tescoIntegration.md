# 005 — Store Integration

**Status:** ToDo

## Objective

Provide a store-neutral integration boundary that can translate a user's shopping list into reviewed actions for an external grocery store. Tesco UK is the first store adapter, but catalogue and shopping-list behaviour must not depend on Tesco-specific concepts.

The initial integration remains user-controlled: organiseMyGroceries prepares and previews store actions, while authentication, product choice, payment, substitution decisions, and checkout remain with the user on the store website.

## Requirements

### Store model

* Treat a grocery store as a first-class application object.
* Each configured store must have a stable store identifier, display name, enabled/disabled state, and the configuration required by its adapter.
* Tesco UK must be provided as the first supported store.
* Store-specific behaviour must remain behind a store adapter/service boundary.
* Catalogue and user shopping-list services must remain usable when no store is configured.
* Adding another store must not require changing catalogue or shopping-list schemas.

### Store maintenance

Support the command vocabulary defined by ADR-003 where applicable:

```text
groceries store list
groceries store show <store>
groceries store add <store>
groceries store update <store>
groceries store disable <store>
groceries store test <store>
```

* `store test` must validate configuration without modifying a shopping list or external basket.
* Disabling a store must preserve its identity/configuration for existing references unless an explicit migration is performed.
* Invalid or incomplete store configuration must fail clearly rather than silently falling back to Tesco.

### Basket boundary

Store submission must use the `basket` object rather than overloading shopping-list commands:

```text
groceries basket preview --user <user> --store <store>
groceries basket add --user <user> --store <store>
```

* `basket preview` must be safe by default and must not modify an external basket.
* Preview must identify the user list, target store, selected items, quantities where relevant, and the store action/search that would be attempted.
* `basket add` is the explicit action that may interact with the external store.
* A shopping-list `add` command means adding a catalogue item to a user's list; it must not mean sending a list to Tesco.
* External-store failures must not modify the persisted user shopping list.

### Tesco adapter

* Generate correctly URL-encoded Tesco UK grocery searches from catalogue/store search terms.
* Prefer a store-specific product/search term when one is available; otherwise use the catalogue search term/display name according to documented fallback rules.
* Do not assume the first Tesco search result is the correct product without an explicit product-matching rule or user confirmation.
* Do not automate checkout in this increment.
* Do not store Tesco usernames, passwords, payment details, cookies, or other reusable Tesco credentials in catalogue or shopping-list data.
* If browser automation is retained, Tesco-specific browser automation must remain isolated from core domain services.

### Product identity boundary

* A catalogue item represents the application's grocery concept and is not the same thing as a store product/SKU.
* Do not place Tesco-specific product identifiers directly into the shared catalogue schema unless a later ADR explicitly changes this decision.
* The design must allow a future store-product mapping layer, including preferred products and substitutions, without changing stable catalogue IDs.

## Safety and failure behaviour

* Preview before external mutation must be supported.
* No external basket mutation may happen merely by listing, showing, editing, or saving a shopping list.
* Network/store failures must produce actionable errors and leave local persisted state valid.
* The application must never claim that an item was added to an external basket unless the adapter has evidence that the action succeeded.
* Store integrations must not log credentials or sensitive session data.

## Testing requirements

* Unit-test URL/search generation and adapter selection without network access.
* Boundary-test store configuration validation.
* Test that catalogue and shopping-list services have no Tesco dependency.
* Test that preview performs no external mutation.
* Test failure paths, including disabled stores, invalid configuration, unavailable adapters, and external action failures.
* Use fakes/mocks for consumer behaviour, but keep a clearly identified real-adapter/manual acceptance path for proving Tesco integration when appropriate.
* Tests must not require or contain real Tesco credentials.

## Acceptance criteria

* Tesco exists as a configured store behind the common store boundary.
* `groceries store list` and `groceries store show tesco` expose the configured store without requiring browser automation.
* A user's selected shopping-list items can be converted into a Tesco basket preview with correctly encoded searches.
* Preview causes no external basket changes.
* An explicit basket action can hand off to the Tesco adapter without modifying the source shopping list.
* Core catalogue/list tests run successfully with the Tesco adapter unavailable.
* No Tesco authentication, payment, or checkout data is persisted by the application.
* The design can accommodate a second store without changing catalogue or user-list schemas.

## Out of scope

* Automated payment or checkout.
* Capturing Tesco credentials.
* Price comparison between stores.
* Automatic substitution decisions.
* A complete store-product/SKU catalogue.
* Guaranteed product matching from arbitrary Tesco search results.

## Related decisions and requirements

* Requirement 002 — Grocery Catalogue
* Requirement 003 — User Shopping Lists
* Requirement 004 — Grocery Web Application
* ADR-003 — Command Line Object Model
