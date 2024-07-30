import os
from agent.app import get_agent_app

app = get_agent_app(
    name=os.getenv("AGENT_NAME", default="generic"),
    persona=os.getenv("PERSONA_NAME", default="generic"),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)