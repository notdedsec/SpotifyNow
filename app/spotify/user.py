import logging
from typing import Dict, Optional, Tuple
from uuid import uuid4

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from app.config import config
from app.database.cache import cache_store
from app.database.database import Database
from app.models import Stats, Track, User
from app.spotify.store import TokenStore

db = Database()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# user-read-private user-read-recently-played user-top-read
# https://developer.spotify.com/documentation/general/guides/authorization/scopes/


class SpotifyNowUser():
    '''
    Interface for interacting with Spotify API via spotipy
    and also with the database
    '''

    def __init__(self, user_id: int, user_name: Optional[str] = None) -> None:
        """
        Parameters:
             * user_id: `id` of the user in the database, i.e. Telegram user id
        """

        self.user = User(id=user_id)
        self.user.name = user_name or self.user.name

        self.cache_handler = TokenStore(user_id)
        self.oauth_manager = SpotifyOAuth(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            redirect_uri=config.REDIRECT_URI,
            cache_handler=self.cache_handler,
            open_browser=False,
            scope=[
                'user-read-currently-playing'
            ]
        )


    def get_auth_url(self) -> str:
        state = str(uuid4())
        cache_store.set(state, self.user.id, ttl=999)
        url = self.oauth_manager.get_authorize_url(state)
        return url


    def generate_access_token(self, code: str) -> str:
        status = 'auth_failed'
        try:
            cache = self.oauth_manager.get_cached_token()
            token = self.oauth_manager.get_access_token(code)
        except Exception as e:
            logger.warning(f'Failed to get tokens from store: {e}')
            return status

        if token:
            status = 'auth_success'

        if token and not cache:
            status = 'auth_success_new'

        return status


    def connect(self) -> Spotify:
        spotify = Spotify(oauth_manager=self.oauth_manager)
        return spotify


    def link(self) -> User:
        user = db.create_user(self.user)
        return user


    def unlink(self) -> Optional[User]:
        user = db.delete_user(self.user.id)
        return user


    def update(self, updates: Dict[str, str]) -> Optional[User]:
        user = db.get_user(self.user.id)
        if not user:
            raise ValueError('User is not in the database')
        for key, val in updates.items():
            setattr(user, key, val)
        user = db.update_user(user)
        return user


    def fetch(self) -> Optional[User]:
        user = db.get_user(self.user.id)
        if not user:
            return
        self.user = user
        return user


    def now_playing(self) -> Optional[Track]:
        spotify = self.connect()
        response = spotify.currently_playing()
        if not isinstance(response, dict) or not response.get('item'):
            return

        item = response['item']
        song = item['type'] == 'track' # else podcast

        track = Track.parse_obj({
            'name': item['name'],
            'album': item['album']['name'] if song else item['show']['name'],
            'artist': ', '.join([x['name'] for x in item['artists']]) if song else item['show']['publisher'],
            'duration': item['duration_ms'],
            'position': response.get('progress_ms', 0),
            'pic': item['album']['images'][0]['url'] if song else item['images'][0]['url'],
            'url': item['href'],
            'raw': response
        })

        return track


    def top_stats(self) -> Optional[Stats]:
        ...
