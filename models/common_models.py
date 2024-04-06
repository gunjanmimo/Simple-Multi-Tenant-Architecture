# -------------------------------- SQL ALCHEMY IMPORTS --------------------------------#
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, String, ForeignKey

# -------------------------------- LOCAL IMPORTS --------------------------------#
from database import Base
from models.utils import get_random_uuid_string

# COVERAGE IS TENANT IN THIS SYSTEM
"""
    ADMIN HAS ACCESS TO ALL THE COVERAGE 
    OTHER USER CAN ACCESS ONLY IT'S ASSIGNED COVERAGE
"""


class Coverage(Base):
    __tablename__ = "coverage"
    id = Column(
        String(50),
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        default=get_random_uuid_string,
    )
    name = Column(String(50), unique=True)
    db_schema = Column(
        String,
        unique=True,
        default=lambda x: "schema_" + get_random_uuid_string(),
    )
    user = relationship("User", backref="coverage")


class User(Base):
    __tablename__ = "user"
    id = Column(
        String(50),
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        default=get_random_uuid_string,
    )
    email_id = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    coverage_id = Column(String(50), ForeignKey("coverage.id"), nullable=True)
