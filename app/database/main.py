from sqlmodel import SQLModel, create_engine

from app.config import config

engine = create_engine(config.DATABASE_URL)


def initialize_db():
    SQLModel.metadata.create_all(engine)
