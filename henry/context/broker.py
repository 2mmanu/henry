from datetime import UTC, datetime, timedelta

from henry.contracts.capability import CapabilityContract
from henry.contracts.context import ContextGrant
from henry.contracts.task import TaskEnvelope
from henry.policy.engine import PolicyEngine, PolicyRequest


class ContextAccessDeniedError(PermissionError):
    pass


class ContextBroker:
    def __init__(self, policy_engine: PolicyEngine, grant_ttl_seconds: int = 900) -> None:
        self._policy_engine = policy_engine
        self._grant_ttl_seconds = grant_ttl_seconds
        self._grants: dict[str, ContextGrant] = {}

    def issue_grant(
        self,
        task: TaskEnvelope,
        capability: CapabilityContract,
        selectors: tuple[str, ...],
    ) -> tuple[ContextGrant, str]:
        decision = self._policy_engine.evaluate(
            PolicyRequest(
                subject=task.requester,
                capability=capability,
                purpose=task.purpose,
                recipient_agent=capability.agent_ref,
                requested_classification=task.input_classification,
                requested_selectors=selectors,
            )
        )
        if not decision.allowed:
            raise ContextAccessDeniedError(decision.reason)

        grant = ContextGrant(
            task_id=task.task_id,
            subject_id=task.requester.subject_id,
            source_domain="twin",
            recipient_agent=capability.agent_ref,
            recipient_domain=capability.domain_id,
            purpose=task.purpose,
            selectors=decision.granted_selectors,
            max_classification=decision.max_classification,
            policy_decision_id=decision.decision_id,
            expires_at=datetime.now(UTC) + timedelta(seconds=self._grant_ttl_seconds),
        )
        self._grants[str(grant.grant_id)] = grant
        return grant, decision.policy_snapshot

    def project(self, grant: ContextGrant, values: dict[str, object]) -> dict[str, object]:
        if not grant.is_usable():
            raise ContextAccessDeniedError("context grant is not usable")
        projection = {key: values[key] for key in grant.selectors if key in values}
        grant.uses += 1
        return projection
