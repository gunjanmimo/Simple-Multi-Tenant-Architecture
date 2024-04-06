# -------------------------------- PYTHON IMPORTS --------------------------------#
# -------------------------------- FASTAPI IMPORTS --------------------------------#
from fastapi import APIRouter, Depends, status, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# -------------------------------- SQL ALCHEMY  IMPORTS --------------------------------#
from sqlalchemy.orm import Session

# -------------------------------- LOCAL IMPORTS --------------------------------#
from routes.user import schemas as payload_schemas
from database import get_public_schema_db
from models.common_models import User, Coverage
from security import authenticator


# user route to handle user related end-points
user_route = APIRouter(tags=["USER"])


@user_route.post("/users")
def create_user(
    payload: payload_schemas.UserCreationPayload,
    db: Session = Depends(get_public_schema_db),
):
    """
    Create a new user.

    Args:
        payload: The user creation payload, containing the user's ``email id``, ``password`` and ``coverage_id``.
        db: The database session to use for the operation.

    Returns:
        user access token

    Raises:
        HTTPException: If the payload is invalid or if the user already exists.
    """

    # check if email id is already registered
    if db.query(User).filter(User.email_id == payload.email_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{payload.email_id} is already used !",
        )
    # check given coverage is already exist or not
    if not db.query(Coverage).filter(Coverage.id == payload.coverage_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coverage with id {payload.coverage_id} does not exist !!",
        )

    user_db = User(
        email_id=payload.email_id,
        password=payload.password,  # not using hashed password for simplicity
        coverage_id=payload.coverage_id,
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    # generate access token
    access_token = authenticator.generate_access_token(user_id=user_db.id)

    return {
        "status": "success",
        "message": "user created successfully",
        "access_token": access_token,
    }


@user_route.get("/users/login")
def user_login(
    payload: payload_schemas.UserLoginPayload,
    db: Session = Depends(get_public_schema_db),
):
    """
    Authenticate a user and generate an access token.

    Args:
        payload: The user login payload, containing the user's credentials.
        db: The database session to use for the operation.

    Returns:
        A dictionary containing the access token.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    user_db_object = db.query(User).filter(User.email_id == payload.email_id).first()
    if not user_db_object:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad credentials !!",
        )

    password = user_db_object.password
    if password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad credentials !!",
        )

    return {
        "status": "success",
        "token": authenticator.generate_access_token(user_id=user_db_object.id),
    }


@user_route.get("/users/me")
def get_user_credentials(
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    Get the current user's credentials.

    This endpoint can be used as a forgot password feature. The user will receive an access token that can be used to recover their email and password.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Valid user

    Returns:
    A dictionary containing the email and password for the current user.

    Raises:
    HTTPException: If the access token is invalid or the user is not authorized.
    """

    token = token.credentials
    user_id = authenticator.decode_token(token=token)

    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        raise HTTPException(status_code=400, detail="User Not found !!")
    return {
        "status": "success",
        "credentials": {
            "email": user_db_object.email_id,
            "password": user_db_object.password,
        },
    }


@user_route.get("/users/all")
def get_all_users(
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    List all users in the database.

    This API endpoint allows users with admin access to list all the users in the database.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Returns:
    A list of dictionaries containing the email and user ID for each user in the database.

    Raises:
    HTTPException: If the user is not authorized to perform this action.
    """

    token = token.credentials
    admin_user_id = authenticator.decode_token(token=token)
    if (
        not db.query(User)
        .filter(User.id == admin_user_id, User.is_admin == True)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized !!"
        )

    all_user = [
        {"email_id": x.email_id, "id": x.id}
        for x in db.query(User).filter(User.is_admin == False).all()
    ]

    return {"status": "success", "data": all_user}


@user_route.put("/users/{user_id}")
def update_coverage_access(
    user_id: str,
    payload: payload_schemas.ChangePermissionPayload,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    Update a user's permission.

    This API endpoint changes a user's permission by assigning them admin access or access to a specific coverage. It takes the user ID as input.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Parameters:
    - user_id (str): The ID of the user whose permission is being updated.
    - payload (payload_schemas.ChangePermissionPayload): The payload containing the updated permission details.

    Returns:
    A dictionary containing a success message.

    Raises:
    HTTPException: If the user is not authorized to perform this action, if the user ID is invalid, or if the payload is missing required fields.
    """

    token = token.credentials
    admin_user_id = authenticator.decode_token(token=token)
    if (
        not db.query(User)
        .filter(User.id == admin_user_id, User.is_admin == True)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized !!"
        )

    user_object = db.query(User).filter(User.id == user_id).first()
    if not user_object:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {user_id} does not exist !!",
        )

    if payload.is_admin:
        # change permission to admin
        user_object.is_admin = True
    elif payload.coverage_id:
        # change permission to given coverage
        user_object.coverage_id = payload.coverage_id
    else:
        # wrong payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong permission update details !!",
        )
    db.commit()

    return {"status": "success", "message": "User access changed !!"}


@user_route.delete("/users/{user_id}")
def get_all_users(
    user_id: str,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    Delete a user from the database.

    This API endpoint deletes a user with the given user ID from the User database.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Parameters:
    - user_id (str): The ID of the user to be deleted.

    Returns:
    A dictionary containing a success message.

    Raises:
    HTTPException: If the user is not authorized to perform this action or if the user ID is invalid.
    """
    admin_user_id = authenticator.decode_token(token=token.credentials)
    if (
        not db.query(User)
        .filter(User.id == admin_user_id, User.is_admin == True)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token !!"
        )
    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        raise HTTPException(status_code=400, detail="Not a valid user id !!")
    db.delete(user_db_object)
    db.commit()
    return {
        "status": "success",
        "message": f"User with id {user_id} deleted from database !",
    }
