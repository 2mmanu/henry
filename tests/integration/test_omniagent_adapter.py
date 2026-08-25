import json
import unittest

import httpx

from henry.contracts.task import SubjectContext, TaskEnvelope
from henry.runtime.models import ExecutionState
from henry.runtime.omniagent.client import OmniAgentClient
from henry.runtime.omniagent.execution import OmniAgentExecutionRuntime


class OmniAgentAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            if request.method == "POST" and request.url.path == "/sessions":
                return httpx.Response(
                    201,
                    json={
                        "id": "session-1",
                        "agent_name": "hr-agent",
                        "agent_version": "v1",
                        "toolbox_versions": {},
                        "status": "idle",
                        "created_at": "2026-08-25T00:00:00Z",
                    },
                )
            if request.method == "POST" and request.url.path == "/sessions/session-1/run":
                return httpx.Response(202, json={"session_id": "session-1", "queued": False})
            if request.method == "GET" and request.url.path == "/sessions/session-1/status":
                return httpx.Response(
                    200,
                    json={
                        "status": "idle",
                        "result": "done",
                        "messages": [],
                        "tool_calls": [],
                    },
                )
            if request.method == "POST" and request.url.path == "/sessions/session-1/cancel":
                return httpx.Response(204)
            return httpx.Response(404)

        self.client = OmniAgentClient(
            "http://omniagent.test",
            "test-key",
            transport=httpx.MockTransport(handler),
        )
        self.runtime = OmniAgentExecutionRuntime(self.client)

    async def asyncTearDown(self) -> None:
        await self.client.close()

    async def test_submit_sends_only_context_projection(self) -> None:
        task = TaskEnvelope(
            requester=SubjectContext(subject_id="user", tenant_id="tenant"),
            purpose="candidate-assessment",
            capability_ref="hr.compensation.read@1",
            objective="Get salary band",
            inputs={"role": "developer", "candidate_name": "Alice"},
            idempotency_key="one",
        )
        handle = await self.runtime.submit(task, "hr-agent:v1", {"role": "developer"})
        self.assertEqual("session-1", handle.session_id)
        run_request = self.requests[1]
        payload = json.loads(run_request.content)
        self.assertIn('"role": "developer"', payload["prompt"])
        self.assertNotIn("candidate_name", payload["prompt"])
        self.assertEqual("test-key", run_request.headers["X-OmniAgent-Key"])

        status = await self.runtime.status(handle)
        self.assertEqual(ExecutionState.IDLE, status.state)
        self.assertEqual("done", status.result)
