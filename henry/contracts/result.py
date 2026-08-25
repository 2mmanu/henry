from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from henry.contracts.task import DataClassification, TaskStatus


class EvidenceRef(BaseModel):
    uri: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_domain: str = Field(min_length=1)
    classification: DataClassification


class ResultEnvelope(BaseModel):
    task_id: UUID
    producer_ref: str
    status: TaskStatus
    output: Any = None
    classification: DataClassification = DataClassification.INTERNAL
    evidence: list[EvidenceRef] = Field(default_factory=list)
    policy_decision_ids: list[UUID] = Field(default_factory=list)
    runtime_session_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
