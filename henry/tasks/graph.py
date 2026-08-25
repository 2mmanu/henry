from collections import defaultdict, deque
from uuid import UUID

from henry.contracts.task import TaskEnvelope


class TaskGraphError(ValueError):
    pass


class TaskGraph:
    def __init__(self, root: TaskEnvelope) -> None:
        if root.parent_task_id is not None:
            raise TaskGraphError("root task cannot have a parent")
        self._tasks: dict[UUID, TaskEnvelope] = {root.task_id: root}
        self._dependencies: dict[UUID, set[UUID]] = defaultdict(set)

    def add_task(self, task: TaskEnvelope, depends_on: set[UUID] | None = None) -> None:
        if task.task_id in self._tasks:
            raise TaskGraphError(f"duplicate task: {task.task_id}")
        if task.parent_task_id not in self._tasks:
            raise TaskGraphError("parent task is not in graph")
        dependencies = depends_on or set()
        if unknown := dependencies - self._tasks.keys():
            raise TaskGraphError(f"unknown dependencies: {unknown}")
        self._tasks[task.task_id] = task
        self._dependencies[task.task_id] = set(dependencies)
        self.topological_order()

    def topological_order(self) -> list[TaskEnvelope]:
        indegree = {task_id: 0 for task_id in self._tasks}
        children: dict[UUID, set[UUID]] = defaultdict(set)
        for task_id, dependencies in self._dependencies.items():
            indegree[task_id] += len(dependencies)
            for dependency in dependencies:
                children[dependency].add(task_id)

        ready = deque(task_id for task_id, degree in indegree.items() if degree == 0)
        ordered: list[TaskEnvelope] = []
        while ready:
            task_id = ready.popleft()
            ordered.append(self._tasks[task_id])
            for child_id in children[task_id]:
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    ready.append(child_id)
        if len(ordered) != len(self._tasks):
            raise TaskGraphError("task graph contains a cycle")
        return ordered

    def ready_tasks(self, completed: set[UUID]) -> list[TaskEnvelope]:
        return [
            self._tasks[task_id]
            for task_id, dependencies in self._dependencies.items()
            if task_id not in completed and dependencies.issubset(completed)
        ]
