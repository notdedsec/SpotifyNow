from typing import Optional

from sqlmodel import Session

from app.database.main import engine
from app.models import User


class Database:
    def __init__(self):
        self.session = Session(engine)


    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


    def get_user(self, user_id: int) -> Optional[User]:
        user = self.session.get(User, user_id)
        return user


    def update_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


    def delete_user(self, user_id: int) -> Optional[User]:
        user = self.get_user(user_id)
        self.session.delete(user)
        self.session.commit()
        return user


    def count_users(self) -> int:
        count = self.session.query(User).count()
        return count

