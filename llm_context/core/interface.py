from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    timestamp: str
    agent_name: str
    message: str

class Context(BaseModel):
    messages: List[Message] = []
    last_update: str = ""

class ContextManagerInterface(ABC):
    @abstractmethod
    def create_context(self, context_id: str):
        pass

    @abstractmethod
    def add_message(self, context_id: str, agent_name: str, message: str):
        pass

    @abstractmethod
    def get_context(self, context_id: str) -> Context:
        pass

    @abstractmethod
    def delete_context(self, context_id: str):
        pass

    @abstractmethod
    def register_agent(self, context_id: str, agent_name: str):
        pass

    @abstractmethod
    def get_last_update(self, context_id: str) -> str:
        pass

    @abstractmethod
    def notify_agents(self, context_id: str, updater_agent_name: str):
        pass
