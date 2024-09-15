from fastapi import APIRouter

from endpoints import generate_schedule, generate_tags

api_router = APIRouter()

api_router.include_router(generate_schedule.router, prefix="/trips")
api_router.include_router(generate_tags.router, prefix="/tags")
