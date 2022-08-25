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
| `POST`  | `/api/v1/services/enrich_map/`                                                  | [Enrich Map](#enrich-map)               |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`            |


## Enrich Map

Description

Example Input
```json
```

Example Response
```json
```

