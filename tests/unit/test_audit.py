import unittest
from uuid import uuid4

from henry.audit.ledger import InMemoryAuditLedger


class AuditLedgerTests(unittest.TestCase):
    def test_hash_chain_verifies(self) -> None:
        ledger = InMemoryAuditLedger()
        task_id = uuid4()
        ledger.append("task.created", task_id, "user")
        ledger.append("context.granted", task_id, "broker", {"selectors": ["role"]})
        self.assertTrue(ledger.verify())

    def test_tampering_is_detected(self) -> None:
        ledger = InMemoryAuditLedger()
        task_id = uuid4()
        event = ledger.append("task.created", task_id, "user")
        event.actor = "attacker"
        self.assertFalse(ledger.verify())
