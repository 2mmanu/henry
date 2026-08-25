import json
from typing import Any

from henry.contracts.task import TaskEnvelope
from henry.runtime.models import ExecutionHandle, ExecutionState, ExecutionStatus
from henry.runtime.omniagent.client import OmniAgentClient


class OmniAgentExecutionRuntime:
    runtime_name = "omniagent"

    def __init__(self, client: OmniAgentClient) -> None:
        self._client = client

    async def submit(
        self,
        task: TaskEnvelope,
        agent_ref: str,
        context_projection: dict[str, Any],
    ) -> ExecutionHandle:
        agent_name, agent_version = self._parse_agent_ref(agent_ref)
        session = await self._client.create_session(agent_name, agent_version)
        session_id = str(session["id"])
        prompt = self._build_prompt(task, context_projection)
        await self._client.run_session(session_id, prompt)
        return ExecutionHandle(
            runtime=self.runtime_name,
            session_id=session_id,
            agent_name=agent_name,
            agent_version=agent_version,
        )

    async def status(self, handle: ExecutionHandle) -> ExecutionStatus:
        payload = await self._client.get_session_status(handle.session_id)
        return ExecutionStatus(
            state=ExecutionState(payload["status"]),
            result=payload.get("result"),
            messages=payload.get("messages", []),
            tool_calls=payload.get("tool_calls", []),
        )

    async def cancel(self, handle: ExecutionHandle) -> None:
        await self._client.cancel_session(handle.session_id)

    @staticmethod
    def _parse_agent_ref(agent_ref: str) -> tuple[str, str]:
        try:
            name, version = agent_ref.rsplit(":", 1)
        except ValueError as exc:
            raise ValueError("agent_ref must use name:version format") from exc
        if not name or not version:
            raise ValueError("agent_ref must use name:version format")
        return name, version

    @staticmethod
    def _build_prompt(task: TaskEnvelope, context_projection: dict[str, Any]) -> str:
        payload = {
            "task_id": str(task.task_id),
            "purpose": task.purpose,
            "objective": task.objective,
            "inputs": context_projection,
            "constraints": task.constraints.model_dump(mode="json"),
        }
        return (
            "Execute the authorized task described by this JSON envelope. "
            "Use only the supplied projection and configured tools.\n"
            + json.dumps(payload, sort_keys=True)
        )
