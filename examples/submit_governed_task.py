from __future__ import annotations

import json
import os
import time
from uuid import uuid4

import httpx

BASE_URL = os.getenv("HENRY_BASE_URL", "http://127.0.0.1:8090")
HEADERS = {
    "X-HEnRY-Key": os.getenv("HENRY_API_KEY", "local-demo-key"),
    "X-HEnRY-Subject": "employee-123",
    "X-HEnRY-Tenant": "example-org",
    "X-HEnRY-Entitlements": "hr:read",
}


def main() -> None:
    payload = {
        "purpose": "candidate-assessment",
        "capability_ref": "hr.compensation.read@1",
        "objective": "Return the compensation band for a software developer.",
        "inputs": {
            "role": "software-developer",
            "candidate_name": "Alice Example",
        },
        "selectors": ["role"],
        "input_classification": 2,
        "idempotency_key": f"quickstart:{uuid4()}",
    }

    with httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=10) as client:
        response = client.post("/v1/tasks", json=payload)
        response.raise_for_status()
        task = response.json()

        for _ in range(50):
            status_response = client.get(f"/v1/tasks/{task['task_id']}")
            status_response.raise_for_status()
            status = status_response.json()
            state = status["execution"]["state"]
            if state == "idle":
                break
            if state in {"cancelled", "failed"}:
                raise RuntimeError(f"Execution ended in state {state}")
            time.sleep(0.1)
        else:
            raise TimeoutError("Execution did not complete")

        audit_response = client.get(f"/v1/tasks/{task['task_id']}/audit")
        audit_response.raise_for_status()
        audit = audit_response.json()

    projection = status["execution"]["result"]["received_projection"]
    if projection != {"role": "software-developer"}:
        raise RuntimeError(f"Unexpected context projection: {projection}")

    print(
        json.dumps(
            {
                "task_id": task["task_id"],
                "task_status": status["task"]["status"],
                "runtime": status["execution"]["runtime"],
                "authorized_projection": projection,
                "candidate_name_shared": "candidate_name" in projection,
                "audit_events": [event["event_type"] for event in audit],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
