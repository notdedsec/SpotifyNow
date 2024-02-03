from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import config
from app.database.cache import cache_store
from app.spotify.user import SpotifyNowUser

router = APIRouter()


@router.get('/', include_in_schema=False)
def home():
    return Response(f'Welcome to {config.BOT_USERNAME} Authentication Server')


@router.get(path='/callback')
def callback(code: str, state: str):
    user_id = cache_store.get(state)
    if not user_id:
        response = {'message': 'Session expired or invalid', 'error': 'INVALID_STATE'}
        return JSONResponse(content=response, status_code=401)

    user = SpotifyNowUser(user_id)
    status = user.generate_access_token(code)
    return RedirectResponse(f'https://t.me/{config.BOT_USERNAME}/?start={status}')

