# The problem HEnRY solves

Enterprise assistants are often introduced as isolated, single-domain applications: one assistant
for HR, another for finance, another for legal, and so on. That model works for an initial use case,
but it does not provide a safe or maintainable way to complete tasks that span organizational
boundaries.

HEnRY starts from a different premise: an organization is a federation of domains, not one flat
knowledge base.

## Domains are real boundaries

A domain has its own:

- accountable owner and governance process;
- data, procedures, tools and business capabilities;
- access rules, classifications and regulatory constraints;
- internal agents, models, infrastructure and memory;
- lifecycle and technology choices.

These boundaries cannot be removed merely to make agent orchestration easier. In regulated or
large organizations, least privilege requires each user and system participant to receive only the
information relevant to its role and purpose. The HEnRY paper describes these permitted views as
**visibility cones**.

## Why common assistant architectures fail

### Isolated domain assistants create silos

Copying an assistant for every new domain fragments the user experience and the technology stack.
Users must discover and operate multiple portals, shared features are implemented repeatedly, and
cross-domain procedures remain manual or become a set of brittle point-to-point integrations. Each
new domain increases the governance and integration burden.

### A central super-agent creates excessive authority

Combining every domain in one assistant improves discoverability but weakens boundaries. The
central agent tends to accumulate broad credentials, raw context, tool access and conversation
history. It becomes difficult to answer who authorized a disclosure, which domain owned an action,
why a piece of context was available, or which agent contributed to a result.

### Runtime-specific integrations create lock-in

If organizational rules are embedded directly in prompts, tools or provider-specific sessions,
changing the execution runtime requires rebuilding the control model. Different domains may also
need different models or providers, so one runtime cannot be the organizational boundary.

## The design question

HEnRY asks:

> How can one user objective be decomposed and executed across independently governed domains
> without creating either disconnected silos or an all-powerful central agent?

A satisfactory system must provide all of the following at the same time:

1. **One interaction surface.** A user can express an objective without manually coordinating
   domain-specific assistants.
2. **Domain sovereignty.** Each domain continues to own its capabilities, policies, data and
   implementation choices.
3. **Controlled collaboration.** Cross-domain work occurs through explicit tasks and contracts,
   rather than unrestricted agent access.
4. **Minimum necessary context.** Every participant receives a purpose-bound projection instead of
   the complete source context.
5. **Replaceable execution.** Domains can select suitable models, agents and providers without
   moving governance into those providers.
6. **End-to-end accountability.** The system records decomposition, authorization, disclosure,
   execution and result provenance so a task can be reconstructed.

These requirements are in tension. Better collaboration often encourages broader sharing; stronger
isolation often makes useful workflows harder. HEnRY exists to make that trade-off explicit,
policy-controlled and auditable.

## What HEnRY contributes

HEnRY separates organizational governance from agent execution:

- the **digital twin** represents the user and protects user-owned context;
- the **facilitator** discovers capabilities and decomposes an objective into domain-scoped tasks;
- the **mediator** governs temporary collaboration and context exchange across domains;
- **domain agents** execute bounded capabilities under domain-owned rules;
- **capability contracts** expose what a domain can do without exposing its internals;
- **context grants** materialize expiring visibility cones for a recipient and purpose;
- **audit records** connect policy decisions, grants, tasks, provider executions and results.

The execution provider remains replaceable. OmniAgent is the default adapter today, while the
original research prototype used MemGPT/Letta. Neither provider defines HEnRY's domain model or
security boundary.

## Scope

HEnRY is intended for workflows where multiple agents or services must cooperate across meaningful
ownership, privacy or policy boundaries. It is not required for a single assistant operating inside
one trust domain, and it is not a substitute for an organization's identity, policy, data-governance
or records-management systems. It integrates those controls into agent collaboration.

The problem and original architecture are introduced in
[HEnRY: A Multi-Agent System Framework for Multi-Domain Contexts](https://arxiv.org/abs/2410.12720).
See the [research landscape and alternatives](related-work.md) for a sourced comparison with adjacent
approaches to interoperability, least privilege, identity and auditability.
