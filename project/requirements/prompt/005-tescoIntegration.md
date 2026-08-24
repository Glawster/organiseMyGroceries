# 005: Tesco Integration prompt

## Assignment

Requirement: 005 — `project/requirements/features/005-tescoIntegration.md`

Role: implement, test, and document the Tesco UK integration boundary.

Read the requirement, ADR-001, and all applicable repository instructions before changing anything. The initial integration is user-controlled search/click-through. Do not expand scope into automated authentication, payment, or checkout.

## Implementation guidance

- Generate Tesco UK grocery search URLs from catalogue `tescoSearch` values using correct URL encoding.
- Keep Tesco-specific URL/browser behaviour behind a dedicated service/boundary.
- Present searches for selected items in a controlled way; do not automatically open large numbers of tabs.
- Preserve preview/safe-by-default behaviour for any CLI/browser action.
- Do not store Tesco credentials, cookies, payment information, or checkout state.
- Treat Tesco HTML/selectors and other external behaviour as volatile dependencies.
- Prefer deterministic URL-generation tests over brittle browser tests where URL generation is sufficient.
- Where real browser integration remains, include production-path evidence that the real integration boundary has been exercised.

## Verification

- Run the complete pytest suite.
- Test URL encoding for spaces, punctuation, `%`, `&`, and representative product names.
- Verify only selected/active items are offered for Tesco searching.
- Verify no checkout, payment, or credential automation is introduced.
- Exercise at least one real Tesco search through the supported production path where practical.

## Handoff

Report changed areas, acceptance evidence, commands and results, external Tesco assumptions, production-path evidence, residual risks, and unresolved items.
