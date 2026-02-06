# Layer Recipes

Exact patterns for generating code in each DDD layer. Use the project's
package name (from CLAUDE.md) in all imports.

## Domain: Entity

```python
# src/<pkg>/domain/entities/<name>.py
from dataclasses import dataclass, field
from uuid import UUID

from src.<pkg>.domain.entities.base import AggregateRoot
from src.<pkg>.domain.events.<name>_events import <Name>Created
from src.<pkg>.domain.exceptions import BusinessRuleViolationError


@dataclass
class <Name>(AggregateRoot):
    """Aggregate root for <Name>. All mutations go through methods."""

    # Required fields (no defaults) first
    some_field: str
    # Optional / defaulted fields
    status: str = "draft"

    def do_something(self) -> None:
        """Business method that enforces invariants and records events."""
        if self.status != "draft":
            raise BusinessRuleViolationError(f"Cannot act in {self.status}")
        self.status = "active"
        self._record_event(<Name>Created(entity_id=self.id))
```

Rules:
- Extend `AggregateRoot` for aggregate roots, `Entity` for child entities
- All mutations via methods, never set attributes directly from outside
- Record domain events inside methods via `self._record_event()`
- Raise domain exceptions, not ValueError/RuntimeError

## Domain: Value Object

```python
# src/<pkg>/domain/value_objects/<name>.py
from dataclasses import dataclass

from src.<pkg>.domain.value_objects.base import ValueObject
from src.<pkg>.domain.exceptions import BusinessRuleViolationError


@dataclass(frozen=True)
class Money(ValueObject):
    amount: int  # cents to avoid float issues
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise BusinessRuleViolationError("Amount cannot be negative")
```

Rules:
- Always `frozen=True`
- Validate in `__post_init__`
- No identity, compared by value

## Domain: Event

```python
# src/<pkg>/domain/events/<name>_events.py
from dataclasses import dataclass
from uuid import UUID

from src.<pkg>.domain.events.base import DomainEvent


@dataclass(frozen=True)
class <Name>Created(DomainEvent):
    """Past tense. Immutable. Carries only IDs and primitive data."""
    entity_id: UUID
```

## Application: Command + Handler

```python
# src/<pkg>/application/commands/<action>_<name>.py
from dataclasses import dataclass
from uuid import UUID

from src.<pkg>.application.ports.<name>_repository import <Name>Repository
from src.<pkg>.application.ports.unit_of_work import UnitOfWork
from src.<pkg>.domain.entities.<name> import <Name>


@dataclass(frozen=True)
class <Action><Name>:
    """Command: imperative verb phrase. Immutable."""
    some_field: str


async def handle_<action>_<name>(
    cmd: <Action><Name>,
    repo: <Name>Repository,
    uow: UnitOfWork,
) -> UUID:
    """One function per use case. Orchestrates domain + infra."""
    entity = <Name>(some_field=cmd.some_field)
    entity.do_something()
    async with uow:
        await repo.save(entity)
        await uow.commit()
    return entity.id
```

Rules:
- Command is a frozen dataclass (just data, no behavior)
- Handler is a standalone async function, NOT a class method
- Handler receives command + ports as arguments
- Handler orchestrates: create/load entity -> call domain methods -> persist
- One handler per use case, max ~40 lines

## Application: Query

```python
# src/<pkg>/application/queries/get_<name>.py
from dataclasses import dataclass
from uuid import UUID

from src.<pkg>.application.dto.<name>_dto import <Name>DTO
from src.<pkg>.application.ports.<name>_read_repository import <Name>ReadRepository


@dataclass(frozen=True)
class Get<Name>ById:
    id: UUID


async def handle_get_<name>(
    query: Get<Name>ById,
    repo: <Name>ReadRepository,
) -> <Name>DTO | None:
    return await repo.get_dto_by_id(query.id)
```

Rules:
- Queries can bypass domain layer for reads (CQRS)
- Return DTOs, not domain entities
- Read repositories can return DTOs directly (optimized SQL)

## Application: Port (Protocol)

```python
# src/<pkg>/application/ports/<name>_repository.py
from typing import Protocol
from uuid import UUID

from src.<pkg>.domain.entities.<name> import <Name>


class <Name>Repository(Protocol):
    async def get_by_id(self, id: UUID) -> <Name> | None: ...
    async def save(self, entity: <Name>) -> None: ...
    async def delete(self, id: UUID) -> None: ...
```

Rules:
- Always use `Protocol`, never ABC
- Methods match domain needs, not SQL operations
- One repository per aggregate root

## Application: DTO

```python
# src/<pkg>/application/dto/<name>_dto.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class <Name>DTO:
    id: UUID
    some_field: str
    status: str
    created_at: datetime
```

## Infrastructure: Repository Implementation

```python
# src/<pkg>/infrastructure/persistence/repositories/<name>_repo.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.<pkg>.domain.entities.<name> import <Name>
from src.<pkg>.infrastructure.persistence.models.<name>_model import <Name>Model


class SqlAlchemy<Name>Repository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, id: UUID) -> <Name> | None:
        async with self._session_factory() as session:
            model = await session.get(<Name>Model, id)
            return self._to_entity(model) if model else None

    async def save(self, entity: <Name>) -> None:
        async with self._session_factory() as session:
            model = self._to_model(entity)
            session.add(model)
            await session.commit()

    async def delete(self, id: UUID) -> None:
        async with self._session_factory() as session:
            model = await session.get(<Name>Model, id)
            if model:
                await session.delete(model)
                await session.commit()

    @staticmethod
    def _to_entity(model: <Name>Model) -> <Name>:
        return <Name>(
            id=model.id,
            some_field=model.some_field,
            status=model.status,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: <Name>) -> <Name>Model:
        return <Name>Model(
            id=entity.id,
            some_field=entity.some_field,
            status=entity.status,
            created_at=entity.created_at,
        )
```

Rules:
- Always map between ORM Model and Domain Entity
- Never return ORM models outside repository
- Include `_to_entity` and `_to_model` mappers

## Infrastructure: ORM Model

```python
# src/<pkg>/infrastructure/persistence/models/<name>_model.py
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.<pkg>.infrastructure.persistence.models.base import Base


class <Name>Model(Base):
    __tablename__ = "<names>"  # plural, snake_case

    id: Mapped[UUID] = mapped_column(primary_key=True)
    some_field: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="draft")
```

## Presentation: Schema

```python
# src/<pkg>/presentation/schemas/<name>_schemas.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class Create<Name>Request(BaseModel):
    some_field: str = Field(..., min_length=1, max_length=255)


class <Name>Response(BaseModel):
    id: UUID
    some_field: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Presentation: Router

```python
# src/<pkg>/presentation/api/v1/<names>.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.<pkg>.application.commands.create_<name> import (
    Create<Name>,
    handle_create_<name>,
)
from src.<pkg>.presentation.dependencies import get_container
from src.<pkg>.presentation.schemas.<name>_schemas import (
    Create<Name>Request,
    <Name>Response,
)

router = APIRouter(prefix="/<names>", tags=["<names>"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_<name>(body: Create<Name>Request) -> dict[str, UUID]:
    container = get_container()
    cmd = Create<Name>(some_field=body.some_field)
    entity_id = await handle_create_<name>(
        cmd=cmd,
        repo=container.<name>_repository(),
        uow=container.unit_of_work(),
    )
    return {"id": entity_id}
```

Rules:
- Router is thin: parse request -> build command -> call handler -> format response
- Max ~15 lines per endpoint function
- Register router in main.py: `app.include_router(router, prefix="/api/v1")`
- Add new repository factory to container.py
