from fastapi import APIRouter

from app.api.v1 import auth, chat, courses, lessons, parent, problems, reports, sessions, users

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
