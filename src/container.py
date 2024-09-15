import googlemaps
from dependency_injector import containers, providers
from langchain_groq import ChatGroq

from src.services.ai_service import AIService
from src.services.scheduler_service import SchedulerService


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    ai_model = providers.Singleton(
        ChatGroq,
        model=config.llm.model,
        temperature=0,
        max_tokens=2048,
        timeout=None,
        max_retries=2,
        api_key=config.llm.api_key,
    )
    gmaps: googlemaps.Client = providers.Singleton(
        googlemaps.Client, key=config.google_service.api_key
    )
    ai_service: providers.Factory[AIService] = providers.Factory(
        AIService, ai_model=ai_model
    )
    scheduler_service: providers.Factory[SchedulerService] = providers.Factory(
        SchedulerService, ai_service=ai_service, gmaps=gmaps
    )


class Application(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])

    config = providers.Configuration(json_files=["config.json"])
    services = providers.Container(
        Services,
        config=config,
    )
