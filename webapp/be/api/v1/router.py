from memgpt import Admin
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from .session import validate_session, save_data_session, get_data_session
from .twin import Twin

router = APIRouter()

class Message(BaseModel):
    message: str

@router.post("/set-username")
async def set_username(x_session_id: str = Depends(validate_session), username:dict= Body(...)):
    admin = Admin(base_url="http://localhost:8083", token="password")
    # admin.create_user('00000000-0000-0000-0000-000000375016')
    username = username["username"]
    k=admin.get_keys(user_id=username)[0]
    await save_data_session(x_session_id=x_session_id, k="twin_k", v=k)
    return "OK"

@router.post("/sentinel")
async def sentinel(x_session_id: str = Depends(validate_session)):
    username = get_data_session(session_id=x_session_id, k="twin_k")
    twin = Twin(session_id=x_session_id,token=username)
    twin_id = str(twin.get_agent_id())
    domains = None # twin.get_domains_syntax()
    await save_data_session(x_session_id=x_session_id, k="twin_id", v=twin_id)
    # await save_data_session(x_session_id=x_session_id, k="twin_domains", v=domains)
    # resp = twin.init_enterprise_context('Emmanuele',domains)
    return {"twin id": twin_id, "domains": domains}

@router.get("/stream")
async def stream(sessionId: str, content: str):
    if not sessionId or not content:
        raise HTTPException(status_code=422, detail="Invalid parameters")

    if not await validate_session(sessionId):
        raise HTTPException(status_code=401, detail="Invalid session ID")

    def event_generator():
        username = get_data_session(session_id=sessionId, k="twin_k")
        twin_id = get_data_session(session_id=sessionId,k="twin_id")
        twin = Twin(id=twin_id,session_id=sessionId,token=username)
        messages, usage = twin.send_message(question=content)
        yield f"""data: {json.dumps({
            "messages": messages, 
            "usage": {
                "completion_tokens": usage.completion_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "total_tokens": usage.total_tokens,
                "step_count": usage.step_count,
            }})
            }\n\n"""
        return

    return StreamingResponse(event_generator(), media_type="text/event-stream")