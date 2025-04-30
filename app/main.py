from fastapi import FastAPI

from lib.tts import printer
from .routers import audio

printer("Starting FastAPI application...")

app = FastAPI()

app.include_router(audio.router)
