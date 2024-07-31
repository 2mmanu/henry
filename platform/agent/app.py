from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from utils.memgpt import memGPT
import httpx, tempfile, os, shutil


def get_agent_app(name:str,persona:str,purpose:str=None,hostname:str=None,port:str=None,parent_hostname:str=None,parent_port:str=None):

    context = {}

    # memgpt add persona --name isp_hr_expert --text "Name: isp_hr_expert. I'm a domain HR expert bot. My one goal in life is to help all humans with HR problems."

    def notify_to_parent(name:str,purpose:str,hostname:str,port:str,parent_hostname:str,parent_port:str):
        notification_url = f"http://{parent_hostname}:{parent_port}/api/v1/new_agent"
        parameters = {"agent_name":name, "purpose":purpose, "hostname":hostname, "port":port}
        with httpx.Client() as client:
            response = client.put(notification_url, params=parameters)
            print(f"Notification sent with status code {response.status_code}")


    @asynccontextmanager
    async def lifespan(app: FastAPI):
        context["memgpt"] = memGPT(name=name,persona=persona)
        context["agents"] = {}
        if parent_hostname is not None and parent_port is not None:
            notify_to_parent(name=name,purpose=purpose,hostname=hostname,port=port,parent_hostname=parent_hostname,parent_port=parent_port)
        yield
        # cleanup

    app = FastAPI(lifespan=lifespan)

    @app.get("/api/v1/ask")
    def ask(question:str) -> str:
        if len(context["agents"])!=0:
            return str(context["memgpt"].request(context["agents"],question))
        return str(context["memgpt"].ask(question))

    @app.get("/api/v1/verify")
    def verify() -> str:
        return "ciao"
    
    @app.get("/api/v1/agents")
    def list_agents() -> str:
        return str(context["agents"])

    @app.put("/api/v1/new_agent")
    def ask(agent_name:str, purpose:str, hostname:str, port:str) -> str:
        if agent_name not in context["agents"]:
            context["agents"][agent_name]={
                "purpose": purpose,
                "hostname": hostname,
                "port":port
            }
            _client = context["memgpt"]
            response = _client.notify(f"rember by now you can ask to {agent_name} [at address {hostname}:{port}] about {purpose}. use the function ask_to to send a question and get an answer. to try the connection you can use the function verify.")
            return str(response)
        return f"agent {agent_name} exists"

    @app.put("/api/v1/create_source")
    def add_source(name):
        source_id = context["memgpt"].create_source(name)
        return str(source_id)

    @app.put("/api/v1/add_kb")
    def add_kb(source_id:str, file: UploadFile) -> str:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, file.filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                context["memgpt"].add_file_to_source(source_id=source_id,filename=file_path)
                
                return JSONResponse(status_code=200, content={"message": "File uploaded and processed successfully"})
        
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": str(e)})
    
    return app