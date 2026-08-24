# 003: User Shopping Lists prompt

## Assignment

Requirement: 003 — `project/requirements/features/003-userShoppingLists.md`

Role: implement, test, and document independent per-user shopping lists over the shared catalogue.

Read requirement 002 as a dependency and read all applicable repository instructions before changing anything. Do not duplicate catalogue definitions into user data.

## Implementation guidance

- Model user-list state separately from catalogue state.
- Reference catalogue items by stable catalogue ID.
- Encapsulate persistence behind domain/service interfaces so JSON can later be replaced by SQLite without rewriting UI/domain workflows.
- Ensure one user's save operation cannot mutate another user's list.
- Define and test behaviour for missing, inactive, or removed catalogue references.
- Keep core list behaviour independent of FastAPI, Jinja, Playwright, or another UI/browser framework.
- Do not commit real user shopping data; use safe fixtures/examples.
- Update maintained documentation for the resulting list format and behaviour.

## Verification

- Run the complete pytest suite.
- Demonstrate two independent users can select different items from one catalogue.
- Demonstrate save/reload persistence.
- Test invalid catalogue references and inactive catalogue items.
- Verify the domain/service tests require no web server or browser.

## Handoff

Report changed areas, acceptance-criterion evidence, commands and results, persistence boundaries, assumptions, residual risks, and unresolved items.
