# -------------------------------- PYTHON IMPORTS --------------------------------#
from pydantic import BaseModel


class UserCreationPayload(BaseModel):
    email_id: str
    password: str
    coverage_id: str


class UserLoginPayload(BaseModel):
    email_id: str
    password: str
class ChangePermissionPayload(BaseModel):
    coverage_id: str                 = None
    is_admin:bool                    = None