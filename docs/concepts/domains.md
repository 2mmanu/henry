# Domains and sovereignty

A HEnRY domain is an organizational, administrative, data and trust boundary. It may represent a
business function such as HR or finance, a regulated environment such as healthcare, or a personal
digital twin.

## What a domain owns

- capability definitions and versions;
- internal agents, tools and operational memory;
- policy references and accepted data classifications;
- data residency and retention requirements;
- the decision to expose, change or retire a capability.

`DomainManifest` makes that ownership explicit. `CapabilityContract` defines the narrow interface
that other domains can discover and request.

## Capability, not agent access

Callers do not receive a handle to an unrestricted agent. They address a contract such as
`hr.compensation.read@1`, which declares:

- its owning domain;
- input and output schemas;
- required entitlements and allowed purposes;
- maximum input and output classifications;
- side-effect class and timeout;
- the domain-selected agent implementation.

This keeps agents replaceable and prevents provider-specific session APIs from becoming the
organization's authorization model.

## Cross-domain roles

- The **digital twin** initiates work on behalf of a governed subject.
- The **facilitator** discovers capabilities and decomposes objectives into domain-scoped tasks.
- The **mediator** authorizes context and result propagation across boundaries.
- The **domain agent** performs one authorized capability inside its sovereignty boundary.

Facilitators coordinate but do not become superusers. Mediators enforce exchanges but do not take
ownership of domain data.
