from pydantic import BaseModel, Field
from typing import List, Optional, Literal, NamedTuple, Union
from typing_extensions import Annotated

class Variable(BaseModel):
    table: str
    column: str
    type: Literal['min','max','sum','avg','count']
    influence: Literal['low','high','ideal']
    weight: int
    ideal_value: float=0

class MapSuitability(BaseModel):
    table: str
    table_column: str
    table_values: list=[]
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False
    filter: str=""

class Point(BaseModel):
    latitude: float
    longitude: float

class PointSuitability(BaseModel):
    points: List[Point]
    buffer_in_kilometers: float
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False

LonField = Annotated[
    Union[float, int],
    Field(
        title='Coordinate longitude',
        gt=-180,
        lt=180,
    ),
]

LatField = Annotated[
    Union[float, int],
    Field(
        title='Coordinate latitude',
        gt=-90,
        lt=90,
    ),
]

class Coordinates(NamedTuple):
    lon: LonField
    lat: LatField
    
class PolygonGeometry(BaseModel):
    type: Literal['Polygon']
    coordinates: List[List[Coordinates]]

class LineGeometry(BaseModel):
    type: Literal['LineString']
    coordinates: List[Coordinates]

class PolygonGeojson(BaseModel):
    type: str="Feature"
    geometry: PolygonGeometry   

class LineGeojson(BaseModel):
    type: str="Feature"
    geometry: LineGeometry   

class PolygonGeojsonCollection(BaseModel):
    type: str="FeatureCollection"
    features: List[PolygonGeojson]

class LineGeojsonCollection(BaseModel):
    type: str="FeatureCollection"
    features: List[LineGeojson]

class PolygonSuitability(BaseModel):
    geojson_collection: PolygonGeojsonCollection
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False

class LineSuitability(BaseModel):
    geojson_collection: LineGeojsonCollection
    buffer_in_kilometers: float
    variables: Optional[List[Variable]]=[]
    return_geometry: bool=False