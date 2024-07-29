from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from .session import validate_session, save_data_session
from twin import Twin

router = APIRouter()

class Message(BaseModel):
    message: str

@router.post("/sentinel")
async def sentinel(x_session_id: str = Depends(validate_session)):
    pilot = Twin(name=x_session_id)
    pilot.create_agent()
    agent_id = pilot.get_agent_id()
    await save_data_session(x_session_id=x_session_id,k="agentid",v=agent_id)
    return {"agent id": agent_id}


@router.get("/stream")
async def stream(sessionId: str, content: str):
    if not sessionId or not content:
        raise HTTPException(status_code=422, detail="Invalid parameters")

    if not await validate_session(sessionId):
        raise HTTPException(status_code=401, detail="Invalid session ID")

    def event_generator():
        pilot = Twin(name=sessionId)
        # agentid = await get_data_session(sessionId,"agentid")
        pilot.create_agent() # pilot.set_agent_id(agentid)
        messages, usage = pilot.send_message(content)
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