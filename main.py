from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.main_router import api_main_router
from core.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)
app.include_router(api_main_router)


if __name__ == "__main__":
    pass
