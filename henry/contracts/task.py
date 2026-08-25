from __future__ import annotations

from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataClassification(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    SECRET = 4


class TaskStatus(StrEnum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    SUBMITTED = "submitted"
    RUNNING = "running"
    DEFERRED = "deferred"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubjectContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    subject_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    entitlements: frozenset[str] = frozenset()
    attributes: dict[str, str] = Field(default_factory=dict)


class TaskConstraints(BaseModel):
    deadline: datetime | None = None
    max_cost: float | None = Field(default=None, ge=0)
    max_steps: int = Field(default=8, ge=1, le=100)


class TaskEnvelope(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    root_task_id: UUID | None = None
    parent_task_id: UUID | None = None
    correlation_id: UUID = Field(default_factory=uuid4)
    requester: SubjectContext
    purpose: str = Field(min_length=1)
    capability_ref: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    input_classification: DataClassification = DataClassification.INTERNAL
    context_grant_ids: list[UUID] = Field(default_factory=list)
    constraints: TaskConstraints = Field(default_factory=TaskConstraints)
    idempotency_key: str = Field(min_length=1)
    policy_snapshot: str | None = None
    status: TaskStatus = TaskStatus.CREATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def initialize_root(self) -> TaskEnvelope:
        if self.root_task_id is None:
            self.root_task_id = self.task_id
        return self
