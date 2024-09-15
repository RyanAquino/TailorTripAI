from langchain_core.language_models import BaseChatModel


class AIService:

    def __init__(self, ai_model: BaseChatModel):
        self.prompts: list = []
        self._ai_model = ai_model

    def initialize_system_prompt(self, prompt: str):
        self.prompts = [
            ("system", prompt),
        ]

    def add_user_prompt(self, prompt: str):
        self.prompts.append(("human", prompt))

    def add_assistant_prompt(self, prompt: str):
        self.prompts.append(("assistant", prompt))

    @property
    def ai_model(self):
        return self._ai_model
