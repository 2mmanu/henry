from typing import Any, Protocol

from henry.contracts.task import TaskEnvelope
from henry.runtime.models import ExecutionHandle, ExecutionStatus


class ExecutionRuntimePort(Protocol):
    async def submit(
        self,
        task: TaskEnvelope,
        agent_ref: str,
        context_projection: dict[str, Any],
    ) -> ExecutionHandle: ...

    async def status(self, handle: ExecutionHandle) -> ExecutionStatus: ...

    async def cancel(self, handle: ExecutionHandle) -> None: ...
