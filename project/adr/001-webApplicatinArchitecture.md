# ADR-001 — Web Application Architecture

**Status:** Accepted

**Date:** 2026-08-24

## Context

organiseMyGroceries began as a local Python/Playwright workflow for turning a maintained grocery list into reviewed Tesco actions. The intended use now includes multiple family users in different physical locations, each maintaining an independent shopping list over a shared grocery catalogue.

A locally installed desktop/CLI-only application would require each user to install and maintain Python and application dependencies and would make shared catalogue management awkward. A centrally hosted browser application provides a simpler client experience while preserving Python as the implementation language.

The application also needs a clear boundary between durable grocery/list behaviour and volatile external Tesco integration. Production Internet access introduces authentication, user-isolation, configuration, backup, and deployment concerns that must not be mixed into the core domain model.

## Decision

1. The multi-user product will be a centrally hosted Python web application.
2. FastAPI will provide the initial HTTP/application layer.
3. HTML will be server-rendered with Jinja templates and plain CSS. A SPA framework such as React is not part of the initial architecture.
4. Catalogue and user-shopping-list business logic will remain framework-independent and testable without FastAPI, Jinja, Playwright, or a browser.
5. A shared grocery catalogue will be distinct from per-user shopping-list state. User lists reference stable catalogue identifiers.
6. Persistence will initially use JSON behind service/storage boundaries. The design must permit migration to SQLite or another suitable store without rewriting the domain or web UI workflows.
7. Tesco integration will remain an external boundary. The first web implementation generates user-controlled Tesco UK search links/actions and does not automate Tesco authentication, payment, or checkout.
8. Prototype profile selection may be used during local development, but public deployment requires proper authentication and enforced user isolation.
9. Production hosting is intended for 123-reg. The exact deployment topology must be confirmed against the purchased 123-reg product before implementation; the architecture must not assume VPS capabilities when only shared hosting is available.
10. Secrets, real user data, Tesco credentials, payment data, and authenticated Tesco session data must not be committed to the repository.

## Consequences

### Positive

- Users need only a modern browser; no local Python installation is required.
- Shared catalogue behaviour has one authoritative server-side implementation.
- Independent user lists can be accessed from different locations and devices.
- Core behaviour remains easy to unit and integration test without the web framework.
- JSON keeps the initial implementation small while an explicit persistence boundary preserves a migration path.
- Tesco-specific changes can be contained without rewriting catalogue/list logic.

### Negative

- The project acquires server operation, HTTPS, authentication, backup, and security responsibilities.
- JSON persistence requires care around concurrent writes and may become unsuitable as usage grows.
- Public deployment cannot proceed safely until authentication/user isolation is implemented.
- Tesco remains an external dependency whose URLs, browser behaviour, or policies may change.

## Alternatives considered

### Local application on every user's computer

Rejected for the multi-location family use case because it creates installation, upgrade, data-sharing, and support overhead on each client device.

### Streamlit

Considered as a rapid UI option, but FastAPI plus server-rendered templates provides clearer separation between domain services, HTTP routes, templates, authentication, and future deployment concerns.

### React or another SPA

Deferred. The current interaction model does not justify the additional build/runtime complexity. It may be reconsidered through a future ADR if the UI becomes substantially more interactive.

### SQLite immediately

Deferred. JSON is sufficient for the first catalogue/list increments provided persistence is isolated behind a replaceable boundary. Concurrency or operational evidence may trigger a later storage ADR.

### Full Tesco basket/checkout automation

Rejected from the initial web architecture. The application should assist users in preparing and searching for groceries while Tesco retains control of authentication, product confirmation, basket, substitution, payment, and checkout workflows.

## Related requirements

- [002 — Grocery Catalogue](../requirements/features/002-groceryCatalogue.md) (schema: [ADR-002](002-groceryCatalogueSchema.md))
- [003 — User Shopping Lists](../requirements/features/003-userShoppingLists.md)
- [004 — Grocery Web Application](../requirements/features/004-groceryWebApplication.md)
- [005 — Tesco Integration](../requirements/features/005-tescoIntegration.md)
- [006 — Authentication and User Isolation](../requirements/features/006-authentication.md)
- [007 — Production Deployment](../requirements/features/007-deployment.md)
