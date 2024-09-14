import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.container import Application
from router import api_router


def create_app():
    core_container = Application()
    fast_app = FastAPI()
    fast_app.container = core_container
    fast_app.include_router(api_router, prefix="/api/v1")

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fast_app


app = create_app()


if __name__ == "__main__":
    app_config = app.container.config()
    uvicorn.run(
        "src.main:app",
        host=app_config.get("host", "0.0.0.0"),
        port=app_config.get("port", 3001),
        reload=app_config.get("debug", False),
    )
