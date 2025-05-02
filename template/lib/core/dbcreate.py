from config.initializers.database import engine
from sqlmodel import Session, SQLModel

with Session(engine) as session:
  SQLModel.metadata.create_all(engine)
