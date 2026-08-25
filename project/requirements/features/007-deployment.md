# 007 — Production Deployment

**Status:** ToDo

## Objective

Deploy organiseMyGroceries as a secure, maintainable Internet-accessible service on the selected 123-reg hosting environment, with HTTPS, repeatable installation, service management, configuration/secrets handling, persistence/backups, logging, and clean-room acceptance evidence.

Deployment must prove the real production composition rather than only proving individual application components in tests.

## Preconditions

* Requirements 003 and 004 must provide the persistent user-list and web application workflows.
* Requirement 006 authentication/user isolation must be complete before public Internet exposure.
* The exact 123-reg hosting product and its capabilities must be confirmed before implementation. Do not assume shared hosting supports the same process/service model as a Linux VPS.
* Any hosting-specific architectural decision that materially changes ADR-001 must be recorded before deployment.

## Requirements

### Deployment target

* Document the selected 123-reg hosting product, operating system/runtime, domain/subdomain, and relevant resource constraints.
* Prefer a Linux environment where the Python application can run as a managed service.
* Production deployment must not depend on a developer's home directory, Conda environment, interactive shell, or manually started terminal process.
* Application files, persistent data, configuration, logs, and deployment tooling must have clearly documented locations.

### Application service

* Run the FastAPI application using a production-suitable ASGI process configuration.
* The application process must be managed by the hosting environment or a service manager so it can start/restart without an interactive login.
* Service configuration must specify the production working directory, Python environment, application entry point, and required environment/configuration.
* A service restart must not lose persisted catalogue, user, or shopping-list data.
* Development reload/debug modes must not be enabled in production.

### Reverse proxy and HTTPS

* Public HTTP traffic must be served through the hosting platform/reverse proxy appropriate to the selected environment.
* HTTPS is mandatory for authenticated production use.
* HTTP requests should redirect to HTTPS where supported.
* TLS certificate issuance and renewal must be documented and preferably automated.
* Reverse-proxy forwarding/header configuration must be explicit so the application can correctly determine secure requests and client-facing URLs.
* Direct access to an internal application port should not be publicly exposed when a reverse proxy is used.

### Configuration and secrets

* Environment-specific configuration must be external to source control.
* Authentication/session secret keys must be generated for production and must not use repository examples/defaults.
* Secrets must not appear in committed `.env` files, documentation examples containing real values, normal logs, or test fixtures.
* Provide an example/template describing required configuration names without real secrets.
* Startup must fail clearly when mandatory production configuration is missing.

### Persistent storage

* Identify all production-persistent data and keep it outside disposable deployment/build artefacts.
* Application upgrades/redeployments must not overwrite production user lists or catalogue enrichment.
* The storage mechanism must be safe for the expected concurrent web workload.
* If JSON persistence is no longer safe for concurrent production writes, migrate to SQLite or another approved persistence mechanism before public deployment and record the decision.
* File/database ownership and permissions must restrict access to the application/service account and authorised administrators.

### Backup and restore

* Define what data is backed up, backup frequency, retention, and storage location.
* Backups containing user data must be protected appropriately.
* Provide and test a restore procedure.
* A backup is not considered sufficient until restoration has been demonstrated against representative data.
* Deployment/release instructions must identify when a pre-upgrade backup is required.

### Logging and diagnostics

* Production logs must provide enough information to diagnose startup, authentication, persistence, and store-adapter failures without exposing credentials/session secrets.
* Document how to inspect application/service and reverse-proxy logs.
* Establish a simple health/status mechanism suitable for confirming the application is running.
* The ADR-003 `groceries system status` / `groceries system validate` commands should be used or implemented where useful for operational verification.
* Log retention/rotation must prevent uncontrolled disk growth.

### Deployment and upgrade process

* Provide a repeatable documented process for initial deployment from a clean host/account.
* Pin or otherwise control Python/application dependencies sufficiently for repeatable deployment.
* Production upgrades must be deployable from a known repository revision/release.
* Document service stop/start/restart and rollback steps.
* Deployment should separate application release artefacts from persistent data/configuration.
* Avoid manual production edits to tracked source files.

### Security

* Public deployment must enforce Requirement 006 authentication and user isolation.
* Run the application with the minimum practical operating-system permissions; do not run the web application as root where avoidable.
* Expose only required network services/ports.
* Keep the host/runtime and relevant dependencies maintainable and updateable.
* Production error pages/responses must not expose stack traces, secrets, filesystem paths, or debug information to normal users.
* Tesco/store credentials and payment data must not be introduced as part of deployment configuration.

## Testing and acceptance evidence

Testing must follow the repository testing-process guidance. In particular, unit/code coverage alone is not proof of deployment completeness.

### Automated checks

* Run the complete application test suite against the release candidate.
* Validate production configuration parsing and missing-secret failure paths.
* Test persistence across application/service restart.
* Test authentication/authorisation using the production-style application composition.
* Test health/status behaviour.

### Clean-room deployment

Perform a clean deployment using only repository/release documentation and declared external secrets/configuration.

The acceptance run must demonstrate at minimum:

1. application installation from a clean environment;
2. production service starts successfully;
3. HTTPS access works through the real reverse proxy/domain path;
4. unauthenticated users cannot access private shopping lists;
5. two authenticated users remain isolated;
6. catalogue and shopping-list data survive a service restart;
7. a store/basket preview can be generated through the deployed application where Requirement 005 is available;
8. logs can be inspected without exposing secrets;
9. backup creation and representative restore succeeds;
10. the service can be restarted/redeployed using the documented process.

Capture sufficient command/output or other evidence to show that the real production path was exercised.

## Acceptance criteria

* organiseMyGroceries is reachable through its intended HTTPS URL on the selected 123-reg environment.
* The application runs as a managed production service rather than an interactive development process.
* Authentication and user isolation operate correctly through the deployed public path.
* Persistent application data survives restart and redeployment.
* Production secrets are external to source control and mandatory-secret failures are safe and explicit.
* Reverse proxy/TLS configuration is documented and reproducible.
* Backup and restore have both been demonstrated.
* Operational logs/status information are documented and do not expose sensitive data.
* A clean-room deployment from the documented instructions succeeds.
* Deployment evidence proves the composed production workflow, not merely isolated unit tests.

## Out of scope

* High-availability clustering.
* Multi-region deployment.
* Kubernetes/container orchestration unless required by the selected hosting product and separately approved.
* Automated Tesco checkout/payment.
* Enterprise monitoring/alerting platforms unless separately required.

## Documentation deliverables

* Production deployment guide.
* Required configuration/secrets reference using placeholder values only.
* Service/reverse-proxy configuration or reproducible templates where applicable.
* Backup and restore procedure.
* Upgrade/rollback procedure.
* Clean-room acceptance record/evidence.

## Related requirements

* Requirement 004 — Grocery Web Application
* Requirement 005 — Store Integration
* Requirement 006 — Authentication and User Isolation
* ADR-001 — Web Application Architecture
* ADR-003 — Command Line Object Model
