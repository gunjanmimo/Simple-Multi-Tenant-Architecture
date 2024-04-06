# -------------------------------- FASTAPI IMPORTS --------------------------------#
from fastapi import HTTPException

# -------------------------------- SQL ALCHEMY  IMPORTS --------------------------------#
from sqlalchemy.orm import Session

# -------------------------------- LOCAL IMPORTS --------------------------------#
from models.common_models import Coverage
from models.coverage_models import Sensor, SensorReading, Sink
from database import engine


def create_coverage(name: str, db: Session):
    if db.query(Coverage).filter(Coverage.name == name).first():
        raise HTTPException(
            status_code=404, detail=f"Coverage with name {name} exists in database !"
        )
    db_coverage_object = Coverage(name=name)
    db.add(db_coverage_object)
    db.commit()
    db.refresh(db_coverage_object)
    # create db schema with tables
    engine.execute(f"CREATE SCHEMA IF NOT EXISTS {db_coverage_object.db_schema}")

    # Set the schema for each table class
    Sensor.__table__.schema = db_coverage_object.db_schema
    SensorReading.__table__.schema = db_coverage_object.db_schema
    Sink.__table__.schema = db_coverage_object.db_schema

    # Create the tables for the tenant schema
    Sensor.__table__.create(bind=engine)
    SensorReading.__table__.create(bind=engine)
    Sink.__table__.create(bind=engine)

    # set table schema to none
    Sensor.__table__.schema = None
    SensorReading.__table__.schema = None
    Sink.__table__.schema = None

    return db_coverage_object.id, db_coverage_object.db_schema
