# Requirements

Next available number: 008

## ToDo

| Req ID | Requirement | Description | Agent Prompt | Architecture Decisions |
| --- | --- | --- | --- | --- |
| 002 | [Grocery Catalogue](features/002-groceryCatalogue.md) | Create the persistent shared catalogue and repeatable import path. | [Prompt](prompt/002-groceryCatalogue.md) | [ADR-001](../adr/001-webApplicatinArchitecture.md) |
| 003 | [User Shopping Lists](features/003-userShoppingLists.md) | Maintain independent per-user lists over the shared catalogue. | [Prompt](prompt/003-userShoppingLists.md) | [ADR-001](../adr/001-webApplicationArchitecture.md) |
| 004 | [Grocery Web Application](features/004-groceryWebApplication.md) | Provide the browser application for remote users. | [Prompt](prompt/004-groceryWebApplication.md) | [ADR-001](../adr/001-webApplicationArchitecture.md) |
| 005 | [Tesco Integration](features/005-tescoIntegration.md) | Keep Tesco search/click-through behind a controlled external boundary. | [Prompt](prompt/005-tescoIntegration.md) | [ADR-001](../adr/001-webApplicationArchitecture.md) |
| 006 | [Authentication and User Isolation](features/006-authentication.md) | Protect Internet-accessible profiles and user data. | [Prompt](prompt/006-authentication.md) | [ADR-001](../adr/001-webApplicationArchitecture.md) |
| 007 | [Production Deployment](features/007-deployment.md) | Deploy securely to the selected 123-reg hosting environment. | [Prompt](prompt/007-deployment.md) | [ADR-001](../adr/001-webApplicationArchitecture.md) |

## In Progress

None.

## Completed

| Req ID | Requirement | Description | Agent Prompt | Architecture Decisions |
| --- | --- | --- | --- | --- |
| 001 | [Align agent instructions](features/001-alignAgentInstructions.md) | Align structure, safety, documentation, and tests with OMP 0.5. | [Prompt](prompt/001-alignAgentInstructions.md) | Not required |
| 002 | [Grocery Catalogue](features/002-groceryCatalogue.md) | Create the persistent shared catalogue and repeatable import path. | [Prompt](prompt/002-groceryCatalogue.md) | [ADR-001](../adr/001-webApplicatinArchitecture.md), [ADR-002](../adr/002-groceryCatalogueSchema.md) |

## Sequencing

The expected dependency order is 002 → 003 → 004 → 005/006 → 007. Requirements 005 and 006 may be developed independently once the web application boundaries from 004 are stable, but production deployment in 007 depends on authentication/user isolation being complete.
