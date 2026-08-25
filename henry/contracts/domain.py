from pydantic import BaseModel, Field, HttpUrl

from henry.contracts.task import DataClassification


class DomainManifest(BaseModel):
    domain_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    owner_team: str = Field(min_length=1)
    gateway_url: HttpUrl
    parent_domain: str | None = None
    classifications: set[DataClassification] = Field(default_factory=set)
    capability_refs: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)
    data_residency: str = Field(min_length=2)
    enabled: bool = True
