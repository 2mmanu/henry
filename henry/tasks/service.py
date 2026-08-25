from __future__ import annotations

from typing import Any
from uuid import UUID

from henry.audit.ledger import InMemoryAuditLedger
from henry.context.broker import ContextBroker
from henry.contracts.task import TaskEnvelope, TaskStatus
from henry.registry.service import InMemoryCapabilityRegistry
from henry.runtime.models import ExecutionHandle, ExecutionState, ExecutionStatus
from henry.runtime.port import ExecutionRuntimePort
from henry.tasks.repository import InMemoryTaskRepository
from henry.tasks.state_machine import transition_task


class TaskService:
    def __init__(
        self,
        registry: InMemoryCapabilityRegistry,
        context_broker: ContextBroker,
        runtime: ExecutionRuntimePort,
        repository: InMemoryTaskRepository,
        audit: InMemoryAuditLedger,
    ) -> None:
        self._registry = registry
        self._context_broker = context_broker
        self._runtime = runtime
        self._repository = repository
        self._audit = audit
        self._handles: dict[UUID, ExecutionHandle] = {}

    async def submit(self, task: TaskEnvelope, selectors: tuple[str, ...]) -> TaskEnvelope:
        persisted = self._repository.save(task)
        if persisted.task_id != task.task_id:
            return persisted

        self._audit.append("task.created", task.task_id, task.requester.subject_id)
        capability = self._registry.resolve(task.capability_ref)
        grant, policy_snapshot = self._context_broker.issue_grant(task, capability, selectors)
        task = transition_task(
            task.model_copy(
                update={
                    "context_grant_ids": [grant.grant_id],
                    "policy_snapshot": policy_snapshot,
                }
            ),
            TaskStatus.AUTHORIZED,
        )
        self._repository.save(task)
        self._audit.append(
            "context.granted",
            task.task_id,
            "context-broker",
            {
                "grant_id": str(grant.grant_id),
                "decision_id": str(grant.policy_decision_id),
                "selectors": list(grant.selectors),
            },
        )

        projection = self._context_broker.project(grant, task.inputs)
        handle = await self._runtime.submit(task, capability.agent_ref, projection)
        self._handles[task.task_id] = handle
        task = transition_task(task, TaskStatus.SUBMITTED)
        self._repository.save(task)
        self._audit.append(
            "runtime.submitted",
            task.task_id,
            f"{handle.runtime}-adapter",
            {"runtime": handle.runtime, "session_id": handle.session_id},
        )
        return task

    async def execution_status(self, task_id: UUID) -> ExecutionStatus:
        handle = self._handles[task_id]
        execution = await self._runtime.status(handle)
        task = self._repository.get(task_id)

        if execution.state == ExecutionState.RUNNING and task.status == TaskStatus.SUBMITTED:
            task = self._transition_and_audit(task, TaskStatus.RUNNING, "runtime.running")
        elif execution.state == ExecutionState.DEFERRED:
            if task.status == TaskStatus.SUBMITTED:
                task = self._transition_and_audit(task, TaskStatus.RUNNING, "runtime.running")
            if task.status == TaskStatus.RUNNING:
                task = self._transition_and_audit(task, TaskStatus.DEFERRED, "runtime.deferred")
        elif execution.state == ExecutionState.IDLE:
            if task.status in {TaskStatus.SUBMITTED, TaskStatus.DEFERRED}:
                task = self._transition_and_audit(task, TaskStatus.RUNNING, "runtime.running")
            if task.status == TaskStatus.RUNNING:
                self._transition_and_audit(task, TaskStatus.COMPLETED, "task.completed")
        elif execution.state == ExecutionState.FAILED and task.status in {
            TaskStatus.SUBMITTED,
            TaskStatus.RUNNING,
        }:
            self._transition_and_audit(task, TaskStatus.FAILED, "task.failed")
        elif execution.state == ExecutionState.CANCELLED and task.status not in {
            TaskStatus.CANCELLED,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        }:
            self._transition_and_audit(task, TaskStatus.CANCELLED, "task.cancelled")
        return execution

    def execution_handle(self, task_id: UUID) -> ExecutionHandle:
        return self._handles[task_id]

    async def cancel(self, task_id: UUID) -> TaskEnvelope:
        task = self._repository.get(task_id)
        handle = self._handles[task_id]
        await self._runtime.cancel(handle)
        cancelled = transition_task(task, TaskStatus.CANCELLED)
        self._repository.save(cancelled)
        self._audit.append("task.cancelled", task_id, task.requester.subject_id)
        return cancelled

    def get(self, task_id: UUID) -> TaskEnvelope:
        return self._repository.get(task_id)

    def audit_events(self, task_id: UUID) -> list[dict[str, Any]]:
        return [event.model_dump(mode="json") for event in self._audit.list_for_task(task_id)]

    def _transition_and_audit(
        self, task: TaskEnvelope, target: TaskStatus, event_type: str
    ) -> TaskEnvelope:
        updated = transition_task(task, target)
        self._repository.save(updated)
        runtime = self._handles[task.task_id].runtime
        self._audit.append(event_type, task.task_id, f"{runtime}-adapter")
        return updated
