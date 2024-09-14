from dependency_injector import containers, providers
from src.services.ai_service import AIService
from src.services.scheduler_service import SchedulerService


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    ai_model = providers.Singleton()
    ai_service = providers.Factory(
        AIService,
        ai_model=ai_model
    )
    scheduler_service = providers.Factory(
        SchedulerService,
        ai_service="ai-service"
    )


class Application(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["endpoints"]
    )

    config = providers.Configuration(json_files=["config.json"])
    services = providers.Container(
        Services,
        config=config,
    )
