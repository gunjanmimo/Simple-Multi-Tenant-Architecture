"""
    DATA SEEDER FILE WILL STORE AVAILABLE DATA INTO DATABASE ON STARTING OF THE SERVER
    
    1. ADMIN 
        Admin will be created on starting server
        admin credentials:
            email_id: admin@everimpact.com
            password: admin@everimpact
            
    2. COVERAGE
        We have two known coverage 1. Dijon 2. Ishinomaki. On starting of the server,
        we will upload data into their own database schemas
        
        
        Schema will have two table
            1. SENSOR
            2. SINK
            
        On creating all new coverage we will create a database schema with above two tables
        
"""
# -------------------------------- PYTHON IMPORTS --------------------------------#
import pandas as pd
import geopandas as gpd
import time

# -------------------------------- ALEMBIC IMPORTS --------------------------------#
from alembic.config import Config
from alembic import command

# -------------------------------- LOCAL IMPORTS --------------------------------#
from database import SessionLocal, engine, Base
from models import common_models
from routes.coverage.utils import create_coverage
from database import SessionLocal


# DATABASE SESSION
db = SessionLocal()

# Alembic configuration file path
alembic_cfg = "alembic.ini"


def run_migration():
    alembic_config = Config(alembic_cfg)
    command.upgrade(alembic_config, "head")


def create_admin():
    try:
        admin_user_db_obj = common_models.User(
            email_id="admin@everimpact.com",
            password="admin@everimpact",
            is_admin=True,
        )
        db.add(admin_user_db_obj)
        db.commit()
    except Exception as error:
        pass


def create_default_migration():
    print("-" * 100)
    print("DATA SEEDING STARTED !!\nIT WILL TAKE SOME TIME...")
    print("-" * 100)

    print("DIJON COVERAGE DATA SEEDING ..............\n")
    # dijon schema
    dijon_start_time = time.time()
    _, dijon_schema = create_coverage(name="Dijon", db=SessionLocal())
    # read data files
    sensor_data = gpd.read_file("data_seeder/data/dijon_sensor_data.geojson")
    sensor_data.to_postgis(
        con=engine,
        name="sensor",
        schema=dijon_schema,
        index=False,
        if_exists="append",
        dtype={"geometry": "Geometry"},
    )

    sensor_reading_data = pd.read_csv("data_seeder/data/dijon_sensor_reading_data.csv")
    sensor_reading_data.to_sql(
        con=engine,
        name="sensor_reading",
        schema=dijon_schema,
        index=False,
        if_exists="append",
    )
    # ishinomaki schema
    print("ISHINOMAKI COVERAGE DATA SEEDING ..............\n")
    _, ishinomaki_schema = create_coverage(name="Ishinomaki", db=SessionLocal())
    sink_data = gpd.read_file("data_seeder/data/ishinomaki_sink.geojson")
    sink_data.to_postgis(
        con=engine,
        name="sink",
        schema=ishinomaki_schema,
        index=False,
        if_exists="append",
        dtype={"geometry": "Geometry"},
    )


def start_data_seeding():

    try:
        # add Postgis support
        engine.execute("CREATE EXTENSION Postgis;")
        # run migration
        # run_migration()
    except:
        pass

    # create default schema and upload data
    try:
        create_default_migration()
    except Exception as error:
        print("-" * 100)
        print("SOMETHING WENT WRONG WHILE CREATING DEFAULT COVERAGE")
        print("~" * 30)
        print(str(error))
        print("~" * 30)
        print("-" * 100)

    # CREATE ADMIN USER
    create_admin()
