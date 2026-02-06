#!/usr/bin/env python3
"""Initialize a production-ready Python DDD project with FastAPI."""

import argparse
import re
import sys
from pathlib import Path


def to_snake_case(name: str) -> str:
    name = re.sub(r"[-\s]+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    name = re.sub(r"([A-Z])", r"_\1", name).lower().strip("_")
    return re.sub(r"_+", "_", name)


def create_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def generate_project(project_name: str, output_dir: Path) -> Path:
    pkg = to_snake_case(project_name)
    root = output_dir / project_name
    src = root / "src" / pkg

    if root.exists():
        print(f"Error: Directory {root} already exists")
        sys.exit(1)

    # -- CLAUDE.md --------------------------------------------------------
    template_path = Path(__file__).parent.parent / "references" / "claude-md-template.md"
    if template_path.exists():
        template = template_path.read_text()
        # Extract content after the template header
        marker = "\n# CLAUDE.md"
        idx = template.find(marker)
        if idx != -1:
            claude_md = template[idx:].strip()
        else:
            claude_md = template
        claude_md = claude_md.replace("{project_name}", project_name)
        claude_md = claude_md.replace("{package_name}", pkg)
    else:
        claude_md = f"# CLAUDE.md\n\n## Project: {project_name}\n\nPython DDD project.\n"

    create_file(root / "CLAUDE.md", claude_md)

    # -- pyproject.toml ---------------------------------------------------
    create_file(root / "pyproject.toml", f'''[project]
name = "{project_name}"
version = "0.1.0"
description = ""
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "pydantic>=2.10",
    "pydantic-settings>=2.6",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "alembic>=1.14",
    "httpx>=0.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-cov>=6.0",
    "testcontainers[postgres]>=4.8",
    "httpx>=0.28",
    "factory-boy>=3.3",
    "ruff>=0.8",
    "mypy>=1.13",
    "pre-commit>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{pkg}"]

[tool.ruff]
target-version = "py312"
line-length = 99
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
''')

    # -- Docker -----------------------------------------------------------
    create_file(root / "Dockerfile", f'''FROM python:3.12-slim AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.{pkg}.main:app", "--host", "0.0.0.0", "--port", "8000"]
''')

    create_file(root / "docker-compose.yml", f'''services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: {pkg}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
''')

    create_file(root / ".env", f'''DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{pkg}
DEBUG=true
''')

    create_file(root / ".env.example", f'''DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{pkg}
DEBUG=true
''')

    # -- CI/CD ------------------------------------------------------------
    create_file(root / ".github" / "workflows" / "ci.yml", '''name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --all-extras
      - run: uv run ruff check src/ tests/
      - run: uv run ruff format --check src/ tests/
      - run: uv run mypy src/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --all-extras
      - run: uv run pytest --cov=src/ --cov-report=term-missing
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
''')

    # -- Pre-commit -------------------------------------------------------
    create_file(root / ".pre-commit-config.yaml", '''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
''')

    # -- .gitignore -------------------------------------------------------
    create_file(root / ".gitignore", '''__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
.env
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
''')

    # -- Alembic ----------------------------------------------------------
    create_file(root / "alembic.ini", f'''[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/{pkg}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''')

    create_file(root / "alembic" / "env.py", f'''import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.{pkg}.infrastructure.persistence.models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {{}}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''')

    create_file(root / "alembic" / "script.py.mako", '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''')

    create_file(root / "alembic" / "versions" / ".gitkeep", "")

    # -- Source: Domain Layer ---------------------------------------------
    create_file(src / "__init__.py", "")

    create_file(src / "domain" / "__init__.py", "")

    create_file(src / "domain" / "entities" / "__init__.py", "")
    create_file(src / "domain" / "entities" / "base.py", '''from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Entity:
    """Base entity with identity equality."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class AggregateRoot(Entity):
    """Entity that collects domain events."""

    _events: list = field(default_factory=list, repr=False, compare=False)

    def _record_event(self, event: object) -> None:
        self._events.append(event)

    def collect_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
''')

    create_file(src / "domain" / "value_objects" / "__init__.py", "")
    create_file(src / "domain" / "value_objects" / "base.py", '''from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Immutable, equality by value."""
    pass
''')

    create_file(src / "domain" / "events" / "__init__.py", "")
    create_file(src / "domain" / "events" / "base.py", '''from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event. Immutable, named in past tense."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
''')

    create_file(src / "domain" / "services" / "__init__.py", "")

    create_file(src / "domain" / "exceptions.py", '''class DomainError(Exception):
    """Base for all domain exceptions."""
    pass


class EntityNotFoundError(DomainError):
    pass


class BusinessRuleViolationError(DomainError):
    pass
''')

    # -- Source: Application Layer ----------------------------------------
    create_file(src / "application" / "__init__.py", "")
    create_file(src / "application" / "commands" / "__init__.py", "")
    create_file(src / "application" / "queries" / "__init__.py", "")
    create_file(src / "application" / "dto" / "__init__.py", "")

    create_file(src / "application" / "ports" / "__init__.py", "")
    create_file(src / "application" / "ports" / "unit_of_work.py", '''from typing import Protocol


class UnitOfWork(Protocol):
    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, *args: object) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
''')

    # -- Source: Infrastructure Layer -------------------------------------
    create_file(src / "infrastructure" / "__init__.py", "")

    create_file(src / "infrastructure" / "persistence" / "__init__.py", "")
    create_file(src / "infrastructure" / "persistence" / "models" / "__init__.py", "")
    create_file(src / "infrastructure" / "persistence" / "models" / "base.py",
'''from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
''')

    create_file(src / "infrastructure" / "persistence" / "repositories" / "__init__.py", "")

    create_file(src / "infrastructure" / "persistence" / "database.py", '''from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, url: str) -> None:
        self.engine = create_async_engine(url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def close(self) -> None:
        await self.engine.dispose()
''')

    create_file(src / "infrastructure" / "persistence" / "unit_of_work.py", '''from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
''')

    create_file(src / "infrastructure" / "external" / "__init__.py", "")

    # -- Source: Presentation Layer ---------------------------------------
    create_file(src / "presentation" / "__init__.py", "")
    create_file(src / "presentation" / "schemas" / "__init__.py", "")

    create_file(src / "presentation" / "api" / "__init__.py", "")
    create_file(src / "presentation" / "api" / "v1" / "__init__.py", "")
    create_file(src / "presentation" / "api" / "v1" / "health.py", '''from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
''')

    create_file(src / "presentation" / "dependencies.py", f'''"""FastAPI dependency wiring. Connects presentation to container."""

from functools import lru_cache

from src.{pkg}.container import Container
from src.{pkg}.config import get_settings


@lru_cache
def get_container() -> Container:
    return Container(get_settings())
''')

    # -- Source: Config & Entrypoints ------------------------------------
    create_file(src / "config.py", f'''from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/{pkg}"
    debug: bool = False

    model_config = {{"env_file": ".env"}}


@lru_cache
def get_settings() -> Settings:
    return Settings()
''')

    create_file(src / "container.py", f'''"""Composition Root — wire all dependencies here."""

from src.{pkg}.config import Settings
from src.{pkg}.infrastructure.persistence.database import Database
from src.{pkg}.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = Database(settings.database_url)

    def unit_of_work(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.db.session_factory)

    async def close(self) -> None:
        await self.db.close()
''')

    create_file(src / "main.py", f'''from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.{pkg}.presentation.api.v1.health import router as health_router
from src.{pkg}.presentation.dependencies import get_container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    container = get_container()
    await container.close()


app = FastAPI(title="{project_name}", lifespan=lifespan)
app.include_router(health_router, prefix="/api/v1")
''')

    # -- Tests ------------------------------------------------------------
    create_file(root / "tests" / "__init__.py", "")
    create_file(root / "tests" / "unit" / "__init__.py", "")
    create_file(root / "tests" / "unit" / "domain" / "__init__.py", "")
    create_file(root / "tests" / "unit" / "application" / "__init__.py", "")
    create_file(root / "tests" / "integration" / "__init__.py", "")

    create_file(root / "tests" / "conftest.py", '''"""Shared test fixtures."""

import pytest
''')

    create_file(root / "tests" / "factories.py", '''"""Factory functions for creating test entities.

Use these instead of raw constructors for readable, maintainable tests.
"""
''')

    create_file(root / "tests" / "unit" / "domain" / "test_placeholder.py",
'''"""Placeholder — replace with real domain tests."""


def test_domain_layer_exists() -> None:
    """Smoke test: domain package is importable."""
    assert True
''')

    # -- Docs -------------------------------------------------------------
    create_file(root / "docs" / "adr" / "0001-use-ddd-layered-architecture.md", f'''# 1. Use DDD Layered Architecture

**Status:** Accepted
**Date:** auto-generated

## Context

{project_name} needs a maintainable architecture that separates business logic
from infrastructure concerns. The team wants to be able to swap databases,
frameworks, and external services without rewriting business logic.

## Decision

Use Domain-Driven Design with a layered architecture:
- domain (pure Python entities, value objects, events)
- application (use cases, ports as Protocols)
- infrastructure (adapters implementing ports)
- presentation (FastAPI HTTP layer)

Manual Dependency Injection via Composition Root.

## Consequences

- Domain logic is testable without any infrastructure
- Slightly more files/directories than a flat structure
- New team members need to learn the layer rules
- Easy to swap infrastructure (DB, message broker, LLM provider)
''')

    print(f"Project '{project_name}' created at {root}")
    print(f"   Package: src/{pkg}/")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  uv sync --all-extras")
    print("  docker-compose up -d")
    print("  uv run alembic upgrade head")
    print(f"  uv run uvicorn src.{pkg}.main:app --reload")

    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="Init a Python DDD project")
    parser.add_argument("name", help="Project name (e.g. my-ai-service)")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    args = parser.parse_args()
    generate_project(args.name, Path(args.output))


if __name__ == "__main__":
    main()
