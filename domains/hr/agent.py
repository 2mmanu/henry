from pydantic import SecretStr
from agentlink.agent import Agent
from agentlink.bus.config import BusSettings, BlackboardSettings, ChannelsSettings
from agentlink.bus.message import FipaAclMessage, FipaAclMessageValidator

from memgpt import Admin
from memgpt import create_client

def get_memGPT_credential():
    admin = Admin(base_url="http://localhost:8083", token="password")
    response = admin.create_user()
    user_id = response.user_id # unique UUID for the user 
    api_key = response.api_key # bearer token for authentication
    return user_id, api_key

_, k = get_memGPT_credential()
_client = create_client(base_url="http://localhost:8083",token=k)

_agent_client = _client.create_agent(
name="ISPExpert",
metadata= {
    "human:": "basic", 
    "persona": "sam_pov",
    },
)

_a0 = Agent("ISPExpert",
            topics=["HR", "Intesa Sanpaolo"],
            bus_config=BusSettings(
                channels=ChannelsSettings(
                    dns="kafka://localhost:9092",
                    ),
                blackboard=BlackboardSettings(
                    dns="redis://localhost:6379",
                    redis_pwd=SecretStr("h1qeEKs3TK"),
                    ),
                )
            )

import json

def handle_message(messages):
    response = None
    for message in messages:
        if 'internal_monologue' in message:
            print("Internal Monologue:", message['internal_monologue'])
        elif 'function_call' in message:
            try:
                function_arguments = json.loads(message['function_call']['arguments'])
                print(f"Function Call ({message['function_call']['name']}):", function_arguments)
                if message['function_call']['name'] == 'send_message':
                    response = function_arguments['message']
            except json.JSONDecodeError:
                print("Function Call:", message['function_call'])
        elif 'function_return' in message:
            print("Function Return:", message['function_return'])
        else:
            print("Message:", message)
            # TODO warning
            return message
    return response

def send_message(question):
    response = _client.user_message(agent_id=_agent_client.id, message=question)
    return response.messages, response.usage

while True:
    question = _a0.get_kb_question()
    
    question = FipaAclMessage.from_dict(question)
    request =f""" you receive a message from {question.sender}. the question is: {question.content}. the suggested ontology is: {question.ontology}.
    """

    message, usage = send_message(request)
    response = handle_message(message)

    _a0.ask_kb(ontology="response",question=response,receiver_id="facilitator")
    