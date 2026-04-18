from fastapi import APIRouter
from app.api.v1 import auth, modules, lessons, tasks, dashboard

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(modules.router)
api_router.include_router(lessons.router)
api_router.include_router(tasks.router)
api_router.include_router(dashboard.router)

__all__ = ["api_router"]
