# Research landscape and alternatives

> Last reviewed: 25 August 2026. This is a focused comparison of primary publications, not a
> systematic literature review or a security certification of the listed systems.

HEnRY was proposed in 2024 to govern collaboration among agents operating across independently
owned organizational domains. Since then, research has increasingly separated this problem into
interoperability, least-privilege enforcement, cross-domain identity, information-flow governance
and auditability.

The result is not a field with one established alternative to HEnRY. It is a landscape of projects
that solve different layers of the same emerging problem.

## Why this problem is current

The strongest confirmation comes from the 2025 position paper
[Seven Security Challenges in Cross-domain Multi-agent LLM Systems][seven-challenges], accepted
for publication in *npj Artificial Intelligence*. It argues that agents controlled by different
organizations invalidate the shared-trust assumptions of single-domain systems. Its research agenda
includes dynamic group vetting, conflicting incentives, cross-domain provenance, context bypass,
and confidentiality and integrity across boundaries.

Other work reinforces individual parts of the HEnRY problem:

- [Agents Under Siege][agents-under-siege] demonstrates attacks that exploit communication and
  network topology in practical multi-agent systems.
- [A Vision for Access Control in LLM-based Agent Systems][aac] reframes access control as dynamic
  information-flow governance, including redaction, summarization and paraphrasing rather than only
  allow/deny decisions.
- [Auditable Agents][auditable-agents] treats auditability as a prerequisite for accountability and
  separates recoverability, lifecycle coverage, policy checkability, attribution and evidence
  integrity.
- [Progent][progent], [SEAgent][seagent] and [AgentGuard][agentguard] apply least privilege,
  mandatory or attribute-based access control to agent execution and tool use.

These publications do not prove that HEnRY is the only solution. They show that the concerns HEnRY
combines are active and increasingly treated as system-level requirements.

## Capability comparison

Legend:

- **●** — a primary architectural contribution of the referenced work;
- **◐** — partial coverage or an enabling mechanism;
- **—** — outside the work's primary scope.

The ratings describe the published architecture, not every feature that could be added to an
implementation.

| Work | Organizational domain sovereignty | Capability discovery and interoperability | Governed task decomposition | Minimum necessary context | Provider-neutral execution | Cross-domain traceability |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HEnRY** | ● | ● | ● | ● | ● | ● |
| [Internet of Agents][ioa] | ◐ | ● | ● | — | ● | — |
| [Agent Collaboration Protocols][acps] | ◐ | ● | ● | ◐ | ● | ◐ |
| [Progent][progent] | — | — | — | ● | ◐ | ◐ |
| [SEAgent][seagent] / [AgentGuard][agentguard] | — | — | — | ● | ◐ | ◐ |
| [Agents with DIDs and Verifiable Credentials][did-vc] | ◐ | — | — | ◐ | ● | ◐ |
| [BlockA2A][blocka2a] | ◐ | ● | ◐ | ◐ | ● | ● |
| [Auditable Agents][auditable-agents] | — | — | — | — | ◐ | ● |

## What the alternatives optimize for

### Agent interoperability and open collaboration

[Internet of Agents][ioa] connects heterogeneous third-party agents through an integration protocol,
dynamic teaming and conversation-flow control. [Agent Collaboration Protocols][acps] extends this
direction with registration, discovery, interaction and tooling protocols.

These approaches are appropriate when the primary problem is making independently implemented
agents discover and communicate with one another. HEnRY addresses a different question: after a
capability is discovered, which organizational authority may authorize it, what context may cross
the boundary, and how is the delegation reconstructed?

The approaches can be complementary. An ACP, A2A or similar protocol could transport HEnRY task,
capability and result contracts without becoming the owner of HEnRY policy.

### Least-privilege execution

[Progent][progent] introduces programmable policies around tool calls. [SEAgent][seagent] models
privilege escalation using mandatory and attribute-based access control, while
[AgentGuard][agentguard] provides attribute-based inspection and runtime auditing for tool-use
agents.

These systems are a better fit when the main requirement is constraining what one agent may execute
inside an existing application. HEnRY operates one level above that boundary: it models who owns a
capability, why another domain may invoke it, and which projection of source context the executing
agent receives. A domain could still use one of these systems as its local policy-enforcement layer.

### Cross-domain identity and verifiable trust

[AI Agents with Decentralized Identifiers and Verifiable Credentials][did-vc] gives agents
self-controlled identities and third-party attestations for cross-domain authentication.
[BlockA2A][blocka2a] combines decentralized identity, ledger-backed audit and context-aware policy
enforcement for secure agent-to-agent interoperability.

These approaches are strongest when independently operated organizations have no common identity
or trust anchor. HEnRY does not prescribe blockchain or decentralized identity. It defines the
identity, authorization and audit correlations required at its contracts, leaving the trust mechanism
replaceable.

### Information governance and auditability

[A Vision for Access Control in LLM-based Agent Systems][aac] is close to HEnRY's visibility-cone
principle: the response to a policy decision can shape information instead of merely allowing or
denying access. [Auditable Agents][auditable-agents] is close to HEnRY's traceability objective, with
pre-execution mediation and tamper-evident evidence.

Both deepen mechanisms that HEnRY places inside a wider organizational workflow. HEnRY connects
the context projection and audit evidence to a user objective, domain-owned capability, policy
decision, task graph, runtime execution and classified result.

## Where HEnRY is different

HEnRY's contribution is not that it is the only project with agents, policies or audit logs. Its
distinction is the composition of those concerns around the **sovereign domain**:

1. A domain is an ownership, policy, data and trust boundary, not just an agent label.
2. The digital twin represents the user while keeping user-owned memory outside domain agents.
3. The facilitator decomposes objectives without receiving universal authority.
4. The mediator governs temporary cross-domain collaboration and context propagation.
5. Capability contracts expose business functions without exposing domain internals.
6. Context grants create recipient- and purpose-bound visibility cones.
7. Runtime providers execute authorized work but do not own governance decisions.
8. The audit chain correlates identity, policy, grant, task, provider session and result.

This makes HEnRY most relevant when a task must cross real organizational boundaries and the
organization cannot accept either isolated assistants or one over-privileged central agent.

## When HEnRY is not the right layer

HEnRY adds governance structure and is not necessary for every agent application:

- use a conventional orchestration runtime when every participant is inside one trust domain;
- use an agent protocol when interoperability is the only missing capability;
- use tool-level privilege middleware when the boundary is one agent and its tools;
- use decentralized identity or verifiable ledgers when cross-organization trust is the primary
  problem;
- combine those mechanisms with HEnRY when collaboration must preserve organizational sovereignty
  and minimum-context guarantees end to end.

## Open gaps

The current HEnRY repository is an alpha reference implementation, not a complete answer to the
cross-domain security agenda. Production work remains for federated identity, durable policy and
storage, distributed audit, complete facilitator and mediator workflows, dynamic agent vetting,
collusion and covert-channel defenses, and formal evaluation of multi-hop context leakage.

These gaps are important research and engineering opportunities. A credible evaluation should test
HEnRY against the seven cross-domain challenges, measure authorized-context utility versus leakage,
and verify whether every critical action retains a reconstructable source-to-result chain.

## References

- Lacavalla et al. (2024), [HEnRY: A Multi-Agent System Framework for Multi-Domain Contexts][henry-paper].
- Chen et al. (2024), [Internet of Agents: Weaving a Web of Heterogeneous Agents for Collaborative Intelligence][ioa].
- Shi et al. (2025), [Progent: Programmable Privilege Control for LLM Agents][progent].
- Liu et al. (2025), [Agent Collaboration Protocols for the Internet of Agents][acps].
- Ko et al. (2025/2026), [Seven Security Challenges in Cross-domain Multi-agent LLM Systems][seven-challenges].
- Khan et al. (2025), [Agents Under Siege][agents-under-siege].
- Zou et al. (2025), [BlockA2A: Towards Secure and Verifiable Agent-to-Agent Interoperability][blocka2a].
- Li et al. (2025), [A Vision for Access Control in LLM-based Agent Systems][aac].
- Garzon et al. (2025), [AI Agents with Decentralized Identifiers and Verifiable Credentials][did-vc].
- Ji et al. (2026), [SEAgent: A Mandatory Access Control Framework][seagent].
- Nian et al. (2026), [Auditable Agents][auditable-agents].
- Luo et al. (2026), [AgentGuard: An Attribute-Based Access Control Framework][agentguard].

[aac]: https://arxiv.org/abs/2510.11108
[acps]: https://arxiv.org/abs/2505.13523
[agentguard]: https://arxiv.org/abs/2605.28071
[agents-under-siege]: https://aclanthology.org/2025.acl-long.476/
[auditable-agents]: https://arxiv.org/abs/2604.05485
[blocka2a]: https://arxiv.org/abs/2508.01332
[did-vc]: https://arxiv.org/abs/2511.02841
[henry-paper]: https://arxiv.org/abs/2410.12720
[ioa]: https://arxiv.org/abs/2407.07061
[progent]: https://arxiv.org/abs/2504.11703
[seagent]: https://arxiv.org/abs/2601.11893
[seven-challenges]: https://arxiv.org/abs/2505.23847
