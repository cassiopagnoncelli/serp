from sqlmodel import Session, create_engine
from contextlib import contextmanager
from typing import Annotated
from fastapi import Depends
from config.initializers.settings import get_settings

settings = get_settings()

engine = create_engine(
  settings.fetch("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/my_app_development"),
  echo = False,
  pool_size = 5
)

# For FastAPI usage
#
#   from typing import Annotated
#   from fastapi import Depends
#
#   SessionDep = Annotated[Session, Depends(get_session)]
#
# then
#
#   @app.get("/users")
#   def get_users(session: Session = Depends(get_session)):
#     session.execute(select(User)).all()
#
def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]

# For general-purpose usage
#   from config.initializers.database import get_session_standalone
#
#   with get_session_standalone() as session:
#     session.execute(select(User)).all()
#
@contextmanager
def get_session_standalone():
  with Session(engine) as session:
    yield session
