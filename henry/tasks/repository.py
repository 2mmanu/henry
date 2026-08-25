from uuid import UUID

from henry.contracts.task import TaskEnvelope


class TaskNotFoundError(LookupError):
    pass


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[UUID, TaskEnvelope] = {}
        self._idempotency_index: dict[tuple[str, str], UUID] = {}

    def save(self, task: TaskEnvelope) -> TaskEnvelope:
        key = (task.requester.tenant_id, task.idempotency_key)
        existing_id = self._idempotency_index.get(key)
        if existing_id is not None and existing_id != task.task_id:
            return self._tasks[existing_id]
        self._tasks[task.task_id] = task
        self._idempotency_index[key] = task.task_id
        return task

    def get(self, task_id: UUID) -> TaskEnvelope:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskNotFoundError(task_id) from exc

    def list(self) -> list[TaskEnvelope]:
        return list(self._tasks.values())
