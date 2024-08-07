from fastapi import APIRouter, HTTPException, Depends, Request
from core.interface import ContextManagerInterface

router = APIRouter()

def get_context_manager(request: Request) -> ContextManagerInterface:
    return request.app.state.context_manager

@router.post("/context/{context_id}")
async def create_context(context_id: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        context_manager.create_context(context_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Context created successfully"}

@router.put("/context/{context_id}/add_message")
async def update_context(context_id: str, agent_name: str, message: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        context_manager.add_message(context_id, agent_name, message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "Message added to context successfully"}

@router.get("/context/{context_id}")
async def get_context(context_id: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        context = context_manager.get_context(context_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return context

@router.delete("/context/{context_id}")
async def delete_context(context_id: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        context_manager.delete_context(context_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "Context deleted successfully"}

@router.post("/context/{context_id}/register")
async def register_agent(context_id: str, agent_name: str, agent_url: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        context_manager.register_agent(context_id, agent_name, agent_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Agent {agent_name} registered for notifications"}

@router.get("/context/{context_id}/last_update")
async def get_last_update(context_id: str, context_manager: ContextManagerInterface = Depends(get_context_manager)):
    try:
        last_update = context_manager.get_last_update(context_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"last_update": last_update}
