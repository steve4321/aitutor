from fastapi import APIRouter

from app.api.v1 import auth, chat, courses, dashboard, lessons, parent, problems, reports, sessions, users
from app.api.v1 import ket
from app.api.v1 import voice

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router)
api_router.include_router(courses.router)
api_router.include_router(lessons.router)
api_router.include_router(problems.router)
api_router.include_router(sessions.router)
api_router.include_router(chat.router)
api_router.include_router(reports.router)
api_router.include_router(parent.router)
api_router.include_router(ket.router)
api_router.include_router(dashboard.router)
api_router.include_router(voice.router)
