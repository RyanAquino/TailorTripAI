

class AIService:

    def __init__(self, ai_model):
        self._ai_model = ai_model

    def run_ai_service(self):
        print("Running...", self._ai_model)
        return {"status": "OK"}
