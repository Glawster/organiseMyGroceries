# 003 — User Shopping Lists

**Status:** ToDo

## Objective

Allow multiple people to maintain independent shopping lists while sharing the common grocery catalogue.

## Requirements

* A user shopping list must reference catalogue items rather than duplicate the complete catalogue definition.
* Each user has an independent list.
* Changes to one user's selections must not affect another user's list.
* A user entry supports:

  * catalogue item ID
  * selected state
  * quantity
  * user-specific notes
* Users may select previously unused catalogue items.
* User data is persisted between sessions.
* JSON storage is acceptable initially.
* Storage design should permit later migration to SQLite without requiring the UI or domain model to be rewritten.

## Initial data model

```json
{
  "profile": "exampleUser",
  "displayName": "Example User",
  "items": [
    {
      "catalogueId": "item-001",
      "selected": true,
      "quantity": 1,
      "notes": ""
    }
  ]
}
```

## Acceptance criteria

* Two users can have different selections for the same catalogue.
* Saving one user cannot modify another user's data.
* Removing or deactivating a catalogue item is handled predictably when referenced by a user.
* List loading, modification and saving are testable independently of the web UI.
