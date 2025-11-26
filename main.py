from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from api.block import router as block_router
from api.logs import router as logs_router
from api.health import health_check
from core.cache.redis import init_redis, shutdown_redis
from core.block.web3 import init_web3_pool, shutdown_web3_pool
from core.logging import configure_logging
from middleware import (
    configure_cors_middleware,
    configure_exception_middleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting application...")

    await init_redis()
    await init_web3_pool()
    logger.info("Web3 clients initialized")

    yield

    logger.info("Shutting down application...")

    await shutdown_redis()
    await shutdown_web3_pool()
    logger.info("Web3 clients closed")


def _configure_middleware(app: FastAPI) -> None:
    configure_cors_middleware(app)
    configure_exception_middleware(app)


def _register_routes(app: FastAPI) -> None:
    app.add_api_route("/health", health_check, methods=["GET"])
    app.include_router(block_router)
    app.include_router(logs_router)


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="Blockscope API",
        description="",
        version="1.0.0",
    )

    _configure_middleware(app)
    _register_routes(app)

    return app


app = create_app()
