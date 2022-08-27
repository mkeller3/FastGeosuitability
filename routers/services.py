import json
from fastapi import APIRouter, Request, HTTPException
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse

import models
import utilities

router = APIRouter()

@router.post("/map_suitability/", tags=["Services"])
async def map_suitability(info: models.MapSuitability, request: Request):
    """
    Method to enrich map with suitability metrics

    """

    geojson_collection = {
        "type": "FeatureCollection",
        "features": []
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        query = f"""
            SELECT a."{info.table_column}",
        """

        if info.return_geometry:
            query += f"""ST_AsGeoJSON(geom) as geometry"""
        else:
            query += f"""null as geometry"""

        query += f""" FROM "{info.table}" as a """

        if info.table_values != []:
            values = "','".join(info.table_values)
            query += f""" WHERE {info.table_column} in ('{values}')"""
        
        if info.table_values == [] and info.cql_filter != "":
            sql_field_query = f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{info.table}'
                AND column_name != 'geom';
            """

            field_mapping = {}

            db_fields = await con.fetch(sql_field_query)

            for field in db_fields:
                field_mapping[field['column_name']] = field['column_name']

            ast = parse(info.cql_filter)
            where_statement = to_sql_where(ast, field_mapping)

            query += f" WHERE {where_statement}"

        features = await con.fetch(query)

        for feature in features:
            if info.return_geometry:
                geojson_collection['features'].append({
                    "type": "Feature",
                    "geometry": json.loads(feature['geometry']),
                    "properties": {info.table_column: feature[info.table_column]}
                })
            else:
                geojson_collection['features'].append({
                    "type": "Feature",
                    "geometry": None,
                    "properties": {info.table_column: feature[info.table_column]}
                })

        if info.variables != []:
            total_weight = 0
            for variable in info.variables:
                total_weight += variable.weight
            if total_weight < 100:
                raise HTTPException(status_code=400, detail="Total weights do not add up to 100. Add more weight to your variables to equal 100.")            
            if total_weight > 100:
                raise HTTPException(status_code=400, detail="Total weights add up to over 100. Add less weight to your variables to equal 100.")
            for variable in info.variables:
                geometry_query = f"""
                    SELECT ST_GeometryType(geom) as geometry_type
                    FROM "{variable.table}" 
                    LIMIT 1
                """

                geometry_type = await con.fetchrow(geometry_query)

                if 'Polygon' in geometry_type['geometry_type']:
                    query = f"""
                        SELECT b."{info.table_column}", {variable.type}(CAST(a."{variable.column}" * (ST_Area(st_intersection(a.geom, b.geom)) / ST_Area(a.geom)) as integer)) as {variable.type}_{variable.column}
                        FROM {variable.table} as a, {info.table} as b
                        WHERE ST_Intersects(b.geom, a.geom)
                    """
                else:
                    query = f"""
                        SELECT b."{info.table_column}", {variable.type}(a."{variable.column}") as {variable.type}_{variable.column}
                        FROM {variable.table} as a, {info.table} as b
                        WHERE ST_Intersects(b.geom, a.geom)
                    """
                
                if info.table_values != []:
                    values = "','".join(info.table_values)
                    query += f""" AND b."{info.table_column}" in ('{values}')"""
                
                if info.table_values == [] and info.cql_filter != "":
                    sql_field_query = f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = '{info.table}'
                        AND column_name != 'geom';
                    """

                    field_mapping = {}

                    db_fields = await con.fetch(sql_field_query)

                    for field in db_fields:
                        field_mapping[field['column_name']] = field['column_name']

                    ast = parse(info.cql_filter)
                    where_statement = to_sql_where(ast, field_mapping)

                    query += f" AND {where_statement}"
                
                query += f""" GROUP BY b."{info.table_column}" """

                features = await con.fetch(query)

                for geo_feature in features:
                    feature_index = [feature['properties'][info.table_column] for feature in geojson_collection['features']].index(geo_feature[info.table_column])
                    geojson_collection['features'][feature_index]['properties'][f"{variable.table}_{variable.type}_{variable.column}"] = geo_feature[f"{variable.type}_{variable.column}"]

            geojson_collection = utilities.get_final_scores(
                geojson_collection=geojson_collection,
                variables=info.variables
            )

        return geojson_collection

@router.post("/point_suitability/", tags=["Services"])
async def point_suitability(info: models.PointSuitability, request: Request):
    """
    Method to enrich map with suitability metrics

    """

    geojson_collection = {
        "type": "FeatureCollection",
        "features": []
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        for point in info.points:

            query = f"""
                SELECT 
            """

            if info.return_geometry:
                query += f""" ST_AsGeoJSON(ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({point.longitude}, {point.latitude}),4326),3857), {info.buffer_in_kilometers*1000}),4326)) as geometry"""
            else:
                query += f"""null as geometry"""

            features = await con.fetch(query)

            for feature in features:
                if info.return_geometry:
                    geojson_collection['features'].append({
                        "type": "Feature",
                        "geometry": json.loads(feature['geometry']),
                        "properties": {
                            "longitude": point.longitude,
                            "latitude": point.latitude
                        }
                    })
                else:
                    geojson_collection['features'].append({
                        "type": "Feature",
                        "geometry": None,
                        "properties": {
                            "longitude": point.longitude,
                            "latitude": point.latitude
                        }
                    })

            if info.variables != []:
                total_weight = 0
                for variable in info.variables:
                    total_weight += variable.weight
                if total_weight < 100:
                    raise HTTPException(status_code=400, detail="Total weights do not add up to 100. Add more weight to your variables to equal 100.")            
                if total_weight > 100:
                    raise HTTPException(status_code=400, detail="Total weights add up to over 100. Add less weight to your variables to equal 100.")
                for variable in info.variables:
                    geometry_query = f"""
                        SELECT ST_GeometryType(geom) as geometry_type
                        FROM "{variable.table}" 
                        LIMIT 1
                    """

                    geometry_type = await con.fetchrow(geometry_query)

                    if 'Polygon' in geometry_type['geometry_type']:
                        query = f"""
                            SELECT CAST({point.latitude} as double precision) as latitude, {variable.type}(CAST(a."{variable.column}" * (ST_Area(st_intersection(a.geom, b.geom)) / ST_Area(a.geom)) as integer)) as {variable.type}_{variable.column}
                            FROM {variable.table} as a, ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({point.longitude}, {point.latitude}),4326),3857), {info.buffer_in_kilometers*1000}),4326) as b
                            WHERE ST_Intersects(b, a.geom)
                        """
                    else:
                        query = f"""
                            SELECT CAST({point.latitude} as double precision) as latitude, {variable.type}(a."{variable.column}") as {variable.type}_{variable.column}
                            FROM {variable.table} as a, ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({point.longitude}, {point.latitude}),4326),3857), {info.buffer_in_kilometers*1000}),4326) as b
                            WHERE ST_Intersects(b, a.geom)
                        """
                    

                    features = await con.fetch(query)

                    for geo_feature in features:
                        feature_index = [feature['properties']['latitude'] for feature in geojson_collection['features']].index(geo_feature['latitude'])
                        geojson_collection['features'][feature_index]['properties'][f"{variable.table}_{variable.type}_{variable.column}"] = geo_feature[f"{variable.type}_{variable.column}"]

            geojson_collection = utilities.get_final_scores(
                geojson_collection=geojson_collection,
                variables=info.variables
            )

        return geojson_collection

@router.post("/polygon_suitability/", tags=["Services"])
async def polygon_suitability(info: models.PolygonSuitability, request: Request):
    """
    Method to enrich map with suitability metrics

    """

    geojson_collection = {
        "type": "FeatureCollection",
        "features": []
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        for index, polygon in enumerate(info.geojson_collection.features):

            query = f"""
                SELECT 
            """

            geojson = {
                "type": polygon.geometry.type,
                "coordinates": json.loads(json.dumps(polygon.geometry.coordinates))
            }

            if info.return_geometry:                
                query += f""" ST_AsGeoJSON(ST_GeomFromGeoJSON('{json.dumps(geojson)}')) as geometry"""
            else:
                query += f"""null as geometry"""

            features = await con.fetch(query)

            for feature in features:
                if info.return_geometry:
                    geojson_collection['features'].append({
                        "type": "Feature",
                        "geometry": json.loads(feature['geometry']),
                        "properties": {
                            "index": index
                        }
                    })
                else:
                    geojson_collection['features'].append({
                        "type": "Feature",
                        "geometry": None,
                        "properties": {
                            "index": index
                        }
                    })

            if info.variables != []:
                total_weight = 0
                for variable in info.variables:
                    total_weight += variable.weight
                if total_weight < 100:
                    raise HTTPException(status_code=400, detail="Total weights do not add up to 100. Add more weight to your variables to equal 100.")            
                if total_weight > 100:
                    raise HTTPException(status_code=400, detail="Total weights add up to over 100. Add less weight to your variables to equal 100.")
                for variable in info.variables:
                    geometry_query = f"""
                        SELECT ST_GeometryType(geom) as geometry_type
                        FROM "{variable.table}" 
                        LIMIT 1
                    """

                    geometry_type = await con.fetchrow(geometry_query)

                    if 'Polygon' in geometry_type['geometry_type']:
                        query = f"""
                            SELECT CAST({index} as integer) as index, {variable.type}(CAST(a."{variable.column}" * (ST_Area(st_intersection(a.geom, b.geom)) / ST_Area(a.geom)) as integer)) as {variable.type}_{variable.column}
                            FROM {variable.table} as a, ST_GeomFromGeoJSON('{json.dumps(geojson)}') as b
                            WHERE ST_Intersects(b, a.geom)
                        """
                    else:
                        query = f"""
                            SELECT CAST({index} as integer) as index, {variable.type}(a."{variable.column}") as {variable.type}_{variable.column}
                            FROM {variable.table} as a, ST_GeomFromGeoJSON('{json.dumps(geojson)}') as b
                            WHERE ST_Intersects(b, a.geom)
                        """
                    

                    features = await con.fetch(query)

                    for geo_feature in features:
                        feature_index = [feature['properties']['index'] for feature in geojson_collection['features']].index(geo_feature['index'])
                        geojson_collection['features'][feature_index]['properties'][f"{variable.table}_{variable.type}_{variable.column}"] = geo_feature[f"{variable.type}_{variable.column}"]

            geojson_collection = utilities.get_final_scores(
                geojson_collection=geojson_collection,
                variables=info.variables
            )

        return geojson_collection