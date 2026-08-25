import unittest
from typing import Any

import httpx

from apps.control_plane.app import create_app
from apps.control_plane.auth import HeaderIdentityProvider
from henry.audit.ledger import InMemoryAuditLedger
from henry.context.broker import ContextBroker
from henry.contracts.capability import CapabilityContract
from henry.contracts.task import DataClassification, TaskEnvelope
from henry.policy.engine import DefaultPolicyEngine
from henry.registry.service import InMemoryCapabilityRegistry
from henry.runtime.models import ExecutionHandle, ExecutionState, ExecutionStatus
from henry.tasks.repository import InMemoryTaskRepository
from henry.tasks.service import TaskService


class FakeRuntime:
    def __init__(self) -> None:
        self.projection: dict[str, Any] | None = None

    async def submit(
        self,
        task: TaskEnvelope,
        agent_ref: str,
        context_projection: dict[str, Any],
    ) -> ExecutionHandle:
        self.projection = context_projection
        name, version = agent_ref.rsplit(":", 1)
        return ExecutionHandle(
            runtime="fake",
            session_id="session-1",
            agent_name=name,
            agent_version=version,
        )

    async def status(self, handle: ExecutionHandle) -> ExecutionStatus:
        return ExecutionStatus(state=ExecutionState.IDLE, result="salary band")

    async def cancel(self, handle: ExecutionHandle) -> None:
        return None


class ControlPlaneTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        capability = CapabilityContract(
            ref="hr.compensation.read@1",
            domain_id="hr",
            description="Read compensation band",
            required_entitlements=frozenset({"hr:read"}),
            allowed_purposes=frozenset({"candidate-assessment"}),
            max_input_classification=DataClassification.CONFIDENTIAL,
            max_output_classification=DataClassification.CONFIDENTIAL,
            agent_ref="hr-agent:v1",
        )
        registry = InMemoryCapabilityRegistry([capability])
        self.runtime = FakeRuntime()
        service = TaskService(
            registry=registry,
            context_broker=ContextBroker(DefaultPolicyEngine()),
            runtime=self.runtime,
            repository=InMemoryTaskRepository(),
            audit=InMemoryAuditLedger(),
        )
        app = create_app(
            registry=registry,
            task_service=service,
            identity_provider=HeaderIdentityProvider("test-key"),
        )
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://henry.test",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_authorized_task_reaches_runtime_with_projection(self) -> None:
        response = await self.client.post(
            "/v1/tasks",
            headers={
                "X-HEnRY-Key": "test-key",
                "X-HEnRY-Subject": "employee-1",
                "X-HEnRY-Tenant": "isp",
                "X-HEnRY-Entitlements": "hr:read",
            },
            json={
                "purpose": "candidate-assessment",
                "capability_ref": "hr.compensation.read@1",
                "objective": "Get salary band",
                "inputs": {"role": "developer", "candidate_name": "Alice"},
                "selectors": ["role"],
                "input_classification": 2,
                "idempotency_key": "request-1",
            },
        )
        self.assertEqual(202, response.status_code, response.text)
        task = response.json()
        self.assertEqual("submitted", task["status"])
        self.assertEqual({"role": "developer"}, self.runtime.projection)

        auth_headers = {
            "X-HEnRY-Key": "test-key",
            "X-HEnRY-Subject": "employee-1",
            "X-HEnRY-Tenant": "isp",
            "X-HEnRY-Entitlements": "hr:read",
        }
        status = await self.client.get(f"/v1/tasks/{task['task_id']}", headers=auth_headers)
        self.assertEqual(200, status.status_code)
        self.assertEqual("salary band", status.json()["execution"]["result"])

        audit = await self.client.get(
            f"/v1/tasks/{task['task_id']}/audit",
            headers=auth_headers,
        )
        self.assertEqual(200, audit.status_code)
        self.assertEqual(
            [
                "task.created",
                "context.granted",
                "runtime.submitted",
                "runtime.running",
                "task.completed",
            ],
            [event["event_type"] for event in audit.json()],
        )

    async def test_missing_identity_is_rejected(self) -> None:
        response = await self.client.post(
            "/v1/tasks",
            json={
                "purpose": "candidate-assessment",
                "capability_ref": "hr.compensation.read@1",
                "objective": "Get salary band",
                "inputs": {"role": "developer"},
                "selectors": ["role"],
                "idempotency_key": "unauthenticated",
            },
        )
        self.assertEqual(401, response.status_code)
        self.assertIsNone(self.runtime.projection)

    async def test_denied_task_never_reaches_runtime(self) -> None:
        response = await self.client.post(
            "/v1/tasks",
            headers={
                "X-HEnRY-Key": "test-key",
                "X-HEnRY-Subject": "employee-2",
                "X-HEnRY-Tenant": "isp",
            },
            json={
                "purpose": "candidate-assessment",
                "capability_ref": "hr.compensation.read@1",
                "objective": "Get salary band",
                "inputs": {"role": "developer"},
                "selectors": ["role"],
                "input_classification": 2,
                "idempotency_key": "request-2",
            },
        )
        self.assertEqual(403, response.status_code)
        self.assertIsNone(self.runtime.projection)
