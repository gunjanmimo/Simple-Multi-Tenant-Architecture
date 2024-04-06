# -------------------------------- PYTHON IMPORTS --------------------------------#
from typing import Union, Dict
from datetime import datetime, timedelta

# -------------------------------- FASTAPI IMPORTS --------------------------------#
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# -------------------------------- JWT IMPORTS --------------------------------#
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError

# -------------------------------- LOCAL IMPORTS --------------------------------#
from security import settings


# password hash manager
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
# authentication scheme
auth_scheme = HTTPBearer()

# ======================= password authentication ========================== #
def generate_password_hash(password: str) -> str:
    """
    HELPER FUNCTION TO  GENERATE PASSWORD HASH
    Args:
        password (str): PASSWORD

    Returns:
        str: HASHED PASSWORD
    """
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    HELPER FUNCTION TO VALIDATE HASHED PASSWORD

    Args:
        plain_password (str): USER INPUT PASSWORD
        hashed_password (str): STORED HASHED PASSWORD

    Returns:
        bool: IS INPUT PASSWORD MATCHES WITH SAVED HASHED PASSWORD
    """
    return PWD_CONTEXT.verify(plain_password, hashed_password)


# ======================= token authentication ========================== #
def generate_access_token(user_id: str) -> str:
    """
    HELPER FUNCTION TO  GENERATE ACCESS TOKEN

    Args:
        user_id (str): USER EMAIL ID

    Returns:
        str: BEARER ACCESS TOKEN
    """

    lifetime = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + lifetime
    payload = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "user_id": user_id,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    """
    HELPER FUNCTION TO  DECODE ACCESS TOKEN

    Args:
        token (str): BEARER ACCESS TOKEN
    Returns:
        str: USER EMAIL ID
    """
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(401, detail="Invalid Token")
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(401, detail="Token is expired")
    except JWTError:
        raise HTTPException(401, detail="Invalid Token")


# ======================= user authentication ========================== #
def validate_is_user_valid(token: str, is_admin_validation: bool = False):
    return
