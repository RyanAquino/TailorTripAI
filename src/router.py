from fastapi import APIRouter

from endpoints import generate_schedule

api_router = APIRouter()

api_router.include_router(generate_schedule.router, prefix="/trips")
