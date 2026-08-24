# 006: Authentication and User Isolation prompt

## Assignment

Requirement: 006 — `project/requirements/features/006-authentication.md`

Role: design, implement, test, and document production-grade application authentication and user isolation before Internet deployment.

Read requirements 003 and 004, ADR-001, the security documentation, and all applicable repository instructions before changing anything. Profile selection from the prototype is not authentication.

## Implementation guidance

- Require authenticated identity for production user-list access.
- Ensure users cannot read or modify another user's shopping-list data by changing URLs, form fields, IDs, or requests.
- Use established password hashing/session mechanisms; never store plaintext passwords.
- Keep secrets in environment/configuration mechanisms appropriate to deployment and out of version control.
- Apply secure cookie/session defaults suitable for HTTPS production deployment.
- Include logout and session-expiry behaviour.
- Do not store Tesco credentials, payment details, or Tesco authenticated session data.
- Avoid inventing custom cryptography or authentication protocols.
- Update the security/privacy model and user documentation.

## Verification

- Run the complete pytest suite.
- Test successful and failed authentication.
- Test unauthenticated access to protected resources.
- Test cross-user access attempts at service and HTTP boundaries.
- Test logout/session invalidation.
- Verify no secrets or password material are written to logs or committed fixtures.

## Handoff

Report changed areas, acceptance evidence, commands and results, security decisions, threat cases tested, assumptions, residual risks, and unresolved items.
