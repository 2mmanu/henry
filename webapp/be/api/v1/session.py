import httpx
from typing import Optional
from fastapi import HTTPException, Header

SESSION_STATUS_URL = "http://localhost:8002/api/v1/session-status"

async def validate_session(x_session_id: Optional[str] = Header(None)) -> str:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Missing session ID")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(SESSION_STATUS_URL, params={"session_id": x_session_id})
    
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    
    return x_session_id


async def save_data_session(x_session_id,k,v):
    url = 'http://localhost:8002/api/v1/session-data'
    params = {"session_id": x_session_id, "k": str(k), "v": str(v)}

    async with httpx.AsyncClient() as client:
        response = await client.put(url, params=params)
        return response.json()
        
async def get_data_session(session_id,k):
    url = 'http://localhost:8002/api/v1/session-data'
    params = {"session_id": session_id, "k": k}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
