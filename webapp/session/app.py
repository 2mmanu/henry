from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from pydantic import BaseModel
import uvicorn
import uuid
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, str] = {}
        self.session_data = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = "active"
        self.session_data[session_id] = {}
        return session_id

    def get_session_status(self, session_id: str) -> str:
        return self.sessions.get(session_id)
    
    def set_session_data(self, session_id: str, k, v):
        self.session_data[session_id][k]=v

    def get_session_data(self, session_id: str, k):
        if k not in self.session_data[session_id]:
            raise HTTPException(status_code=404, detail="Key not found")
        return self.session_data[session_id][k]

    def close_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.session_data[session_id]

session_manager = SessionManager()

@app.post("/api/v1/create-session")
async def create_session():
    session_id = session_manager.create_session()
    return {"sessionId": session_id}

@app.get("/api/v1/session-status")
async def session_status(session_id: str):
    status = session_manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": status}

class CloseSessionRequest(BaseModel):
    sessionId: str

@app.get("/api/v1/session-data")
async def get_session_data(session_id: str, k):
    status = session_manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_manager.get_session_data(session_id,k)

@app.put("/api/v1/session-data")
async def put_session_data(session_id: str, k, v):
    status = session_manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session_manager.set_session_data(session_id,k,v)

class CloseSessionRequest(BaseModel):
    sessionId: str

@app.post("/api/v1/close-session")
async def close_session(request: CloseSessionRequest):
    session_id = request.sessionId
    if session_manager.get_session_status(session_id) is None:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    
    session_manager.close_session(session_id)
    return {"status": "session closed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
