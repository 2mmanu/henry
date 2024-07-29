from memgpt import Admin
from memgpt import create_client
import json
from twin.services.facilitator import facilitator
from twin.services.mediator import mediator

def get_memGPT_credential():
    admin = Admin(base_url="http://localhost:8083", token="password")
    response = admin.create_user()
    user_id = response.user_id # unique UUID for the user 
    api_key = response.api_key # bearer token for authentication
    return user_id, api_key

class Twin():

    def __init__(self, name, base_url:str="http://localhost:8083", tools:list = [facilitator]) -> None:
        self.name = name
        self.base_url = base_url
        self.tools = tools
        self.agent_id = None
        _, k = get_memGPT_credential()
        self._client = create_client(base_url=self.base_url,token=k)
        
    def get_agent_id(self):
        return self.agent_id
    
    def set_agent_id(self, agent_id):
        self._agent_client = self._client.get_agent(agent_name=agent_id)
        self.agent_id = self._agent_client.id
    
    def create_agent(self):
        tools = []
        for tool in self.tools:
            tools.append(self._client.create_tool(tool, tags=["extras"]).name)

        # https://github.com/cpacker/MemGPT/pull/1532
        # if not self._client.agent_exists(agent_name=name):
        #     # Create an agent
        #     self._agent_client = self._client.create_agent(
        #                         tools=self._tools,
        #                         )
        # else:
        #     self._agent_client = self._client.get_agent(agent_name=name, tools=self._tools,)
        self._agent_client = self._client.create_agent(
            name=self.name,
            metadata= {
                "human:": "basic", 
                "persona": "sam_pov",
                },
            tools=tools,
            )
        
        self.agent_id = self._agent_client.id
    
    def send_message(self,question):
        response = self._client.user_message(agent_id=self.agent_id, message=question)
        return response.messages, response.usage