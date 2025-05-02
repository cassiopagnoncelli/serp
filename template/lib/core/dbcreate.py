from app.core.database import SessionDep, engine, create_db_and_tables

db = Session(engine)

create_db_and_tables()
