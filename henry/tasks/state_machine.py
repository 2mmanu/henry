from datetime import UTC, datetime

from henry.contracts.task import TaskEnvelope, TaskStatus


class InvalidTaskTransitionError(ValueError):
    pass


_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.CREATED: frozenset(
        {TaskStatus.AUTHORIZED, TaskStatus.CANCELLED, TaskStatus.EXPIRED}
    ),
    TaskStatus.AUTHORIZED: frozenset(
        {TaskStatus.SUBMITTED, TaskStatus.CANCELLED, TaskStatus.EXPIRED}
    ),
    TaskStatus.SUBMITTED: frozenset({TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED}),
    TaskStatus.RUNNING: frozenset(
        {
            TaskStatus.DEFERRED,
            TaskStatus.AWAITING_APPROVAL,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.DEFERRED: frozenset({TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.EXPIRED}),
    TaskStatus.AWAITING_APPROVAL: frozenset(
        {TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.EXPIRED}
    ),
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.FAILED: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
    TaskStatus.EXPIRED: frozenset(),
}


def transition_task(task: TaskEnvelope, target: TaskStatus) -> TaskEnvelope:
    if target not in _TRANSITIONS[task.status]:
        raise InvalidTaskTransitionError(f"cannot transition task from {task.status} to {target}")
    return task.model_copy(update={"status": target, "updated_at": datetime.now(UTC)})
