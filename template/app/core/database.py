from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel
from core.settings import get_settings

settings = get_settings()

def get_database_url():
  if settings.fetch("DATABASE_URL"):
    return settings.fetch("DATABASE_URL")
  else:
    username = settings.fetch("DB_USERNAME")
    password = settings.fetch("DB_PASSWORD")
    host = settings.fetch("DB_HOST", "localhost")
    port = settings.fetch("DB_PORT", 5432)
    name = settings.fetch("DB_NAME", f"{settings.APP_NAME}_{settings.fetch("APP_ENV", "development")}")
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{name}"
    return database_url

engine = create_engine(get_database_url(), echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]
