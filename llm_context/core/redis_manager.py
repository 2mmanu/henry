import redis
import json
import asyncio
from typing import List, Callable, Dict
from datetime import datetime
from core.interface import ContextManagerInterface, Message, Context
from core.http_client import HttpClient

class RedisContextManager(ContextManagerInterface):
    def __init__(self, redis_url: str = "redis://localhost:6379/0", http_client: HttpClient = HttpClient()):
        self.redis = redis.StrictRedis.from_url(redis_url, password="h1qeEKs3TK")
        self.http_client = http_client   
        self.messages_key = lambda x : f"context:{x}:messages"
        self.last_update_key = lambda x : f"context:{x}:last_update"     

    def create_context(self, context_id: str):
        last_update = datetime.utcnow().isoformat()
        self.redis.set(self.last_update_key(context_id), last_update)
        print(f"Context {context_id} created successfully")

    def add_message(self, context_id: str, agent_name: str, message: str):
        timestamp = datetime.utcnow().isoformat()
        new_message = Message(timestamp=timestamp, agent_name=agent_name, message=message)
        self.redis.rpush(self.messages_key(context_id), json.dumps(new_message.dict()))
        self.redis.set(self.last_update_key(context_id), new_message.timestamp)

        print(f"Message added to context {context_id}")
        asyncio.create_task(self.notify_agents(context_id, agent_name))

    def get_context(self, context_id: str) -> Context:
        context_key = self.messages_key(context_id)
        if not self.redis.exists(context_key):
            raise ValueError("Context not found")
        
        messages_json = self.redis.lrange(context_key, 0, -1)
        messages = [Message(**json.loads(message)) for message in messages_json]
        
        last_update = self.redis.get(self.last_update_key(context_id)).decode("utf-8")

        return Context(messages=messages, last_update=last_update)

    def delete_context(self, context_id: str):
        context_key = self.messages_key(context_id)
        if not self.redis.exists(context_key):
            raise ValueError("Context not found")
        self.redis.delete(context_key)
        self.redis.delete(self.last_update_key(context_id))

    def register_agent(self, context_id: str, agent_name: str, agent_url: str):
        #TODO refactor
        if not self.redis.exists(f"context:{context_id}"):
            raise ValueError("Context not found")

        listeners_key = f"listeners:{context_id}"
        listeners = json.loads(self.redis.get(listeners_key) or '[]')

        if not any(listener['name'] == agent_name for listener in listeners):
            listeners.append({'name': agent_name, 'url': agent_url})
            self.redis.set(listeners_key, json.dumps(listeners))

    def get_last_update(self, context_id: str) -> str:
        context_key = self.last_update_key(context_id)
        if not self.redis.exists(context_key):
            raise ValueError("Context not found")
        context_data = self.redis.get(context_key)
        return context_data

    async def send_notification(self, url: str, context_id: str, updater_agent_name: str):
        #TODO refactor
        success = await self.http_client.post(url, {"context_id": context_id, "updater_agent_name": updater_agent_name})
        if not success:
            print(f"Failed to notify agent at {url}")

    async def notify_agents(self, context_id: str, updater_agent_name: str):
        #TODO refactor
        listeners_key = f"listeners:{context_id}"
        if self.redis.exists(listeners_key):
            listeners = json.loads(self.redis.get(listeners_key) or '[]')
            for listener in listeners:
                if listener['name'] != updater_agent_name:
                    asyncio.create_task(self.send_notification(listener['url'], context_id, updater_agent_name))
