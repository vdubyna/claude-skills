# CLAUDE.md Template

This template is used by init_project.py to generate CLAUDE.md for new projects.
Variables: {project_name}, {package_name}

# CLAUDE.md

## Project: {project_name}

Python DDD project with FastAPI. Layered architecture with strict dependency rules.

## Commands

```bash
uv sync                                           # install deps
uv run uvicorn src.{package_name}.main:app --reload  # dev server
uv run pytest                                      # all tests
uv run pytest tests/unit -x                        # unit tests, stop on first fail
uv run pytest tests/integration                    # integration tests
uv run alembic upgrade head                        # run migrations
uv run alembic revision --autogenerate -m "msg"    # create migration
uv run ruff check src/ tests/                      # lint
uv run ruff format src/ tests/                     # format
uv run mypy src/                                   # type check
```

## Architecture: Layered DDD

```
presentation -> application -> domain <- infrastructure
```

### Layer Rules

**domain/** — PURE Python. No imports from other layers or third-party libs.
Uses only: dataclasses, uuid, datetime, typing, enum, abc.
Contains: entities, value objects, domain events, domain services, exceptions.

**application/** — Use cases. Imports domain only.
Defines Ports (typing.Protocol) that infrastructure implements.
Contains: commands, queries, command handlers, DTOs, ports.

**infrastructure/** — Implements ports. Imports domain + application + third-party.
Contains: SQLAlchemy repos, ORM models, external API clients, unit of work.

**presentation/** — Thin HTTP layer. Imports application + Pydantic schemas.
Contains: FastAPI routers, request/response schemas, dependency wiring.

### Dependency Injection

Manual Composition Root in `src/{package_name}/container.py`.
FastAPI dependencies in `src/{package_name}/presentation/dependencies.py`.

## Naming Conventions

- Entity: `Order`, `User` (PascalCase noun)
- Value Object: `Money`, `Email` (frozen dataclass)
- Domain Event: `OrderCreated`, `PaymentProcessed` (past tense)
- Command: `CreateOrder`, `ProcessPayment` (imperative)
- Port: `OrderRepository`, `LLMProvider` (Protocol)
- Infra impl: `SqlAlchemyOrderRepository`, `InMemoryOrderRepository`
- ORM Model: `OrderModel` (suffix Model)
- Schema: `CreateOrderRequest`, `OrderResponse` (suffix Request/Response)
- Handler: `handle_create_order` (function, not class)

## Patterns

- **Aggregate Root**: entity that owns consistency boundary, collects domain events
- **Repository**: one per aggregate root, defined as Protocol in application/ports/
- **Unit of Work**: wraps transaction, defined as Protocol in application/ports/
- **Command Handler**: one function per use case, receives command + dependencies
- **Composition Root**: container.py wires all concrete implementations

## Testing

- `tests/unit/domain/` — pure logic, no mocks needed, no DB
- `tests/unit/application/` — mock ports (repositories, external services)
- `tests/integration/` — real DB via testcontainers, real HTTP via httpx
- Use factory functions in `tests/factories.py`, not raw constructors
- Test domain behavior through aggregate methods, not by checking internal state

## Code Style

- Python 3.12+, type hints everywhere
- ruff for linting + formatting, mypy --strict for type checking
- Async by default for I/O operations
- Prefer dataclasses for domain, Pydantic for API schemas
- Max function length: ~20 lines. Max file length: ~150 lines.
- No comments that restate code. Docstrings for public APIs only.

## File Size Hints

- Entity: <100 lines
- Command handler: <50 lines
- Repository impl: <80 lines
- API endpoint function: <30 lines

## Anti-patterns to Avoid

- SQLAlchemy/Pydantic/FastAPI imports in domain layer
- Business logic in API endpoints or repositories
- Anemic domain model (entity with only data, no behavior)
- God service with 10+ methods (split into separate command handlers)
- Returning ORM models from repositories (return domain entities)
- Testing implementation details instead of behavior
