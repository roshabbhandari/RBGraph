from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.database import init_db


@asynccontextmanager
async def app_lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield
