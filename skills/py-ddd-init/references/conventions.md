# DDD Conventions Reference

## Naming Conventions

### Domain Layer
- **Entity**: noun, PascalCase — `Order`, `User`, `Agent`
- **Value Object**: descriptive noun — `Money`, `Email`, `AgentConfig`
- **Aggregate Root**: top-level entity — same as entity naming
- **Domain Event**: past tense verb phrase — `OrderCreated`, `PaymentProcessed`, `AgentTaskCompleted`
- **Domain Service**: verb phrase — `PricingCalculator`, `AgentOrchestrator`
- **Domain Exception**: descriptive — `InsufficientFundsError`, `InvalidConfigError`

### Application Layer
- **Command**: imperative verb phrase — `CreateOrder`, `ProcessPayment`, `RunAgentTask`
- **Command Handler**: `handle_create_order(cmd, uow)` — function, not class
- **Query**: noun describing data — `GetOrderById`, `ListAgentTasks`
- **Port (Protocol)**: descriptive — `OrderRepository`, `LLMProvider`, `AgentMemoryStore`
- **DTO**: suffix with purpose — `OrderSummaryDTO`, `AgentResultDTO`

### Infrastructure Layer
- **Repository impl**: `SqlAlchemyOrderRepository`, `InMemoryOrderRepository`
- **ORM Model**: suffix `Model` — `OrderModel`, `UserModel`
- **External client**: descriptive — `OpenAIClient`, `AnthropicClient`

### Presentation Layer
- **Schema**: suffix with direction — `CreateOrderRequest`, `OrderResponse`
- **Router**: resource-based — `orders_router`, `agents_router`

## Entity Base Pattern

```python
# src/<pkg>/domain/entities/base.py
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Entity:
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

## Value Object Base Pattern

```python
# src/<pkg>/domain/value_objects/base.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Immutable, compared by value."""
    pass
```

## Aggregate Root Pattern

```python
# src/<pkg>/domain/entities/order.py
from dataclasses import dataclass, field
from uuid import UUID

from src.<pkg>.domain.entities.base import AggregateRoot
from src.<pkg>.domain.events.order_events import OrderCreated
from src.<pkg>.domain.exceptions import BusinessRuleViolationError


@dataclass
class Order(AggregateRoot):
    """Aggregate root — all changes go through this."""
    customer_id: UUID
    status: str = "draft"

    def place(self) -> None:
        if self.status != "draft":
            raise BusinessRuleViolationError(f"Cannot place order in {self.status}")
        self.status = "placed"
        self._record_event(OrderCreated(order_id=self.id))
```

## Port (Protocol) Pattern

```python
# src/<pkg>/application/ports/order_repository.py
from typing import Protocol
from uuid import UUID

from src.<pkg>.domain.entities.order import Order


class OrderRepository(Protocol):
    async def get_by_id(self, order_id: UUID) -> Order | None: ...
    async def save(self, order: Order) -> None: ...
```

## Command Handler Pattern

```python
# src/<pkg>/application/commands/create_order.py
from dataclasses import dataclass
from uuid import UUID

from src.<pkg>.application.ports.order_repository import OrderRepository
from src.<pkg>.application.ports.unit_of_work import UnitOfWork
from src.<pkg>.domain.entities.order import Order


@dataclass(frozen=True)
class CreateOrder:
    customer_id: UUID


async def handle_create_order(
    cmd: CreateOrder,
    repo: OrderRepository,
    uow: UnitOfWork,
) -> UUID:
    order = Order(customer_id=cmd.customer_id)
    order.place()
    async with uow:
        await repo.save(order)
        await uow.commit()
    return order.id
```

## Unit of Work Pattern

```python
# src/<pkg>/application/ports/unit_of_work.py
from typing import Protocol


class UnitOfWork(Protocol):
    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, *args) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

## Composition Root (Manual DI)

```python
# src/<pkg>/container.py
from src.<pkg>.config import Settings
from src.<pkg>.infrastructure.persistence.database import Database
from src.<pkg>.infrastructure.persistence.repositories.order_repo import (
    SqlAlchemyOrderRepository,
)
from src.<pkg>.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


class Container:
    """Wire all dependencies here. No magic, explicit and traceable."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = Database(settings.database_url)

    def order_repository(self) -> SqlAlchemyOrderRepository:
        return SqlAlchemyOrderRepository(self.db.session_factory)

    def unit_of_work(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.db.session_factory)
```

## File Rules

| File | Max size hint | Responsibility |
|------|-------------|----------------|
| Entity | <100 lines | State + behavior + events |
| Command handler | <50 lines | Orchestrate one use case |
| Repository impl | <80 lines | CRUD for one aggregate |
| API endpoint | <30 lines | Parse, delegate, respond |
| Schema | <40 lines | Request/Response validation |

## Import Rules (CRITICAL)

```
domain imports: stdlib only (dataclasses, uuid, datetime, typing, enum, abc)
application imports: domain + stdlib + typing.Protocol
infrastructure imports: domain + application + third-party (sqlalchemy, httpx)
presentation imports: application + schemas + fastapi

NEVER: domain importing sqlalchemy, fastapi, httpx, pydantic
NEVER: application importing sqlalchemy, fastapi
NEVER: presentation containing business logic
NEVER: infrastructure importing presentation
```
