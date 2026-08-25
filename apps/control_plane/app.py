from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from apps.control_plane.auth import HeaderIdentityProvider, IdentityProvider
from henry.audit.ledger import InMemoryAuditLedger
from henry.context.broker import ContextAccessDeniedError, ContextBroker
from henry.contracts.capability import CapabilityContract, SideEffectClass
from henry.contracts.task import (
    DataClassification,
    SubjectContext,
    TaskConstraints,
    TaskEnvelope,
)
from henry.policy.engine import DefaultPolicyEngine
from henry.registry.service import CapabilityNotFoundError, InMemoryCapabilityRegistry
from henry.runtime.demo import DemoExecutionRuntime
from henry.runtime.omniagent.client import OmniAgentClient, OmniAgentError
from henry.runtime.omniagent.execution import OmniAgentExecutionRuntime
from henry.tasks.repository import InMemoryTaskRepository, TaskNotFoundError
from henry.tasks.service import TaskService


class CreateTaskRequest(BaseModel):
    purpose: str = Field(min_length=1)
    capability_ref: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    inputs: dict[str, object] = Field(default_factory=dict)
    selectors: tuple[str, ...] = ()
    input_classification: DataClassification = DataClassification.INTERNAL
    constraints: TaskConstraints = Field(default_factory=TaskConstraints)
    idempotency_key: str = Field(min_length=1)


def create_app(
    *,
    registry: InMemoryCapabilityRegistry | None = None,
    task_service: TaskService | None = None,
    identity_provider: IdentityProvider | None = None,
) -> FastAPI:
    omniagent_client: OmniAgentClient | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        if omniagent_client is not None:
            await omniagent_client.close()

    app = FastAPI(
        title="HEnRY Control Plane",
        version="0.1.0",
        description=(
            "Domain-sovereign, provider-neutral HEnRY control layer; OmniAgent is the default "
            "adapter."
        ),
        lifespan=lifespan,
    )

    capability_registry = registry or InMemoryCapabilityRegistry()
    identity = identity_provider or HeaderIdentityProvider(os.getenv("HENRY_API_KEY", ""))

    async def get_subject(request: Request) -> SubjectContext:
        return await identity.authenticate(request)

    async def require_admin(subject: SubjectContext = Depends(get_subject)) -> SubjectContext:
        if "henry:admin" not in subject.entitlements:
            raise HTTPException(403, detail="Missing henry:admin entitlement")
        return subject

    if task_service is None:
        runtime_mode = os.getenv("HENRY_RUNTIME", "omniagent")
        capability_registry.publish(
            CapabilityContract(
                ref="twin.conversation.respond@1",
                domain_id="twin",
                description="Respond to a user through the governed HEnRY digital twin.",
                input_schema={"type": "object", "required": ["message"]},
                output_schema={"type": "object", "required": ["message"]},
                required_entitlements=frozenset({"twin:chat"}),
                allowed_purposes=frozenset({"user-assistance"}),
                side_effect=SideEffectClass.READ,
                max_input_classification=DataClassification.INTERNAL,
                max_output_classification=DataClassification.INTERNAL,
                agent_ref="digital-twin:v1",
            )
        )
        if runtime_mode == "demo":
            runtime = DemoExecutionRuntime()
            capability_registry.publish(
                CapabilityContract(
                    ref="hr.compensation.read@1",
                    domain_id="hr",
                    description="Read a role compensation band in the HEnRY demo.",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    required_entitlements=frozenset({"hr:read"}),
                    allowed_purposes=frozenset({"candidate-assessment"}),
                    side_effect=SideEffectClass.READ,
                    max_input_classification=DataClassification.CONFIDENTIAL,
                    max_output_classification=DataClassification.CONFIDENTIAL,
                    agent_ref="hr-compensation-demo:v1",
                )
            )
        else:
            omniagent_client = OmniAgentClient(
                base_url=os.getenv("OMNIAGENT_BASE_URL", "http://localhost:8080"),
                api_key=os.getenv("OMNIAGENT_API_KEY", ""),
            )
            runtime = OmniAgentExecutionRuntime(omniagent_client)
        task_service = TaskService(
            registry=capability_registry,
            context_broker=ContextBroker(DefaultPolicyEngine()),
            runtime=runtime,
            repository=InMemoryTaskRepository(),
            audit=InMemoryAuditLedger(),
        )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def dashboard() -> HTMLResponse:
        html_path = Path(__file__).with_name("static") / "index.html"
        return HTMLResponse(html_path.read_text())

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/capabilities", response_model=CapabilityContract, status_code=201)
    async def publish_capability(
        capability: CapabilityContract,
        _subject: SubjectContext = Depends(require_admin),
    ) -> CapabilityContract:
        capability_registry.publish(capability)
        return capability

    @app.get("/v1/capabilities", response_model=list[CapabilityContract])
    async def discover_capabilities(
        purpose: str,
        subject: SubjectContext = Depends(get_subject),
    ) -> list[CapabilityContract]:
        return capability_registry.discover(subject.entitlements, purpose)

    @app.post("/v1/tasks", response_model=TaskEnvelope, status_code=202)
    async def submit_task(
        request: CreateTaskRequest,
        subject: SubjectContext = Depends(get_subject),
    ) -> TaskEnvelope:
        task = TaskEnvelope(
            requester=subject,
            purpose=request.purpose,
            capability_ref=request.capability_ref,
            objective=request.objective,
            inputs=request.inputs,
            input_classification=request.input_classification,
            constraints=request.constraints,
            idempotency_key=request.idempotency_key,
        )
        try:
            return await task_service.submit(task, request.selectors)
        except CapabilityNotFoundError as exc:
            raise HTTPException(404, detail=f"Capability not found: {exc}") from exc
        except ContextAccessDeniedError as exc:
            raise HTTPException(403, detail=str(exc)) from exc
        except OmniAgentError as exc:
            raise HTTPException(502, detail=str(exc)) from exc

    @app.get("/v1/tasks/{task_id}")
    async def get_task(
        task_id: UUID,
        subject: SubjectContext = Depends(get_subject),
    ) -> dict[str, object]:
        try:
            task = task_service.get(task_id)
            if task.requester.tenant_id != subject.tenant_id:
                raise HTTPException(404, detail="Task not found")
            execution = await task_service.execution_status(task_id)
            task = task_service.get(task_id)
            handle = task_service.execution_handle(task_id)
        except (TaskNotFoundError, KeyError) as exc:
            raise HTTPException(404, detail="Task not found") from exc
        except OmniAgentError as exc:
            raise HTTPException(502, detail=str(exc)) from exc
        return {
            "task": task.model_dump(mode="json"),
            "execution": execution.model_dump(mode="json") | handle.model_dump(mode="json"),
        }

    @app.post("/v1/tasks/{task_id}/cancel", response_model=TaskEnvelope)
    async def cancel_task(
        task_id: UUID,
        subject: SubjectContext = Depends(get_subject),
    ) -> TaskEnvelope:
        try:
            task = task_service.get(task_id)
            if task.requester.subject_id != subject.subject_id:
                raise HTTPException(403, detail="Only the requester can cancel this task")
            return await task_service.cancel(task_id)
        except (TaskNotFoundError, KeyError) as exc:
            raise HTTPException(404, detail="Task not found") from exc
        except OmniAgentError as exc:
            raise HTTPException(502, detail=str(exc)) from exc

    @app.get("/v1/tasks/{task_id}/audit")
    async def get_task_audit(
        task_id: UUID,
        subject: SubjectContext = Depends(get_subject),
    ) -> list[dict[str, object]]:
        try:
            task = task_service.get(task_id)
            if task.requester.tenant_id != subject.tenant_id:
                raise HTTPException(404, detail="Task not found")
        except TaskNotFoundError as exc:
            raise HTTPException(404, detail="Task not found") from exc
        return task_service.audit_events(task_id)

    return app


app = create_app()
