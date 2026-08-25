from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from henry.contracts.task import DataClassification


class SideEffectClass(StrEnum):
    READ = "read"
    DRAFT = "draft"
    REVERSIBLE_WRITE = "reversible-write"
    IRREVERSIBLE_WRITE = "irreversible-write"


class CapabilityContract(BaseModel):
    ref: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+@[0-9]+$")
    domain_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    required_entitlements: frozenset[str] = frozenset()
    allowed_purposes: frozenset[str] = frozenset()
    side_effect: SideEffectClass = SideEffectClass.READ
    max_input_classification: DataClassification = DataClassification.INTERNAL
    max_output_classification: DataClassification = DataClassification.INTERNAL
    agent_ref: str = Field(min_length=1)
    timeout_seconds: int = Field(default=60, ge=1, le=3600)
