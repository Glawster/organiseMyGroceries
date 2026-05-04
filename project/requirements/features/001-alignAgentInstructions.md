# 001: Align agent instructions

## Status

Completed

## Outcome

As a maintainer, I need the repository aligned with the uploaded OMP 0.5
instructions so that application behaviour is safe, testable, documented, and
easy to extend.

## Context

The original implementation combined CLI, file transformation, and Playwright
automation. Its preview opened a browser, generated files escaped the approved
output boundary, and the repository lacked current environment and project
records.

## Scope

- Audit the repository against all applicable uploaded instructions.
- Rearrange code along responsibility boundaries.
- Add current environment, product, architecture, privacy, and audit records.
- Add automated evidence for core and critical preview/export paths.

## Out of scope

- Automating Tesco authentication, payment, or order submission.
- Live authenticated Tesco tests.
- Changing the user's shopping-list content.

## Acceptance criteria

1. Given a preview add command, when a valid source is loaded, then no browser
   opens and no file is written.
2. Given confirmed conversion or export, when output is written, then it is
   beneath the root `output/` directory and the source is preserved.
3. Given invalid input, when the CLI runs, then it reports failure with a
   non-zero status.
4. Given a contributor enters the repository, when they follow the README,
   then they can discover every living guide and create the supported Conda
   environment.
5. Given the automated suite runs, then core branch coverage exceeds 90% and a
   real CLI-to-list preview path is exercised.

## Dependencies and decisions

- OMP release 0.5 managed instructions.
- Architecture decision: not required; the separation follows mandatory
  repository guidance.

## Verification

- `pytest`
- `black --check main.py src tests`
- CLI help checks listed in `project/currentIncrement.md`
- Manual audit recorded in `project/reviews/2026-08-24-agentInstructionAudit.md`

## Traceability

- Implementation: `main.py`, `src/organiseMyGroceries/`
- Tests: `tests/test_main.py`, `tests/test_shoppingList.py`
- Documentation: `README.md`, `documentation/architecture.md`,
  `documentation/securityModel.md`, `documentation/userGuide.md`
- Pull request: None (local maintainer-requested change)
- Agent runs: 2026-08-24 Codex implementation and verification run using
  `project/requirements/prompt/001-alignAgentInstructions.md`

## Change history

- 2026-08-24: created and completed from the maintainer's repository-audit
  request.
