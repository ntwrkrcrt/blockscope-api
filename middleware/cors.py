from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings


def configure_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Requested-With", "Accept", "Origin"],
    )
