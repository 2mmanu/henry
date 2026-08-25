# Architecture

HEnRY models an agent system as a federation of sovereign domains. A domain is an organizational,
administrative, data and trust boundary with an explicit owner, classifications, policy references,
capabilities, residency and agents. Domains expose versioned capability contracts; they do not
expose unrestricted access to their internal agents, memory or tools.

The control plane authenticates the requester, discovers a domain-owned capability, evaluates
policy, creates a minimal context grant, tracks task state and records an auditable trace. The
runtime adapter then delegates only the authorized projection to an execution provider.

OmniAgent is the default adapter in the current release. It is a deployment choice rather than a
core dependency: the original prototype executed through MemGPT/Letta, and future providers can
implement the same runtime port and conformance contract.

## Invariants

1. Domain ownership and sovereignty are never delegated to an execution provider.
2. Domain owners publish and version their own capability contracts.
3. Agents are private domain implementation details behind those contracts.
4. Context is default-deny and projected at field level for a declared purpose.
5. Facilitators may decompose work but cannot bypass domain policy.
6. Mediators govern all cross-domain input and result propagation.
7. Every delegation correlates subject, policy snapshot, context grant, task and runtime session.
8. Execution providers run authorized work but do not make HEnRY governance decisions.

## Domain contracts

| Contract | Boundary responsibility |
| --- | --- |
| `DomainManifest` | Ownership, hierarchy, residency, classifications, policies and capabilities |
| `CapabilityContract` | Versioned domain API, purpose, entitlement, schema and side-effect limits |
| `AgentManifest` | Domain membership, accepted context and permitted delegation |
| `TaskEnvelope` | Governed objective addressed to one capability |
| `ContextGrant` | Expiring visibility cone approved across a boundary |
| `ResultEnvelope` | Classified result with provenance and policy correlation |

## Components

| Component | Responsibility |
| --- | --- |
| Capability registry | Domain-owned capability discovery and versioning |
| Policy engine | Entitlement, purpose and classification decisions |
| Context broker | Visibility-cone projection and expiring grants |
| Task service | Idempotency, lifecycle and runtime delegation |
| Runtime port | Vendor-neutral execution boundary |
| Runtime adapter | Provider-specific session lifecycle and result normalization |
| Audit ledger | Tamper-evident governance events and correlation |
