from sqlmodel import Session, SQLModel
from config.initializers.database import get_session_standalone, engine

with get_session_standalone() as db:
  SQLModel.metadata.create_all(engine)
