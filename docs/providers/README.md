# Provider adapters

Execution providers sit below HEnRY governance. They run authorized tasks but do not decide which
domain owns a capability, whether a purpose is valid or which context fields may cross a boundary.

## Runtime contract

An adapter implements `ExecutionRuntimePort`:

```python
class ExecutionRuntimePort(Protocol):
    async def submit(self, task, agent_ref, context_projection) -> ExecutionHandle: ...
    async def status(self, handle) -> ExecutionStatus: ...
    async def cancel(self, handle) -> None: ...
```

The `context_projection` argument is already authorized. Adapters must not retrieve additional
domain context or reinterpret HEnRY policy.

## Included adapters

| Adapter | Purpose |
| --- | --- |
| `DemoExecutionRuntime` | Deterministic local development and contract tests |
| `OmniAgentExecutionRuntime` | OmniAgent session creation, execution, status and cancellation |

MemGPT/Letta powered the original research prototype but is not part of the current package.

## Conformance checklist

- map one HEnRY submission to one provider execution handle;
- send only `context_projection`, never the complete task input store;
- normalize provider lifecycle states;
- preserve task and runtime correlation identifiers;
- propagate cancellation and provider failures;
- avoid provider-specific authorization decisions;
- pass projection leakage and lifecycle contract tests.
