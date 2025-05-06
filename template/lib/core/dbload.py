import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlmodel import Session, SQLModel
from config.core.database import get_session_standalone, engine

if __name__ == "__main__":
    with get_session_standalone() as db:
        SQLModel.metadata.create_all(engine)
