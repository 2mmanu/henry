import unittest
from datetime import UTC, datetime, timedelta

from henry.context.broker import ContextAccessDeniedError, ContextBroker
from henry.contracts.capability import CapabilityContract
from henry.contracts.context import ContextGrantStatus
from henry.contracts.task import DataClassification, SubjectContext, TaskEnvelope
from henry.policy.engine import DefaultPolicyEngine


def capability() -> CapabilityContract:
    return CapabilityContract(
        ref="hr.compensation.read@1",
        domain_id="hr",
        description="Read a compensation band",
        required_entitlements=frozenset({"hr:read"}),
        allowed_purposes=frozenset({"candidate-assessment"}),
        max_input_classification=DataClassification.CONFIDENTIAL,
        max_output_classification=DataClassification.CONFIDENTIAL,
        agent_ref="hr-compensation:v1",
    )


def task(entitlements: frozenset[str]) -> TaskEnvelope:
    return TaskEnvelope(
        requester=SubjectContext(
            subject_id="employee-1",
            tenant_id="isp",
            entitlements=entitlements,
        ),
        purpose="candidate-assessment",
        capability_ref="hr.compensation.read@1",
        objective="Find the role salary band",
        inputs={"role": "developer", "candidate_name": "Alice"},
        input_classification=DataClassification.CONFIDENTIAL,
        idempotency_key="request-1",
    )


class PolicyAndContextTests(unittest.TestCase):
    def test_missing_entitlement_is_denied(self) -> None:
        broker = ContextBroker(DefaultPolicyEngine())
        with self.assertRaisesRegex(ContextAccessDeniedError, "missing entitlements"):
            broker.issue_grant(task(frozenset()), capability(), ("role",))

    def test_projection_contains_only_granted_selectors(self) -> None:
        broker = ContextBroker(DefaultPolicyEngine())
        grant, snapshot = broker.issue_grant(
            task(frozenset({"hr:read"})),
            capability(),
            ("role",),
        )
        projection = broker.project(grant, {"role": "developer", "candidate_name": "Alice"})
        self.assertEqual({"role": "developer"}, projection)
        self.assertEqual(64, len(snapshot))
        self.assertEqual(1, grant.uses)

    def test_expired_grant_cannot_be_used(self) -> None:
        broker = ContextBroker(DefaultPolicyEngine())
        grant, _ = broker.issue_grant(
            task(frozenset({"hr:read"})),
            capability(),
            ("role",),
        )
        grant.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        self.assertFalse(grant.is_usable())
        with self.assertRaises(ContextAccessDeniedError):
            broker.project(grant, {"role": "developer"})
        self.assertEqual(ContextGrantStatus.ACTIVE, grant.status)
