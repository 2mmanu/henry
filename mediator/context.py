import httpx
from typing import Dict

class ContextAPI:
    def __init__(self, base_url: str, context_id: str):
        self.base_url = base_url
        self.context_id = context_id

    def create_context(self) -> Dict:
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/context/{self.context_id}")
            response.raise_for_status()
            return response.json()

    def add_message(self, agent_name: str, message: str) -> Dict:
        with httpx.Client() as client:
            response = client.put(f"{self.base_url}/context/{self.context_id}/add_message", params={"agent_name": agent_name, "message": message})
            response.raise_for_status()
            return response.json()

    def get_context(self) -> Dict:
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/context/{self.context_id}")
            response.raise_for_status()
            return response.json()

    def delete_context(self) -> Dict:
        with httpx.Client() as client:
            response = client.delete(f"{self.base_url}/context/{self.context_id}")
            response.raise_for_status()
            return response.json()

    def register_agent(self, agent_name: str, agent_url: str) -> Dict:
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/context/{self.context_id}/register", json={"agent_name": agent_name, "agent_url": agent_url})
            response.raise_for_status()
            return response.json()

    def get_last_update(self) -> Dict:
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/context/{self.context_id}/last_update")
            response.raise_for_status()
            return response.json()
