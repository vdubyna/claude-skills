---
name: py-ddd-init
description: >
  Initialize a production-ready Python DDD project with FastAPI. Use when user
  says "/py-ddd-init", "init ddd project", "create new python ddd project",
  "scaffold ddd", or asks to start a new Python project with domain-driven design.
  Creates full project structure with layered architecture (domain, application,
  infrastructure, presentation), CLAUDE.md with DDD conventions, Docker setup,
  CI/CD, and all necessary configuration.
---

# py-ddd-init

Initialize a production-ready Python DDD project.

## Trigger

User says `/py-ddd-init <project-name>` or asks to create a new DDD Python project.

## Process

### Step 1: Collect project name

If not provided, ask for project name. Convert to snake_case for package name.
Default DB: PostgreSQL. Default framework: FastAPI.

### Step 2: Read conventions

Read `references/conventions.md` for DDD layer rules and naming conventions.
Read `references/claude-md-template.md` for the CLAUDE.md template.

### Step 3: Generate project

Run the init script:

```bash
python3 <skill_path>/scripts/init_project.py <project-name> --output <target-dir>
```

The script creates the full directory tree, all boilerplate files, and CLAUDE.md.

### Step 4: Post-init guidance

After generation, tell the user:

1. `cd <project-name> && uv sync` to install dependencies
2. `docker-compose up -d` to start Postgres
3. `uv run alembic upgrade head` to run migrations
4. `uv run uvicorn src.<pkg>.main:app --reload` to start dev server

Mention the companion skill:
- `py-ddd` — code generation, architecture design, review, and testing

### Project Structure

```
<project>/
├── CLAUDE.md                     # DDD conventions for Claude Code
├── pyproject.toml                # uv package config
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── src/
│   └── <package>/
│       ├── __init__.py
│       ├── main.py               # FastAPI app + lifespan
│       ├── config.py             # Pydantic Settings
│       ├── container.py          # Composition Root (manual DI)
│       ├── domain/               # PURE — no external imports
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── events/
│       │   ├── services/
│       │   └── exceptions.py
│       ├── application/          # Use cases, orchestration
│       │   ├── commands/
│       │   ├── queries/
│       │   ├── ports/            # Protocols (interfaces)
│       │   └── dto/
│       ├── infrastructure/       # Adapters — implements ports
│       │   ├── persistence/
│       │   │   ├── repositories/
│       │   │   ├── models/       # SQLAlchemy ORM models
│       │   │   ├── unit_of_work.py
│       │   │   └── database.py
│       │   └── external/         # External API clients
│       └── presentation/         # Thin — delegates to application
│           ├── api/v1/
│           ├── schemas/          # Pydantic request/response
│           └── dependencies.py   # FastAPI Depends wiring
├── tests/
│   ├── unit/domain/
│   ├── unit/application/
│   ├── integration/
│   ├── conftest.py
│   └── factories.py
└── docs/adr/
```

### Layer Dependency Rules

```
presentation → application → domain
infrastructure → application (implements ports)
domain → NOTHING (pure Python only)
```

Never allow: domain importing from infrastructure, SQLAlchemy in domain,
FastAPI in application, circular imports between bounded contexts.
