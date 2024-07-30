from agent.app import get_agent_app

app = get_agent_app(
    name="isp_facilitator",
    persona="isp_facilitator",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)