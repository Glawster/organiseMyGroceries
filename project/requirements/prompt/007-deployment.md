# 007: Production Deployment prompt

## Assignment

Requirement: 007 — `project/requirements/features/007-deployment.md`

Role: prepare, verify, and document a repeatable production deployment to the selected 123-reg Linux hosting environment.

Read requirement 006, ADR-001, the security model, and all applicable repository instructions before changing anything. Do not deploy an unauthenticated multi-user application to the public Internet.

## Implementation guidance

- Confirm the actual 123-reg hosting product/capabilities before choosing deployment commands; do not assume shared hosting and VPS capabilities are interchangeable.
- Run the Python application behind a production application service and reverse proxy where the hosting product permits it.
- Require HTTPS and document certificate renewal.
- Keep secrets and environment-specific configuration outside version control.
- Define persistent-data locations and backup/restore procedures for catalogue and user data.
- Ensure deployment survives process/server restart.
- Document initial deployment, upgrade, rollback, log inspection, backup, and restore.
- Keep development fixtures and real production user data separate.
- Do not automate Tesco authentication, payment, or checkout as part of deployment.

## Verification

- Run the complete automated test suite before deployment.
- Verify the production application starts from a clean deployment environment.
- Verify HTTPS, authentication, user isolation, restart persistence, and data persistence.
- Perform and document a backup/restore test.
- Record the deployed revision and relevant non-secret configuration.

## Handoff

Report changed areas, deployment target/capabilities, commands and results, clean-room deployment evidence, backup/restore evidence, assumptions, residual operational risks, and unresolved items.
