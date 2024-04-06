# -------------------------------- SQL ALCHEMY IMPORTS --------------------------------#
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, Float, Integer, DateTime, BIGINT
from geoalchemy2 import Geometry

# -------------------------------- LOCAL IMPORTS --------------------------------#
from database import Base
from models.utils import get_random_uuid_string


class Sensor(Base):
    __tablename__ = "sensor"
    # sensor id-> device id
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
    )

    fid = Column(Integer)
    xcoord = Column(Float)
    ycoord = Column(Float)
    zcoord = Column(Float)
    geometry = Column(Geometry("POINTZ", dimension=3, srid=4326))
    sensor_reading = relationship("SensorReading", backref="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_reading"
    id = Column(
        String(50),
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        default=get_random_uuid_string,
    )
    fid_measurement = Column(Integer)
    oid = Column(String(50))
    date_time = Column(DateTime)
    value_payload = Column(String(100))
    device_id = Column(Integer, ForeignKey("sensor.id"))
    protocol_version = Column(Integer)
    air_temperature_value = Column(Float)
    air_temperature_unit = Column(String(50))
    air_humidity_value = Column(Float)
    air_humidity_unit = Column(String(50))
    barometer_temperature_value = Column(Float)
    barometer_temperature_unit = Column(String(50))
    barometric_pressure_value = Column(Integer)
    barometric_pressure_unit = Column(String(50))
    co2_concentration_value = Column(Integer)
    co2_concentration_unit = Column(String(50))
    co2_concentration_lpf_value = Column(Integer)
    co2_concentration_lpf_unit = Column(String(50))
    co2_sensor_temperature_value = Column(Float)
    co2_sensor_temperature_unit = Column(String(50))
    capacitor_voltage_1_value = Column(Float)
    capacitor_voltage_1_unit = Column(String(50))
    capacitor_voltage_2_value = Column(Float)
    capacitor_voltage_2_unit = Column(String(50))
    co2_sensor_status_value = Column(Integer, nullable=True)
    co2_sensor_status_unit = Column(String(50))
    raw_ir_reading_value = Column(Integer, nullable=True)
    raw_ir_reading_unit = Column(String(50), nullable=True)
    raw_ir_reading_lpf_value = Column(Integer)
    raw_ir_reading_lpf_unit = Column(String(50), nullable=True)
    battery_voltage_value = Column(Float)
    battery_voltage_unit = Column(String(50))


class Sink(Base):
    __tablename__ = "sink"
    id = Column(
        String(50),
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        default=get_random_uuid_string,
    )
    parcel_id = Column(String(50))
    date_time = Column(DateTime)
    specie = Column(String(50))
    age = Column(Integer)
    area = Column(Integer)
    ndvi_nocloud = Column(Integer, nullable=True)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=True)
    co2removed = Column(Integer, nullable=True)
    co2balance = Column(BIGINT, nullable=True)
    co2emitted = Column(BIGINT, nullable=True)
    colonna = Column(BIGINT, nullable=True)
