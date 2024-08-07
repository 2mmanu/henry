import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1.routes import router as v1_router
from core.local import LocalContextManager
from core.redis_manager import RedisContextManager
from core.http_client import HttpClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    context_backend = os.getenv("CONTEXT_BACKEND", "local")
    if context_backend == "redis":
        http_client = HttpClient()
        context_manager = RedisContextManager(redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"), http_client=http_client)
    else:
        context_manager = LocalContextManager()
    app.state.context_manager = context_manager
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(v1_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    os.environ["CONTEXT_BACKEND"]="redis"
    context_backend = os.getenv("CONTEXT_BACKEND", "local")
    if context_backend == "redis":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
    
