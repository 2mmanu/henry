from threading import Lock
from typing import Dict, List, Callable
from datetime import datetime
from core.interface import ContextManagerInterface, Message, Context

class LocalContextManager(ContextManagerInterface):
    def __init__(self):
        self.contexts: Dict[str, Context] = {}
        self.listeners: Dict[str, List[Callable[[str], None]]] = {}
        self.context_lock = Lock()

    def create_context(self, context_id: str):
        with self.context_lock:
            if context_id in self.contexts:
                raise ValueError("Context already exists")
            self.contexts[context_id] = Context()
            self.listeners[context_id] = []

    def add_message(self, context_id: str, agent_name: str, message: str):
        with self.context_lock:
            if context_id not in self.contexts:
                raise ValueError("Context not found")
            timestamp = datetime.utcnow().isoformat()
            self.contexts[context_id].messages.append(Message(timestamp=timestamp, agent_name=agent_name, message=message))
            self.contexts[context_id].last_update = timestamp
        self.notify_agents(context_id, agent_name)

    def get_context(self, context_id: str) -> Context:
        with self.context_lock:
            if context_id not in self.contexts:
                raise ValueError("Context not found")
            return self.contexts[context_id]

    def delete_context(self, context_id: str):
        with self.context_lock:
            if context_id not in self.contexts:
                raise ValueError("Context not found")
            del self.contexts[context_id]
            del self.listeners[context_id]

    def register_agent(self, context_id: str, agent_name: str):
        with self.context_lock:
            if context_id not in self.contexts:
                raise ValueError("Context not found")
            
            def notify(updater_agent_name: str):
                if agent_name != updater_agent_name:
                    print(f"Notification to {agent_name}: Context {context_id} has been updated.")
            
            self.listeners[context_id].append(notify)

    def get_last_update(self, context_id: str) -> str:
        with self.context_lock:
            if context_id not in self.contexts:
                raise ValueError("Context not found")
            return self.contexts[context_id].last_update

    def notify_agents(self, context_id: str, updater_agent_name: str):
        if context_id in self.listeners:
            for listener in self.listeners[context_id]:
                listener(updater_agent_name)
