from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    sequence: int
    event_type: str
    task_id: UUID
    actor: str
    payload: dict[str, Any] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InMemoryAuditLedger:
    genesis_hash = "0" * 64

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(
        self,
        event_type: str,
        task_id: UUID,
        actor: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEvent:
        sequence = len(self._events) + 1
        previous_hash = self._events[-1].event_hash if self._events else self.genesis_hash
        created_at = datetime.now(UTC)
        event_id = uuid4()
        event = AuditEvent(
            event_id=event_id,
            sequence=sequence,
            event_type=event_type,
            task_id=task_id,
            actor=actor,
            payload=payload or {},
            previous_hash=previous_hash,
            event_hash="",
            created_at=created_at,
        )
        event.event_hash = self._hash_event(event)
        self._events.append(event)
        return event

    def list_for_task(self, task_id: UUID) -> list[AuditEvent]:
        return [event for event in self._events if event.task_id == task_id]

    def verify(self) -> bool:
        previous_hash = self.genesis_hash
        for event in self._events:
            expected = self._hash_event(event)
            if event.previous_hash != previous_hash or event.event_hash != expected:
                return False
            previous_hash = event.event_hash
        return True

    @staticmethod
    def _hash_event(event: AuditEvent) -> str:
        body = event.model_dump(exclude={"event_hash"}, mode="json")
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
