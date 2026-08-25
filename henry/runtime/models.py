from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DEFERRED = "deferred"
    IDLE = "idle"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ExecutionHandle(BaseModel):
    runtime: str
    session_id: str
    agent_name: str
    agent_version: str


class ExecutionStatus(BaseModel):
    state: ExecutionState
    result: Any = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
