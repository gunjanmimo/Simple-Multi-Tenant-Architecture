# -------------------------------- PYTHON IMPORTS --------------------------------#
from datetime import datetime
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_Intersects, ST_GeomFromText, ST_SetSRID
from geoalchemy2.elements import WKBElement

# -------------------------------- SQL ALCHEMY  IMPORTS --------------------------------#
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

# -------------------------------- FASTAPI IMPORTS --------------------------------#
from fastapi import APIRouter, Depends, status, HTTPException, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# -------------------------------- LOCAL IMPORTS --------------------------------#
from routes.coverage import schemas as payload_schemas
from database import get_public_schema_db, get_schema_db
from security import authenticator
from models.common_models import User, Coverage
from models.coverage_models import Sensor, SensorReading, Sink
from routes.coverage import utils

coverage_route = APIRouter(tags=["coverage"])


@coverage_route.post("/coverage")
def create_coverage(
    payload: payload_schemas.CoverageCreationPayload,
    db: Session = Depends(get_public_schema_db),
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
):
    """
    Create a new coverage.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Args:
        payload (payload_schemas.CoverageCreationPayload): The payload containing the data to create a coverage.
        db (Session): The database session to use for the operation.
        token (HTTPAuthorizationCredentials): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function.

    Returns:
        success message.

    Raises:
        HTTPException: If the payload is invalid or if the user is not authorized to create a new coverage.

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
    utils.create_coverage(name=payload.name, db=db)
    return {
        "status": "success",
        "message": f"Coverage created with name {payload.name}",
    }


@coverage_route.get("/coverage")
def get_coverages(
    db: Session = Depends(get_public_schema_db),
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
):
    """
    Get all available coverages.


    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Args:
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        list[dict]: A list of dictionaries, each representing a coverage with its details.

    Raises:
        HTTPException: If the user is not authorized to view the coverages or if there is an error retrieving the data from the database.
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
    all_coverage = db.query(Coverage).all()
    return all_coverage


@coverage_route.delete("/coverage/{name}")
def delete_coverage(
    name: str,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    Delete an existing coverage by name.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Only admin user

    Args:
        name (str): The name of the coverage to be deleted.
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        dict: A dictionary containing a success message indicating that the coverage has been deleted.

    Raises:
        HTTPException: If the user is not authorized to delete a coverage, if the specified coverage does not exist in the database, or if there is an error deleting the coverage from the database.
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

    coverage_db = db.query(Coverage).filter(Coverage.name == name).first()
    if not coverage_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not coverage exists with name {name}",
        )

    db.delete(coverage_db)
    db.commit()
    return {"status": "failed", "message": f"{name} coverage deleted successfully !!"}


@coverage_route.get("/coverage/{name}/sensor")
def get_sensor_data(
    name: str,
    payload: payload_schemas.FilterPayload,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    Retrieve sensor data for a coverage.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Admin user and user associated with `name` coverage

    Args:
        name (str): The name of the coverage for which to retrieve sensor data.
        payload (FilterPayload): A payload object that contains filters to be applied on the sensor data.
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        list[dict]: A list of dictionary objects containing sensor data for the given coverage. The list contains a maximum of 5 items.

    Raises:
        HTTPException: If the user is not authorized to access sensor data for the coverage, or if there is an error retrieving the sensor data from the database.
    """
    # user authentication
    user_id = authenticator.decode_token(token=token.credentials)
    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        return HTTPException(status_code=400, detail="Not a valid token !!")

    coverage_db_object = db.query(Coverage).filter(Coverage.name == name).first()
    if not coverage_db_object:
        return HTTPException(status_code=400, detail="Not a valid coverage name !!")
    if user_db_object.is_admin:
        pass
    else:
        coverage_id = user_db_object.coverage_id
        if coverage_id != coverage_db_object.id:
            return HTTPException(
                status_code=400, detail="Not authorized to perform this action!!"
            )

    # get sensor data
    page_no = 0 if payload.page_no is None else payload.page_no
    schema_db = get_schema_db(schema_name=coverage_db_object.db_schema)

    # db_object = schema_db.query(SensorReading).limit(5).offset(page_no).all()
    db_object = (
        schema_db.query(SensorReading)
        .options(joinedload(SensorReading.sensor))
        .limit(5)
        .offset(page_no)
        .all()
    )

    for x in db_object:
        if isinstance(x.sensor.geometry, WKBElement):
            geometry = to_shape(x.sensor.geometry)
            x.sensor.geometry = str(geometry)
        else:
            x.sensor.geometry = str(x.sensor.geometry)

    return db_object


@coverage_route.get("/coverage/{name}/sensor/filter")
def filter_sensor_data(
    name: str,
    payload: payload_schemas.FilterPayload,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):
    """
    API endpoint to filter sensor data based on date(YYYYMMDDHHMM) and Ploygon Geometry.
    This API sends data in paginated manner and at a time it sends max 5 sensors' data.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Admin user and user associated with `name` coverage

    Args:
        name (str): The name of the coverage for which to retrieve sensor data.
        payload (FilterPayload): A payload object that contains filters to be applied on the sensor data.
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        list[dict]: A list of dictionary objects containing sensor data for the given coverage. The list contains a maximum of 5 items.

    Raises:
        HTTPException: If the user is not authorized to access sensor data for the coverage, or if there is an error retrieving the sensor data from the database.
    """

    # user authentication
    user_id = authenticator.decode_token(token=token.credentials)
    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        return HTTPException(status_code=400, detail="Not a valid token !!")

    coverage_db_object = db.query(Coverage).filter(Coverage.name == name).first()
    if not coverage_db_object:
        return HTTPException(status_code=400, detail="Not a valid coverage name !!")

    if user_db_object.is_admin:
        pass
    else:
        coverage_id = user_db_object.coverage_id
        if coverage_id != coverage_db_object.id:
            return HTTPException(
                status_code=400, detail="Not authorized to perform this action!!"
            )

    # filter
    if not payload.polygon and not payload.start_time and not payload.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a valid payload to filter data !!",
        )
    # get schema db
    schema_db = get_schema_db(schema_name=coverage_db_object.db_schema)
    # Define the query filters
    filters = []
    # query based on start and end datetime
    if payload.start_time and payload.end_time:
        start_time = datetime.strptime(payload.start_time, "%Y%m%d%H%M%S").isoformat()
        end_time = datetime.strptime(payload.end_time, "%Y%m%d%H%M%S").isoformat()
        filters.append(SensorReading.date_time >= start_time)
        filters.append(SensorReading.date_time <= end_time)
    if payload.polygon:
        polygon_wkt = payload.polygon
        polygon_geom = ST_SetSRID(ST_GeomFromText(polygon_wkt), 4326)
        filters.append(ST_Intersects(Sensor.geometry, polygon_geom))
    # return start_time, end_time
    page_no = 0 if payload.page_no is None else payload.page_no

    # Construct the query
    query = (
        schema_db.query(SensorReading)
        .select_from(Sensor)
        .join(SensorReading, Sensor.id == SensorReading.device_id)
        .filter(and_(*filters))
        .limit(5)
        .offset(page_no)
    )
    # Execute the query and fetch the results
    db_object = query.all()

    # process geometry type data
    for x in db_object:
        if isinstance(x.sensor.geometry, WKBElement):
            geometry = to_shape(x.sensor.geometry)
            x.sensor.geometry = str(geometry)
        else:
            x.sensor.geometry = str(x.sensor.geometry)

    return db_object


@coverage_route.get("/coverage/{name}/sinks")
def get_sink_data(
    name: str,
    payload: payload_schemas.FilterPayload,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):

    """
    API endpoint to get sink data. This API sends data in paginated manner and at a time it sends max 5 sinks' data.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Admin user and user associated with `name` coverage

    Args:
        name (str): The name of the coverage for which to retrieve sensor data.
        payload (FilterPayload): A payload object that contains filters to be applied on the sensor data.
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        list[dict]: A list of dictionary objects containing sensor data for the given coverage. The list contains a maximum of 5 items.

    Raises:
        HTTPException: If the user is not authorized to access sensor data for the coverage, or if there is an error retrieving the sensor data from the database.
    """
    # user authentication
    user_id = authenticator.decode_token(token=token.credentials)
    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        return HTTPException(status_code=400, detail="Not a valid token !!")
    coverage_db_object = db.query(Coverage).filter(Coverage.name == name).first()
    if not coverage_db_object:
        return HTTPException(status_code=400, detail="Not a valid coverage name !!")

    if user_db_object.is_admin:
        pass
    else:
        coverage_id = user_db_object.coverage_id
        if coverage_id != coverage_db_object.id:
            return HTTPException(
                status_code=400, detail="Not authorized to perform this action!!"
            )

    # get sensor data
    page_no = 0 if payload.page_no is None else payload.page_no
    schema_db = get_schema_db(schema_name=coverage_db_object.db_schema)
    db_object = schema_db.query(Sink).limit(5).offset(page_no).all()
    for x in db_object:
        x.geometry = to_shape(x.geometry).wkt
    return db_object


@coverage_route.get("/coverage/{name}/sinks/filter")
def filter_sink_data(
    name: str,
    payload: payload_schemas.FilterPayload,
    token: HTTPAuthorizationCredentials = Depends(authenticator.auth_scheme),
    db: Session = Depends(get_public_schema_db),
):

    """
    API endpoint to get sink data. This API sends data in paginated manner and at a time it sends max 5 sinks' data.

    Authentication:
    - JWT Bearer token

    Permissions:
    - Admin user and user associated with `name` coverage

    Args:
        name (str): The name of the coverage for which to retrieve sensor data.
        payload (FilterPayload): A payload object that contains filters to be applied on the sensor data.
        db (Session, optional): The database session to use for the operation. Defaults to Depends(get_db).
        token (HTTPAuthorizationCredentials, optional): The JWT Bearer token obtained from the `authenticator.auth_scheme` dependency function. Defaults to Depends(auth_scheme).

    Returns:
        list[dict]: A list of dictionary objects containing sensor data for the given coverage. The list contains a maximum of 5 items.

    Raises:
        HTTPException: If the user is not authorized to access sensor data for the coverage, or if there is an error retrieving the sensor data from the database.
    """
    # user authentication
    user_id = authenticator.decode_token(token=token.credentials)
    user_db_object = db.query(User).filter(User.id == user_id).first()
    if not user_db_object:
        return HTTPException(status_code=400, detail="Not a valid token !!")
    coverage_db_object = db.query(Coverage).filter(Coverage.name == name).first()
    if not coverage_db_object:
        return HTTPException(status_code=400, detail="Not a valid coverage name !!")

    if user_db_object.is_admin:
        pass
    else:
        coverage_id = user_db_object.coverage_id
        if coverage_id != coverage_db_object.id:
            return HTTPException(
                status_code=400, detail="Not authorized to perform this action!!"
            )

    # get sensor data
    if not payload.polygon and not payload.start_time and not payload.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a valid payload to filter data !!",
        )

    # get schema db
    schema_db = get_schema_db(schema_name=coverage_db_object.db_schema)
    page_no = 0 if payload.page_no is None else payload.page_no

    # Define the query filters
    filters = []
    # query based on start and end datetime
    if payload.start_time and payload.end_time:

        start_time = (
            datetime.strptime(payload.start_time, "%Y%m%d%H%M%S")
            .isoformat()
            .replace("T", " ")
        )
        end_time = (
            datetime.strptime(payload.end_time, "%Y%m%d%H%M%S")
            .isoformat()
            .replace("T", " ")
        )

        filters.append(Sink.date_time >= start_time)
        filters.append(Sink.date_time <= end_time)
    # query based on polygon
    if payload.polygon is not None:
        polygon_wkt = payload.polygon
        polygon_geom = ST_SetSRID(ST_GeomFromText(polygon_wkt), 4326)
        filters.append(ST_Intersects(Sink.geometry, polygon_geom))
    # Construct the query
    query = schema_db.query(Sink).filter(and_(*filters)).limit(5).offset(page_no)

    # Execute the query and fetch the results
    db_object = query.all()
    # process geometry type data
    for x in db_object:
        x.geometry = to_shape(x.geometry).wkt
    return db_object
