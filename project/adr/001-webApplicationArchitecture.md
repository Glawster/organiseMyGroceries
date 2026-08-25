# ADR-001 - Web Application Architecture

## Constraints

Tesco’s groceries site accepts ordinary browser sessions but rejects Playwright-controlled sessions after the cookie-consent interaction. Manual login inside a Playwright-launched browser is therefore not a viable authentication approach.
