import unittest

from henry.contracts.task import SubjectContext, TaskEnvelope, TaskStatus
from henry.tasks.graph import TaskGraph, TaskGraphError
from henry.tasks.repository import InMemoryTaskRepository
from henry.tasks.state_machine import InvalidTaskTransitionError, transition_task


def make_task(key: str, parent: TaskEnvelope | None = None) -> TaskEnvelope:
    return TaskEnvelope(
        parent_task_id=parent.task_id if parent else None,
        root_task_id=parent.root_task_id if parent else None,
        requester=SubjectContext(subject_id="user", tenant_id="tenant"),
        purpose="test",
        capability_ref="demo.echo@1",
        objective="test task",
        idempotency_key=key,
    )


class TaskCoreTests(unittest.TestCase):
    def test_state_machine_rejects_skipped_transition(self) -> None:
        task = make_task("one")
        with self.assertRaises(InvalidTaskTransitionError):
            transition_task(task, TaskStatus.COMPLETED)

    def test_task_graph_orders_dependencies(self) -> None:
        root = make_task("root")
        first = make_task("first", root)
        second = make_task("second", root)
        graph = TaskGraph(root)
        graph.add_task(first)
        graph.add_task(second, depends_on={first.task_id})
        self.assertEqual(
            [root.task_id, first.task_id, second.task_id],
            [task.task_id for task in graph.topological_order()],
        )

    def test_graph_rejects_unknown_dependency(self) -> None:
        root = make_task("root")
        graph = TaskGraph(root)
        child = make_task("child", root)
        unknown = make_task("unknown")
        with self.assertRaises(TaskGraphError):
            graph.add_task(child, depends_on={unknown.task_id})

    def test_repository_enforces_tenant_idempotency(self) -> None:
        repository = InMemoryTaskRepository()
        first = repository.save(make_task("same"))
        second = repository.save(make_task("same"))
        self.assertEqual(first.task_id, second.task_id)
