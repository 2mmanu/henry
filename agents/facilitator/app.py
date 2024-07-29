from fastapi import FastAPI
from pydantic import SecretStr
from agentlink.agent import Agent
from agentlink.bus.config import BusSettings, BlackboardSettings, ChannelsSettings

_a0 = Agent("facilitator",
            topics=["general"],
            bus_config=BusSettings(
                channels=ChannelsSettings(
                    dns="kafka://kafka:9092",
                    ),
                blackboard=BlackboardSettings(
                    dns="redis://redis:6379",
                    redis_pwd=SecretStr("h1qeEKs3TK"),
                    ),
                )
            )

app = FastAPI()

@app.get("/api/v1/query")
def facilitator(ontology: str, question: str) -> str:
    """
    Facilitate a request to the given API with provided ontology and question, and return the response value.
    Wait for the response and give the response to the user.

    :param ontology: The ontology to be used in the API request.
    :type ontology: str
    :param question: The question to be sent to the API.
    :type question: str
    :return: The response from the API as a string.
    :rtype: str
    :raises HTTPException: If the request to the API returns a status code indicating an error.
    """
    print(f"facilitator: {question}")
    
    _a0.ask_kb(ontology=ontology,question=str(question),receiver_id="ISPExpert")
    return str(_a0.get_kb_question())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)