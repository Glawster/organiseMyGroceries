# Agent-instruction audit — 2026-08-24

## Scope

The repository was reviewed against `.github/agent-instructions.md`,
`.github/repositoryLayout.md`, `.github/requirementsManagement.md`, and
`documentation/testingProcess.md` from OMP release 0.5.

## Findings and disposition

| Area | Initial finding | Disposition |
| --- | --- | --- |
| Architecture | Domain, persistence, CLI, and Playwright lived in `main.py`. | Split into entry point, list core, and Tesco adapter. |
| Safe execution | Dry-run opened an interactive browser. | Preview now validates and counts only. |
| Paths | Inputs were not validated and generated files were siblings of sources. | Validate paths and confine artifacts to `output/`. |
| CLI | Unrelated top-level flags obscured actions. | Added discoverable `add` and `export` subcommands. |
| Environment | No Conda or package metadata existed. | Added `environment.yml` and `pyproject.toml`. |
| Documentation | README held all guidance and did not index living guides. | Added linked user, architecture, and security guides. |
| Requirements | No durable requirement or delivery traceability existed. | Added requirement 001, prompt, and index. |
| Tests | Tests imported the entry point dynamically and did not cover failures or safe orchestration. | Added mirrored unit and production-path tests with branch coverage. |
| Naming guidance | A legacy Copilot file contradicted the new test naming rule. | Removed it and added aligned project instructions. |

## Residual risks

Live Tesco behaviour cannot be tested reliably without an authenticated account
and would risk modifying a real basket. The browser boundary therefore remains
a manual acceptance check. Its selectors and first-result policy should be
reviewed before a future release.
