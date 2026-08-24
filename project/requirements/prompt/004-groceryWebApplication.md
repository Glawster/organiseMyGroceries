# 004: Grocery Web Application prompt

## Assignment

Requirement: 004 — `project/requirements/features/004-groceryWebApplication.md`

Role: implement, test, and document the browser-based application over the catalogue and user-list services.

Read requirements 002 and 003, ADR-001, and all applicable repository instructions before changing anything. Treat the web layer as orchestration: do not move catalogue or shopping-list business rules into routes or templates.

## Implementation guidance

- Use FastAPI and server-rendered Jinja templates as decided in ADR-001.
- Keep the first implementation deliberately small and mobile-friendly.
- Provide profile selection for prototype use and clearly distinguish it from production authentication.
- Support catalogue browsing, item selection, quantity, notes, save, and reload.
- Keep HTML/CSS accessible and usable on desktop and mobile browsers.
- Do not introduce React or another SPA framework.
- Keep Tesco-specific integration behind its own boundary; requirement 005 owns Tesco search behaviour.
- Update user and architecture documentation to match implemented behaviour.

## Verification

- Run the complete pytest suite.
- Add route/component tests using the real application composition where practical.
- Verify catalogue/list core tests still run without FastAPI or a browser.
- Exercise the application locally through the production application entry path.
- Verify independent profiles reload their own saved state.
- Check the principal workflow at a narrow/mobile viewport as well as desktop size.

## Handoff

Report changed areas, acceptance-criterion evidence, commands and results, screenshots or other UI evidence where useful, assumptions, residual risks, and unresolved items.
