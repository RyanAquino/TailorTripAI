from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from api.container import Application
from api.schemas.requests import GenerateScheduleQueryParams
from api.services.scheduler_service import SchedulerService

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
