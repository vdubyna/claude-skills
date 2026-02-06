# Full Feature Recipe

When user asks to "add a feature" or "create a full CRUD for X", generate files in this
exact order. Replace `<N>` with entity name (PascalCase), `<n>` with snake_case.

## File Generation Order

1. `src/<pkg>/domain/events/<n>_events.py` — domain events
2. `src/<pkg>/domain/entities/<n>.py` — aggregate root
3. `src/<pkg>/application/dto/<n>_dto.py` — DTO for reads
4. `src/<pkg>/application/ports/<n>_repository.py` — repository protocol
5. `src/<pkg>/application/commands/create_<n>.py` — create command + handler
6. `src/<pkg>/application/queries/get_<n>.py` — query + handler (optional)
7. `src/<pkg>/infrastructure/persistence/models/<n>_model.py` — ORM model
8. `src/<pkg>/infrastructure/persistence/repositories/<n>_repo.py` — repo impl
9. `src/<pkg>/presentation/schemas/<n>_schemas.py` — request/response
10. `src/<pkg>/presentation/api/v1/<ns>.py` — router

## Post-Generation Checklist

After generating files, update:
- `src/<pkg>/container.py` — add repository factory method
- `src/<pkg>/main.py` — include new router
- `alembic/env.py` — import new ORM model (if not auto-discovered)

## Example: "Add Task feature"

Files created:
```
domain/events/task_events.py        -> TaskCreated, TaskCompleted
domain/entities/task.py             -> Task(AggregateRoot)
application/dto/task_dto.py         -> TaskDTO
application/ports/task_repository.py -> TaskRepository(Protocol)
application/commands/create_task.py -> CreateTask + handle_create_task
application/commands/complete_task.py -> CompleteTask + handle_complete_task
application/queries/get_task.py     -> GetTaskById + handle_get_task
infrastructure/persistence/models/task_model.py -> TaskModel
infrastructure/persistence/repositories/task_repo.py -> SqlAlchemyTaskRepository
presentation/schemas/task_schemas.py -> CreateTaskRequest, TaskResponse
presentation/api/v1/tasks.py        -> router with POST, GET, PATCH
```

Updated:
```
container.py  -> add task_repository() method
main.py       -> app.include_router(tasks_router, prefix="/api/v1")
```
