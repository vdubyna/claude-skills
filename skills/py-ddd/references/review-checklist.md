# Review Checklist

## CRITICAL: Layer Dependency Violations

### C1: Domain imports third-party
- domain/ files must only import from stdlib: dataclasses, uuid, datetime, typing, enum, abc
- Check for: sqlalchemy, pydantic, fastapi, httpx, any pip package
- Grep pattern: `from sqlalchemy|from pydantic|from fastapi|import httpx|import requests`
  in files under `domain/`

### C2: Application imports infrastructure
- application/ must not import from infrastructure/ or presentation/
- Check for: `from src.<pkg>.infrastructure` or `from src.<pkg>.presentation`
  in files under `application/`

### C3: Domain imports application
- domain/ must not import from application/, infrastructure/, or presentation/
- domain only imports other domain modules and stdlib

### C4: Presentation contains business logic
- presentation/api/ files should only: parse request -> build command -> call handler -> return response
- Red flag: if/else business rules, calculations, domain validation in router files
- Endpoint functions should be <30 lines

### C5: Infrastructure imports presentation
- infrastructure/ must not import from presentation/

### C6: Circular imports between bounded contexts
- One bounded context module must not import domain entities from another
- Communication between BCs should go through application layer events/DTOs

## WARNING: Pattern Violations

### W1: Anemic domain model
- Entity with only data fields and no behavior methods
- Red flag: entity class with zero methods besides __init__
- Fix: move business logic from services/handlers INTO the entity

### W2: God service / fat handler
- Command handler with >50 lines or doing multiple unrelated things
- Service class with >10 methods
- Fix: split into separate command handlers, one per use case

### W3: Missing domain events
- Aggregate state change without recording a domain event
- Red flag: status changes in entity methods without `self._record_event()`

### W4: ORM model returned from repository
- Repository method returns SQLAlchemy model instead of domain entity
- Check: return type annotations on repository methods
- Fix: add `_to_entity()` mapper

### W5: Domain event named wrong
- Must be past tense: `OrderCreated`, not `CreateOrder` or `OrderCreate`

### W6: Command named wrong
- Must be imperative: `CreateOrder`, not `OrderCreated` or `OrderCreation`

### W7: Repository for non-aggregate
- Repository exists for a child entity or value object
- Rule: one repository per aggregate root only

### W8: Missing Protocol (Port)
- Infrastructure class used directly in application layer without Protocol
- Fix: create Protocol in application/ports/, use that in handlers

### W9: Pydantic model in domain
- Using `pydantic.BaseModel` in domain layer
- Fix: use dataclasses for domain, Pydantic only in presentation/schemas/

### W10: Business logic in repository
- Repository methods doing validation, calculations, or state transitions
- Repository should only: save, load, delete, query

## SUGGESTION: Style & Quality

### S1: Missing type hints
- All function parameters and return types should have type annotations
- All class attributes should be typed

### S2: File too large
- Entity >100 lines, handler >50 lines, router endpoint >30 lines, repo >80 lines

### S3: Missing docstring on public class
- Entity, aggregate root, service, and handler should have docstrings

### S4: Naming convention mismatch
- Entity: PascalCase noun
- Value Object: PascalCase descriptive noun, frozen
- Event: PascalCase past tense
- Command: PascalCase imperative
- Port: PascalCase with Protocol
- Repo impl: prefix with technology (SqlAlchemy, InMemory)
- ORM Model: suffix Model
- Schema: suffix Request/Response

### S5: No factory in tests
- Tests creating entities with raw constructors instead of factory functions
- Fix: use tests/factories.py

### S6: Test in wrong directory
- Domain test in integration/, or integration test in unit/
- Domain tests: no DB, no mocks needed
- Application tests: mock ports
- Integration tests: real DB (testcontainers)

## Quick Grep Commands

Run these to quickly find critical violations:

```bash
# C1: Third-party in domain
grep -rn "from sqlalchemy\|from pydantic\|from fastapi\|import httpx\|import requests" src/*/domain/

# C2: Infrastructure in application
grep -rn "from src\..*\.infrastructure" src/*/application/

# C4: Fat endpoints
find src/*/presentation -name "*.py" -exec awk '/^(async )?def /{n=0} {n++} n>30{print FILENAME": too long endpoint"; exit}' {} \;

# W1: Anemic entities (entities with no def besides __init__)
grep -rL "def [a-z]" src/*/domain/entities/*.py | grep -v base.py | grep -v __init__

# W9: Pydantic in domain
grep -rn "from pydantic\|BaseModel" src/*/domain/
```
