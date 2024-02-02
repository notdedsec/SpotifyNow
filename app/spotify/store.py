from spotipy.cache_handler import CacheHandler

from app.database.database import Database

db = Database()


class TokenStore(CacheHandler):
    '''
    Handles reading and writing cached Spotify authorization tokens
    to and from the database.
    '''

    def __init__(self, user_id: int):
        '''
        Parameters:
             * user_id: `id` of the user in the database, i.e. Telegram user id
        '''

        self.user_id = user_id


    def get_cached_token(self):
        user = db.get_user(self.user_id)
        if user:
            return user.token


    def save_token_to_cache(self, token_info):
        user = db.get_user(self.user_id)
        if not user:
            return
        user.token = token_info
        db.update_user(user)

