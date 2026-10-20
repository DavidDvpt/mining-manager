<!-- nx configuration start-->
<!-- Leave the start & end comments to automatically receive updates. -->

# General Guidelines for working with Nx

- For navigating/exploring the workspace, invoke the `nx-workspace` skill first - it has patterns for querying projects, targets, and dependencies
- When running tasks (for example build, lint, test, e2e, etc.), always prefer running the task through `nx` (i.e. `nx run`, `nx run-many`, `nx affected`) instead of using the underlying tooling directly
- Prefix nx commands with the workspace's package manager (e.g., `pnpm nx build`, `npm exec nx test`) - avoids using globally installed CLI
- You have access to the Nx MCP server and its tools, use them to help the user
- For Nx plugin best practices, check `node_modules/@nx/<plugin>/PLUGIN.md`. Not all plugins have this file - proceed without it if unavailable.
- NEVER guess CLI flags - always check nx_docs or `--help` first when unsure

## Scaffolding & Generators

- For scaffolding tasks (creating apps, libs, project structure, setup), ALWAYS invoke the `nx-generate` skill FIRST before exploring or calling MCP tools

## When to use nx_docs

- USE for: advanced config options, unfamiliar flags, migration guides, plugin configuration, edge cases
- DON'T USE for: basic generator syntax (`nx g @nx/react:app`), standard commands, things you already know
- The `nx-generate` skill handles generator discovery internally - don't call nx_docs just to look up generator syntax

<!-- nx configuration end-->

# Repository Architecture

## Backend API layering

The main backend API lives in `apps/api` and is organized into three layers:

- **Controllers**: HTTP/API boundary. They handle request parsing, authentication and authorization checks, access control, response serialization, and HTTP-specific errors. They must not contain business logic.
- **Services**: business layer. All business rules, use cases, orchestration, and business validations belong here. Services may call repositories but must not depend on HTTP framework details. Each service has a strict business-domain scope and must not take over another service's responsibilities. For example, the session service must never manage session lines; it must delegate that work to the dedicated session-line service.
- **Repositories**: persistence layer. They contain only database-related concerns, including PostgreSQL queries, persistence mapping, and database transactions. They must not contain business rules.

The dependency direction is:

```text
controller -> service -> repository -> PostgreSQL
```

Do not reverse these dependencies. Controllers should not access the database directly, repositories should not decide business behavior, and services should remain independent from HTTP concerns. A cross-domain workflow must use the service responsible for each domain and must never bypass it by calling its repository directly.

## Database migrations

Database migrations use a zero-padded incremental numeric prefix:

- `000_<description>` is the initial database schema migration.
- Later migrations increment the prefix: `001_<description>`, `002_<description>`, and so on.

Migration numbers must be unique, strictly incremental, and must never be reused. The descriptive suffix should briefly state the schema change.
