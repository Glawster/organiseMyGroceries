# Current increment

## Objective

Align the existing application with the OMP release 0.5 agent, repository,
requirements, and testing guidance.

## Scope

- Separate list logic, browser integration, and CLI orchestration.
- Make preview mode side-effect free.
- Validate inputs and contain generated output.
- Add maintained product and contributor documentation.
- Add unit and production-path tests with branch coverage.

## Status

Completed on 2026-08-24. See requirement
[001](requirements/features/001-alignAgentInstructions.md) and the
[audit review](reviews/2026-08-24-agentInstructionAudit.md).

## Verification

```bash
pytest
black --check main.py src tests
python main.py --help
python main.py add --help
python main.py export --help
```
