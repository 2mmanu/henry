from __future__ import annotations

import hashlib
import json
from typing import Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from henry.contracts.capability import CapabilityContract, SideEffectClass
from henry.contracts.task import DataClassification, SubjectContext


class PolicyRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    subject: SubjectContext
    capability: CapabilityContract
    purpose: str
    recipient_agent: str
    requested_classification: DataClassification
    requested_selectors: tuple[str, ...] = ()


class PolicyDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    allowed: bool
    reason: str
    granted_selectors: tuple[str, ...] = ()
    max_classification: DataClassification = DataClassification.PUBLIC
    obligations: tuple[str, ...] = ()
    policy_snapshot: str


class PolicyEngine(Protocol):
    def evaluate(self, request: PolicyRequest) -> PolicyDecision: ...


class DefaultPolicyEngine:
    version = "default-policy:v1"

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        snapshot = hashlib.sha256(
            json.dumps(
                {
                    "version": self.version,
                    "capability": request.capability.ref,
                    "purpose": request.purpose,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()

        missing = request.capability.required_entitlements - request.subject.entitlements
        if missing:
            return self._deny(f"missing entitlements: {sorted(missing)}", snapshot)
        if (
            request.capability.allowed_purposes
            and request.purpose not in request.capability.allowed_purposes
        ):
            return self._deny("purpose is not allowed", snapshot)
        if request.requested_classification > request.capability.max_input_classification:
            return self._deny("input classification exceeds capability ceiling", snapshot)
        if request.requested_classification == DataClassification.SECRET:
            return self._deny("secret context must never enter agent context", snapshot)

        obligations: list[str] = ["audit"]
        if request.requested_classification >= DataClassification.CONFIDENTIAL:
            obligations.extend(["redact", "no-long-term-memory"])
        if request.capability.side_effect != SideEffectClass.READ:
            obligations.append("human-approval")

        return PolicyDecision(
            allowed=True,
            reason="allowed",
            granted_selectors=request.requested_selectors,
            max_classification=min(
                request.requested_classification,
                request.capability.max_input_classification,
            ),
            obligations=tuple(obligations),
            policy_snapshot=snapshot,
        )

    @staticmethod
    def _deny(reason: str, snapshot: str) -> PolicyDecision:
        return PolicyDecision(
            allowed=False,
            reason=reason,
            policy_snapshot=snapshot,
        )
