from enum import StrEnum

from pydantic import BaseModel, Field

from henry.contracts.task import DataClassification


class AgentRole(StrEnum):
    DIGITAL_TWIN = "digital-twin"
    FACILITATOR = "facilitator"
    MEDIATOR = "mediator"
    DOMAIN_AGENT = "domain-agent"


class RuntimeRef(BaseModel):
    provider: str = "omniagent"
    agent_name: str = Field(min_length=1)
    agent_version: str = Field(min_length=1)


class AgentManifest(BaseModel):
    agent_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    owner_domain: str = Field(min_length=1)
    role: AgentRole
    runtime: RuntimeRef
    parent: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    allowed_delegations: list[str] = Field(default_factory=list)
    accepted_context_classes: set[DataClassification] = Field(default_factory=set)
    policy_refs: list[str] = Field(default_factory=list)
