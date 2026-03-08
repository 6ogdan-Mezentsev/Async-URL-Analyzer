from fastapi import APIRouter

from api.routes.health import router as health_router
from api.routes.tasks import router as tasks_router
from api.routes.web_socket import router as ws_router

api_main_router = APIRouter()
api_main_router.include_router(health_router)
api_main_router.include_router(tasks_router)
api_main_router.include_router(ws_router)

