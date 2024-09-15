from endpoints import generate_schedule, generate_tags
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(generate_schedule.router, prefix="/trips")
api_router.include_router(generate_tags.router, prefix="/tags")
