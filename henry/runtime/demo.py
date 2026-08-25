from typing import Any
from uuid import uuid4

from henry.contracts.task import TaskEnvelope
from henry.runtime.models import ExecutionHandle, ExecutionState, ExecutionStatus


class DemoExecutionRuntime:
    """Deterministic local runtime used to exercise the full HEnRY control path."""

    def __init__(self) -> None:
        self._results: dict[str, dict[str, Any]] = {}

    async def submit(
        self,
        task: TaskEnvelope,
        agent_ref: str,
        context_projection: dict[str, Any],
    ) -> ExecutionHandle:
        agent_name, agent_version = agent_ref.rsplit(":", 1)
        session_id = f"demo-{uuid4()}"
        message = "Demo execution completed through the authorized context projection."
        if user_message := context_projection.get("message"):
            message = f"Risposta Omni/HEnRY demo a: {user_message}"
        self._results[session_id] = {
            "message": message,
            "objective": task.objective,
            "received_projection": context_projection,
        }
        return ExecutionHandle(
            runtime="demo",
            session_id=session_id,
            agent_name=agent_name,
            agent_version=agent_version,
        )

    async def status(self, handle: ExecutionHandle) -> ExecutionStatus:
        return ExecutionStatus(
            state=ExecutionState.IDLE,
            result=self._results[handle.session_id],
        )

    async def cancel(self, handle: ExecutionHandle) -> None:
        self._results.pop(handle.session_id, None)
