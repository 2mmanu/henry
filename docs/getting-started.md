# Getting started

This walkthrough exercises identity, domain capability discovery, policy, context projection,
execution and audit without requiring an LLM or external provider.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

## Start the governance lab

```bash
HENRY_RUNTIME=demo HENRY_API_KEY=local-demo-key henry-control
```

Open [http://127.0.0.1:8090](http://127.0.0.1:8090), or run:

```bash
python examples/submit_governed_task.py
```

## What the example proves

The request contains two fields:

```json
{
  "role": "software-developer",
  "candidate_name": "Alice Example"
}
```

It requests only the `role` selector. HEnRY checks the caller's `hr:read` entitlement, the
`candidate-assessment` purpose and the capability classification limit. The context broker then
issues a grant whose visibility cone contains only:

```json
{
  "role": "software-developer"
}
```

The task response correlates the policy snapshot and grant with the runtime session. The audit
endpoint shows task creation, context authorization, runtime submission and completion.

## Next steps

- Change the entitlement or purpose and observe the default-deny response.
- Add `candidate_name` to the selectors and consider which policy should authorize it.
- Read [domains and sovereignty](concepts/domains.md) before defining a new capability.
- Read [provider adapters](providers/README.md) before connecting an execution platform.
