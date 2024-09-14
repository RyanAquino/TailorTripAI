from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from src.container import Application
from src.schemas.requests import GenerateScheduleQueryParams
from src.services.scheduler_service import SchedulerService

router = APIRouter()


@router.post("/generate")
@inject
def generate_schedule(
    query_params: GenerateScheduleQueryParams,
    scheduler_service: SchedulerService = Depends(
        Provide[Application.services.scheduler_service]
    ),
):
    return scheduler_service.run(query_params)
