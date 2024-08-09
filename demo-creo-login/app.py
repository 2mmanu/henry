
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    if user.username and user.password:
        return {"message": "Welcome, " + user.username + "!"}
    else:
        return {"error": "Missing username or password."}
