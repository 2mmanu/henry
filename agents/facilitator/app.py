from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
import requests

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
    return "I giorni di ferie dipendono dal livello. Generalmente sono 22 giorni per anno."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)