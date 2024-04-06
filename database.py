# -------------------------------- PYTHON IMPORTS --------------------------------#
# -------------------------------- SQL ALCHEMY IMPORTS --------------------------------#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# -------------------------------- FASTAPI IMPORTS --------------------------------#
# -------------------------------- LOCAL IMPORTS --------------------------------#
from security import settings


# create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)
# database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_public_schema_db():
    """
    Helper function to return DB session.

    Only Admin user can read, write, update and delete in public schema table.
    Other user can only read and write data from User table.

    Yields:
        _type_: DB session
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_schema_db(schema_name: str):
    """
    Helper function to return schema database for input schema name

    Args:
        schema_name (str): coverage db schema name

    Returns:
        database session: Database session for input schema
    """
    schema_db_engine = create_engine(
        settings.DATABASE_URL,
        echo=True,
        execution_options={"schema_translate_map": {None: schema_name}},
    )
    schema_db = sessionmaker(autocommit=False, autoflush=False, bind=schema_db_engine)
    schema_db = schema_db()
    return schema_db
