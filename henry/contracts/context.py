from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from henry.contracts.task import DataClassification


class ContextGrantStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ContextGrant(BaseModel):
    grant_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    subject_id: str
    source_domain: str
    recipient_agent: str
    recipient_domain: str
    purpose: str
    selectors: tuple[str, ...]
    max_classification: DataClassification
    policy_decision_id: UUID
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(minutes=15))
    max_uses: int = Field(default=1, ge=1)
    uses: int = 0
    status: ContextGrantStatus = ContextGrantStatus.ACTIVE

    def is_usable(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return (
            self.status == ContextGrantStatus.ACTIVE
            and current < self.expires_at
            and self.uses < self.max_uses
        )
