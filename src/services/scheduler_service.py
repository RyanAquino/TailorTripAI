from starlette.responses import JSONResponse

from src.services.ai_service import AIService


class SchedulerService:

    def __init__(self, ai_service: AIService):
        self._ai_service = ai_service

    def run_scheduler(self):
        print("Running...", self._ai_service)
        return JSONResponse(status_code=201, content={"status": "OK"})
