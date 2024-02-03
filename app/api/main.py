import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bot.main import run
from app.config import config
from app.api.routes import router


app = FastAPI(title=f'{config.BOT_USERNAME} Authentication Server')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)

app.include_router(router)


@app.on_event('startup')
async def startup_event():
    asyncio.create_task(run())
