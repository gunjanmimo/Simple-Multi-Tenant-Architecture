# -------------------------------- PYTHON IMPORTS --------------------------------#
import os
import pathlib
from pydantic import BaseSettings


# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)


class Settings(BaseSettings):
    # Token
    JWT_SECRET                   : str   
    ALGORITHM                    : str   
    ACCESS_TOKEN_EXPIRE_MINUTES  : int
    
    # Database
    DATABASE_URL                  : str
    DB_ECHO                       : str
    PUBLIC_TENANT_SCHEMA          : str
    class Config:
        case_sensitive  =  True
        env_file        =  ".env"
        
settings = Settings()
settings.DB_ECHO = eval(settings.DB_ECHO)