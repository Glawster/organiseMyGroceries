# 002: Grocery Catalogue prompt

## Assignment

Requirement: 002 — `project/requirements/features/002-groceryCatalogue.md`

Role: implement, test, and document the persistent shared grocery catalogue and its import path.

Read the requirement and all applicable repository instructions before changing anything. Preserve the catalogue as shared product data rather than user-specific list state. Reuse existing list parsing and validation behaviour where it is suitable instead of duplicating it.

## Implementation guidance

- Keep catalogue parsing, validation, stable-ID assignment, and persistence outside UI/browser code.
- Provide the repeatable text-to-catalogue conversion required by the requirement.
- Preserve stable identifiers when the import is re-run against an existing catalogue.
- Detect duplicates explicitly; do not silently discard ambiguous entries.
- Keep real user shopping data out of version control. Test with safe fixtures.
- Follow the repository layout and OMP CLI safe-by-default rules for any maintainer script or command.
- Update maintained documentation when behaviour or data formats become durable.

## Verification

- Run the complete pytest suite.
- Run formatting/static checks required by the repository.
- Exercise a clean text import into temporary/test data.
- Re-run the import and demonstrate stable identifiers are preserved.
- Demonstrate duplicate and invalid-input behaviour.

## Handoff

Report changed areas, acceptance-criterion evidence, commands and results, catalogue schema decisions, assumptions, residual risks, and unresolved items.
