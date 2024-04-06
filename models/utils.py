# -------------------------------- PYTHON IMPORTS --------------------------------#
import uuid


def get_random_uuid_string():
    """_summary_
    Helper function to generate random uuid string for primary key
    Returns:
        _type_:str = randomly generate UUID string
    """
    uuid_string = str(uuid.uuid4())
    simple_uuid_string = uuid_string.replace("-", "")
    return simple_uuid_string
