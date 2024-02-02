from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.main import initialize_db
from app.bot.main import initialize_bot, bot_info


app = FastAPI(title=f'{bot_info.full_name} API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)


@app.on_event('startup')
def on_startup():
    initialize_db()
    initialize_bot()


app.include_router(router)
