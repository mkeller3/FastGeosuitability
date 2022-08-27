# FastGeosuitability

FastGeosuitability is a geosuitability api to help determine what areas are most suitable based off of a given set of variables. FastGeosuitability is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/mkeller3/FastGeosuitability" target="_blank">https://github.com/mkeller3/FastGeosuitability</a>

---

## Requirements

FastGeosuitability requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the .env with your database connections.

```
DB_HOST=localhost
DB_DATABASE=data
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.

## API

| Method | URL                                                                              | Description                                             |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `POST`  | `/api/v1/services/map_suitability/`                                             | [Map Suitability](#Map-Suitability)      |
| `POST`  | `/api/v1/services/point_suitability/`                                           | [Point Suitability](#Point-Suitability)  |
| `POST`  | `/api/v1/services/polygon_suitability/`                                         | [Polygon Suitability](#Polygon-Suitability)  |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`    |


## Map Suitability

Description

Example Input
```json
{
    "table": "counties",
    "table_column": "fips",
    "table_values": [
        "17077",
        "17043",
        "17115",
        "17097",
        "17099",
        "17111",
        "17113",
        "17001",
        "17007",
        "17019",
        "17029",
        "17031",
        ...
    ],
    "variables":[
        {
            "table": "counties",
            "column": "population",
            "type": "sum",
            "influence": "high",
            "weight": 50
        },
        {
            "table": "walmart_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 25
        },
        {
            "table": "chick_fil_a_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 25
        }
    ]
}
```

Example Response
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "fips": "17031",
                "counties_sum_population": 5313828,
                "walmart_locations_count_gid": 42,
                "chick_fil_a_locations_count_gid": 8,
                "weighted_score_counties_sum_population": 50.0,
                "weighted_score_walmart_locations_count_gid": 25.0,
                "weighted_score_chick_fil_a_locations_count_gid": 25.0,
                "final_score": 100.0
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "fips": "17043",
                "counties_sum_population": 940072,
                "walmart_locations_count_gid": 8,
                "chick_fil_a_locations_count_gid": 7,
                "weighted_score_counties_sum_population": 8.813460142972538,
                "weighted_score_walmart_locations_count_gid": 4.2682926829268295,
                "weighted_score_chick_fil_a_locations_count_gid": 21.428571428571427,
                "final_score": 34.510324254470795
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "fips": "17097",
                "counties_sum_population": 709599,
                "walmart_locations_count_gid": 9,
                "chick_fil_a_locations_count_gid": 2,
                "weighted_score_counties_sum_population": 6.643154940654739,
                "weighted_score_walmart_locations_count_gid": 4.878048780487805,
                "weighted_score_chick_fil_a_locations_count_gid": 3.571428571428571,
                "final_score": 15.092632292571116
            }
        }...
    ]
}
```

## Point Suitability

Description

Example Input
```json
{
    "points": [
        {
            "latitude": 40.45,
            "longitude": -88.95
        },
        {
            "latitude": 41.63212,
            "longitude": -87.85594
        }
    ],
    "buffer_in_kilometers": 50,
    "return_geometry": false,
    "variables":[
        {
            "table": "walmart_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 50
        },
        {
            "table": "chick_fil_a_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 50
        }
    ]
}
```

Example Response
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "longitude": -87.85594,
                "latitude": 41.63212,
                "walmart_locations_count_gid": 42,
                "chick_fil_a_locations_count_gid": 12,
                "weighted_score_walmart_locations_count_gid": 50.0,
                "weighted_score_chick_fil_a_locations_count_gid": 50.0,
                "final_score": 100.0
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "longitude": -88.95,
                "latitude": 40.45,
                "walmart_locations_count_gid": 3,
                "chick_fil_a_locations_count_gid": 2,
                "weighted_score_walmart_locations_count_gid": 0,
                "weighted_score_chick_fil_a_locations_count_gid": 0,
                "final_score": 0
            }
        }
    ]
}
```

## Polygon Suitability

Description

Example Input
```json
{
    "geojson_collection": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -88.11447143554688,
                                41.91147545749747
                            ],
                            [
                                -88.10623168945312,
                                41.85421933478601
                            ],
                            [
                                -88.06777954101562,
                                41.80919639152055
                            ],
                            [
                                -87.94830322265625,
                                41.83682786072714
                            ],
                            [
                                -87.93045043945311,
                                41.89512180073503
                            ],
                            [
                                -88.01696777343749,
                                41.92578147109541
                            ],
                            [
                                -88.11447143554688,
                                41.91147545749747
                            ]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -87.9345703125,
                                42.06560675405716
                            ],
                            [
                                -88.01422119140625,
                                42.06356771883277
                            ],
                            [
                                -87.92633056640625,
                                42.02787400232195
                            ],
                            [
                                -87.84530639648436,
                                42.01563154037739
                            ],
                            [
                                -87.82333374023438,
                                42.02991418347818
                            ],
                            [
                                -87.84393310546875,
                                42.07478160216737
                            ],
                            [
                                -87.9345703125,
                                42.06560675405716
                            ]
                        ]
                    ]
                }
            },...            
        ]
    },
    "return_geometry": false,
    "variables": [
        {
            "table": "walmart_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 50
        },
        {
            "table": "chick_fil_a_locations",
            "column": "gid",
            "type": "count",
            "influence": "high",
            "weight": 50
        }
    ]
}
```

Example Response
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "index": 0,
                "walmart_locations_count_gid": 2,
                "chick_fil_a_locations_count_gid": 3,
                "weighted_score_walmart_locations_count_gid": 25.0,
                "weighted_score_chick_fil_a_locations_count_gid": 50.0,
                "final_score": 75.0
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "index": 2,
                "walmart_locations_count_gid": 3,
                "chick_fil_a_locations_count_gid": 1,
                "weighted_score_walmart_locations_count_gid": 50.0,
                "weighted_score_chick_fil_a_locations_count_gid": 16.666666666666664,
                "final_score": 66.66666666666666
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "index": 4,
                "walmart_locations_count_gid": 2,
                "chick_fil_a_locations_count_gid": 0,
                "weighted_score_walmart_locations_count_gid": 25.0,
                "weighted_score_chick_fil_a_locations_count_gid": 0,
                "final_score": 25.0
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "index": 1,
                "walmart_locations_count_gid": 1,
                "chick_fil_a_locations_count_gid": 0,
                "weighted_score_walmart_locations_count_gid": 0,
                "weighted_score_chick_fil_a_locations_count_gid": 0,
                "final_score": 0
            }
        },
        {
            "type": "Feature",
            "geometry": null,
            "properties": {
                "index": 3,
                "walmart_locations_count_gid": 1,
                "chick_fil_a_locations_count_gid": 0,
                "weighted_score_walmart_locations_count_gid": 0,
                "weighted_score_chick_fil_a_locations_count_gid": 0,
                "final_score": 0
            }
        }
    ]
}
```