from contextlib import asynccontextmanager
from fastapi import FastAPI
from utils.memgpt import memGPT

def get_agent_app(name:str,persona:str):

    context = {}

    # memgpt add persona --name isp_hr_expert --text "Name: isp_hr_expert. I'm a domain HR expert bot. My one goal in life is to help all humans with HR problems."

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        context["memgpt"] = memGPT(name=name,persona=persona)
        yield
        # cleanup

    app = FastAPI(lifespan=lifespan)

    @app.get("/api/v1/ask")
    def ask(question:str) -> str:
        return str(context["memgpt"].ask(question))

    @app.get("/api/v1/verify")
    def verify() -> str:
        return "ciao"

    @app.put("/api/v1/new_agent")
    def ask(agent_name:str, purpose:str, hostname:str, port:str) -> str:
        return str(context["memgpt"].ask(f"rember by now you can ask to {agent_name} [at address {hostname}:{port}] about {purpose}. use the function ask_to to send a question and get an answer. to try the connection you can use the function verify."))

    @app.put("/api/v1/create_source")
    def add_source(name):
        source_id = context["memgpt"].create_source(name)
        return str(source_id)

    @app.put("/api/v1/add_kb")
    def add_kb(source_id:str, filename:str) -> str:
        context["memgpt"].add_file_to_source(source_id=source_id,filename=filename)
        return "OK"
    
    return app