import json
from fastapi import APIRouter, Request, HTTPException

import models
import utilities

router = APIRouter()

@router.post("/enrich_map/", tags=["Services"])
async def enrich_map(info: models.EnrichMap, request: Request):
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