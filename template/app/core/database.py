from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel
from core.settings import get_settings

settings = get_settings()

def get_database_url():
  if settings.fetch("database_url"):
    return settings.fetch("database_url")
  else:
    username = settings.fetch("db_username")
    password = settings.fetch("db_password")
    host = settings.fetch("db_host", "localhost")
    port = settings.fetch("db_port", 5432)
    name = settings.fetch("db_name", f"{settings.APP_NAME}_{settings.fetch("app_env", "development")}")
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{name}"
    return database_url

engine = create_engine(get_database_url(), echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]
