# 004 — Grocery Web Application

**Status:** ToDo

## Objective

Provide a simple browser-based interface so users in different physical locations can manage their own grocery lists.

## Requirements

* Implement a Python web application.
* Use FastAPI for the initial implementation.
* Use server-rendered HTML/Jinja templates.
* Do not introduce React or another client-side application framework without a later architectural decision.
* Provide a home page/profile selection mechanism.
* Provide a shopping-list page for each user.
* Allow users to:

  * browse catalogue items
  * select/unselect groceries
  * change quantities
  * enter notes
  * save changes
* Design for desktop and mobile browsers.
* Keep core catalogue and shopping-list behaviour outside FastAPI/Jinja code.
* UI code orchestrates domain services rather than implementing business rules.

## Initial authentication scope

Profile selection is sufficient for the first local/prototype version.

Production deployment must not rely on profile selection alone; authentication is covered separately.

## Acceptance criteria

* Application can be started locally.
* Browser can display the catalogue.
* A user can modify and save their shopping list.
* Reloading the page restores saved state.
* Different profiles display their own lists.
* Core functionality has automated tests that do not require a browser.
