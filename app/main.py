from fastapi import FastAPI
from .database import SessionLocal, engine, Base
from .routers import audio, worker
from lib.worker import audio_worker
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(audio.router)
app.include_router(worker.router)

async def on_startup():
    asyncio.create_task(audio_worker(app, SessionLocal))

app.add_event_handler("startup", on_startup)

