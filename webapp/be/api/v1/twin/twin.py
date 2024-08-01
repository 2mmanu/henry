import os
import requests
from memgpt import create_client
from memgpt.memory import ChatMemory
from memgpt.utils import get_human_text
from .services.facilitator import get_help

class Twin():

    def __init__(self,
                 session_id:str=None,
                 id:str = None,
                 human:str = "human",  
                 persona:str = "digital-twin",
                 base_url:str=os.getenv("MEMGPT_BASEURL", default="http://localhost:8083"),
                 token:str=os.getenv("MEMGPT_TOKEN", default=""),
                 tools:list = [get_help],
                 domains = None,
                 ) -> None:
        
        self._session = session_id
        self._domains = domains

        self._base_ulr = base_url
        self._token = token
        self._client = self._get_memgpt_client()

        if not id:
            self._persona = persona
            self._human = human
            self._tools = tools
            self._agent_id = self._create_agent()
        elif self._client.agent_exists(agent_id=id):
            _agent_state = self._client.get_agent(agent_id=id)
            self._agent_id = _agent_state.id
            self._tools = _agent_state.tools
            _metadata = _agent_state._metadata
            self._persona = _metadata['persona']
            self._human = _metadata['human']
            
    def get_agent_id(self):    
        return self._agent_id

    def _get_memgpt_client(self):    
        return create_client(base_url=self._base_ulr,token=self._token)
    
    def _create_agent(self):
        tools = []
        for tool in self._tools:
            tools.append(self._client.create_tool(tool, tags=["extras"]).name)
        
        _agent_client = self._client.create_agent(
            name=self._session,
            #TODO deep on memory
            memory = ChatMemory(human=get_human_text(self._human), persona=get_human_text(self._persona)),
            metadata = {"human:": self._human, "persona": self._persona},
            tools=tools,
        )

        return _agent_client.id

    def get_domains_syntax(self):
        address = "localhost:8888"
        api_url = f'http://{address}/api/v1/get_domains'
        response = requests.get(api_url)
        return response.json()
    
    def send_message(self, question):
        domains = self._domains
        _client = self._get_memgpt_client()
        question=f"The user asks: {question} — use the function get_help if your knowledge is limited about the question. The function can explain better about: {domains}. Do not ask the user any questions until you have first consulted the get_help function."
        response = _client.user_message(agent_id=self._agent_id, message=question)
        return response.messages, response.usage