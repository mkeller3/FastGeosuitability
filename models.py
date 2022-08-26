from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Variable(BaseModel):
    table: str
    column: str
    type: Literal['min','max','sum','avg','count']
    influence: Literal['low','high','ideal']
    weight: int
    ideal_value: float=0

class EnrichMap(BaseModel):
    table: str
    table_column: str
    table_values: list=[]
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False
    cql_filter: str

class Point(BaseModel):
    latitude: float
    longitude: float

class EnrichPoints(BaseModel):
    points: List[Point]
    buffer_in_kilometers: float
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False