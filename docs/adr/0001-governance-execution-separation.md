# ADR 0001: Separate governance from execution

- Status: Accepted
- Date: 2026-08-25

## Context

HEnRY treats domains as first-class organizational, data and trust boundaries. It requires domain
sovereignty, purpose-limited context sharing and auditable delegation.
Execution platforms provide agent sessions, workers, models and tools, but these concerns do not
replace organizational governance decisions. OmniAgent is the current default platform; the
original prototype used MemGPT/Letta.

## Decision

HEnRY remains a vendor-neutral governance control plane. It authorizes and shapes tasks before a
runtime adapter creates a provider session. Provider identifiers are correlated with HEnRY task,
policy and context-grant identifiers but do not become the governance source of truth.

Execution providers and individual agents remain below domain-owned capability contracts. A
provider cannot grant itself access to another domain or widen a HEnRY context grant.

## Consequences

Runtime implementations can be replaced without rewriting domain policy. The architecture adds a
control-plane hop and requires explicit contracts, correlation and failure handling across layers.
