from contextlib import asynccontextmanager

from fastapi import FastAPI
from config import settings, state
from cors import setup_cors
from controllers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load()
    yield
    state.clear()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        lifespan=lifespan,
    )
    setup_cors(app)
    app.include_router(router)
    return app


app = create_app()
