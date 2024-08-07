import httpx
import asyncio
import random
from typing import Dict, Any

class HttpClient:
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def post(self, url: str, data: Dict[str, Any]) -> bool:
        retries = 0
        while retries < self.max_retries:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=data)
                    if response.status_code == 200:
                        return True
            except httpx.RequestError:
                pass
            retries += 1
            delay = self.base_delay * random.uniform(0, 1) * (2 ** retries)
            await asyncio.sleep(delay)
        return False
