from pydantic import BaseModel


class CoverageCreationPayload(BaseModel):
    name: str


class FilterPayload(BaseModel):
    start_time: str = None
    end_time: str = None
    page_no: int = None
    polygon: str = None
