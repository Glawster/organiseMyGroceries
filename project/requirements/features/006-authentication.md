# 006 — Authentication and User Isolation

**Status:** ToDo

## Objective

Introduce application authentication and enforce user isolation before organiseMyGroceries is exposed to the public Internet. A signed-in user must be able to access their own shopping data without gaining access to another user's private list through the UI, CLI-facing web services, or direct URL manipulation.

Store credentials, payment details, and external-store sessions remain outside the organiseMyGroceries user account model.

## Requirements

### Application users

* Use the application user/profile established by Requirement 003 as the owner of private shopping-list data.
* Each user must have a stable internal identity independent of display name.
* Display names and other mutable profile attributes must not be used as the sole ownership/security key.
* Disabled users must not be able to authenticate.
* Disabling a user must not silently delete their shopping-list data.

### Authentication

* Production web access must require authentication before private user data can be viewed or modified.
* Passwords, if used, must be stored only as modern salted password hashes; plaintext or reversibly encrypted passwords are prohibited.
* Authentication secrets and application secret keys must not be committed to the repository.
* Authentication failure messages must not unnecessarily disclose whether a username/account exists.
* Login must establish a server-verifiable authenticated session.
* Logout must invalidate or terminate the user's active application session as far as the selected session mechanism permits.
* Session cookies must use appropriate production security settings, including `HttpOnly`, `Secure` under HTTPS, and an appropriate `SameSite` policy.
* Session identifiers/secrets must not be written to normal application logs.

### Authorisation and isolation

* Authentication alone is not sufficient: every private-data operation must enforce ownership/authorisation.
* A user must not be able to access another user's shopping list by changing a URL, form value, request parameter, or client-side state.
* Server-side code must derive or validate the authorised user for every read/write operation involving private user data.
* Catalogue data may remain shared/readable according to application policy, but user selections, quantities, notes, and other private list state must remain isolated.
* Administrative operations, if introduced, must be explicitly distinguished from normal user permissions.
* The CLI `user` maintenance model from ADR-003 must not accidentally provide unauthenticated remote administration when exposed through the web application.

### User maintenance

The domain/service layer should support the ADR-003 vocabulary where applicable:

```text
groceries user list
groceries user show <user>
groceries user create <user>
groceries user update <user>
groceries user disable <user>
```

* User maintenance must operate on stable identities.
* Sensitive credential operations should be separated from ordinary profile updates where practical.
* Destructive deletion is not required in this increment; disable/preserve is preferred.

### External store separation

* organiseMyGroceries credentials are not Tesco or other store credentials.
* Do not store Tesco passwords, payment details, or reusable external-store authentication data in user profiles.
* Authentication to an external store remains a separate user-controlled process unless a later requirement and security review explicitly changes this boundary.

### Security controls

* State-changing web requests must have appropriate CSRF protection for the chosen form/session architecture.
* Redirect targets and return URLs must be validated to avoid open redirects.
* User-supplied text displayed in HTML must use Jinja/HTML escaping and must not be rendered as trusted markup by default.
* Authentication endpoints should support reasonable protection against repeated password guessing; the exact rate-limit mechanism may be selected during implementation/deployment.
* Secrets must be supplied through deployment configuration/environment or an equivalent secret mechanism.
* Production behaviour must fail safely when required authentication secrets are absent or invalid.

## Data and migration

* Existing prototype profiles/lists must have a documented migration path to authenticated users.
* Migration must preserve shopping-list ownership and stable catalogue references.
* Authentication implementation should remain behind services/interfaces sufficiently that moving user/list persistence from JSON to SQLite does not require rewriting web templates.
* If concurrent web writes make JSON persistence unsafe, migration to SQLite may be brought forward and recorded by ADR.

## Testing requirements

* Unit-test credential/password handling without using real passwords.
* Test successful and failed authentication paths.
* Test logout/session invalidation behaviour.
* Test disabled-user behaviour.
* Test direct attempts to access another user's list by identifier/URL manipulation.
* Test unauthenticated reads and writes to private endpoints.
* Test that shared catalogue access does not bypass private-list isolation.
* Test CSRF and relevant session-cookie configuration at the application boundary.
* Use fictional users and credentials only.
* Include a clean-room acceptance path demonstrating that a newly deployed instance cannot expose private lists without authentication.

## Acceptance criteria

* An unauthenticated visitor cannot view or modify a private shopping list.
* A valid user can authenticate and access their own list.
* A signed-in normal user cannot access another user's list by altering request data or URLs.
* Passwords are never stored in plaintext.
* Disabled users cannot authenticate, while their data remains intact.
* Logout ends the authenticated application session.
* Production session cookies are configured securely under HTTPS.
* Required secrets are absent from version control and documented for deployment.
* Tesco/store credentials and payment details are not stored by organiseMyGroceries.
* Automated tests prove both authentication and user-isolation boundaries.

## Out of scope

* Social/OAuth login unless separately approved.
* Tesco/store single sign-on.
* Storing payment methods.
* Fine-grained household sharing/roles beyond what is required for initial administration and user isolation.
* Password recovery by email unless separately specified.
* Multi-factor authentication unless separately specified.

## Related requirements

* Requirement 003 — User Shopping Lists
* Requirement 004 — Grocery Web Application
* Requirement 005 — Store Integration
* Requirement 007 — Production Deployment
* ADR-003 — Command Line Object Model
