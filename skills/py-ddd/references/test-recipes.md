# Test Recipes

## Factory Functions (tests/factories.py)

Always create factories for domain entities. Add new ones here as features grow.

```python
# tests/factories.py
from uuid import uuid4
from datetime import UTC, datetime

from src.<pkg>.domain.entities.order import Order


def make_order(**overrides) -> Order:
    """Create an Order with sensible defaults. Override any field."""
    defaults = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "status": "draft",
        "created_at": datetime(2024, 1, 1, tzinfo=UTC),
    }
    defaults.update(overrides)
    return Order(**defaults)
```

Rules:
- One factory per aggregate root
- Sensible defaults for all fields
- `**overrides` for test-specific values
- Import and use: `order = make_order(status="placed")`

## Domain Tests (tests/unit/domain/)

No mocks. No DB. No async. Pure Python logic.

```python
# tests/unit/domain/test_order.py
import pytest

from src.<pkg>.domain.exceptions import BusinessRuleViolationError
from tests.factories import make_order


class TestOrderPlacement:
    def test_draft_order_can_be_placed(self) -> None:
        order = make_order(status="draft")
        order.place()
        assert order.status == "placed"

    def test_placed_order_cannot_be_placed_again(self) -> None:
        order = make_order(status="placed")
        with pytest.raises(BusinessRuleViolationError):
            order.place()

    def test_placing_order_records_event(self) -> None:
        order = make_order()
        order.place()
        events = order.collect_events()
        assert len(events) == 1
        assert events[0].order_id == order.id


class TestOrderValueObject:
    def test_money_cannot_be_negative(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            Money(amount=-100)

    def test_money_equality(self) -> None:
        assert Money(amount=100, currency="USD") == Money(amount=100, currency="USD")
```

Pattern:
- Group tests by behavior in classes: `TestOrderPlacement`, `TestOrderCancellation`
- Test name = `test_<scenario>`: `test_draft_order_can_be_placed`
- Test domain events are recorded
- Test exceptions for invalid operations
- Test value object validation and equality

## Application Tests (tests/unit/application/)

Mock ports with simple fakes. Async tests.

```python
# tests/unit/application/test_create_order.py
import pytest
from uuid import uuid4

from src.<pkg>.application.commands.create_order import CreateOrder, handle_create_order
from src.<pkg>.domain.entities.order import Order


class FakeOrderRepository:
    """In-memory fake. Implements the same Protocol."""

    def __init__(self) -> None:
        self.saved: list[Order] = []

    async def get_by_id(self, id):
        return next((o for o in self.saved if o.id == id), None)

    async def save(self, entity: Order) -> None:
        self.saved.append(entity)


class FakeUnitOfWork:
    committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


class TestCreateOrder:
    @pytest.fixture
    def repo(self) -> FakeOrderRepository:
        return FakeOrderRepository()

    @pytest.fixture
    def uow(self) -> FakeUnitOfWork:
        return FakeUnitOfWork()

    async def test_creates_order_and_saves(self, repo, uow) -> None:
        cmd = CreateOrder(customer_id=uuid4())
        order_id = await handle_create_order(cmd=cmd, repo=repo, uow=uow)

        assert len(repo.saved) == 1
        assert repo.saved[0].id == order_id
        assert uow.committed

    async def test_order_is_placed_on_creation(self, repo, uow) -> None:
        cmd = CreateOrder(customer_id=uuid4())
        await handle_create_order(cmd=cmd, repo=repo, uow=uow)

        assert repo.saved[0].status == "placed"
```

Pattern:
- Create simple Fake classes that implement the Protocol interface
- Test that handler calls repo.save() and uow.commit()
- Test that domain logic runs (status changes, events recorded)
- Keep fakes in the same test file or in `tests/fakes.py` if reused

## Integration Tests (tests/integration/)

Real DB. Real HTTP. Testcontainers.

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from src.<pkg>.infrastructure.persistence.models.base import Base
from src.<pkg>.main import app


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture
async def db_session(postgres_url):
    engine = create_async_engine(postgres_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

```python
# tests/integration/test_order_api.py
import pytest
from httpx import AsyncClient


class TestOrderAPI:
    async def test_create_order_returns_201(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/orders/", json={
            "customer_id": "550e8400-e29b-41d4-a716-446655440000",
        })
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_create_order_with_invalid_data_returns_422(self, client) -> None:
        response = await client.post("/api/v1/orders/", json={})
        assert response.status_code == 422
```

Pattern:
- Testcontainers for real Postgres — no SQLite substitutes
- httpx AsyncClient for real HTTP through FastAPI
- Scope session-level for container (reuse across tests)
- Function-level for DB state (clean between tests)
- Test happy path + validation errors + 404s

## Test Naming Convention

```
test_<what>_<scenario>_<expected_outcome>

Examples:
test_order_can_be_placed_from_draft
test_order_cannot_be_placed_twice
test_create_order_saves_to_repository
test_create_order_api_returns_201
test_negative_money_raises_error
```

## When to Write Which Test

| Change | Tests to write |
|---|---|
| New entity behavior | Unit domain test |
| New command handler | Unit application test + mock ports |
| New API endpoint | Integration test with httpx |
| Bug fix | Regression test at the lowest possible layer |
| Refactoring | Existing tests should pass. No new tests needed. |
