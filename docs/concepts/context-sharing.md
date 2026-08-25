# Controlled context sharing

HEnRY assumes context is private to its source domain unless policy grants a narrower projection.
This projection is the task's **visibility cone**.

## Grant lifecycle

1. A caller submits a `TaskEnvelope` with purpose, capability and input classification.
2. The destination capability declares its entitlement, purpose and classification limits.
3. Policy evaluates the subject and requested selectors.
4. The context broker issues an expiring `ContextGrant`.
5. Only fields named by the grant are projected to the execution runtime.
6. Task, policy, grant, provider session and result identifiers are correlated in audit events.

## Security properties

- default-deny selection;
- field-level projection before provider submission;
- explicit purpose and classification checks;
- expiration and use limits;
- tenant-scoped task lookup and idempotency;
- traceability without placing private values in every audit event.

Prompts are not treated as access-control boundaries. A provider receives only the authorized
projection, so prompt injection cannot reveal fields that never entered its session.
