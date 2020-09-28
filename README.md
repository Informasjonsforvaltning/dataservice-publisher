# dataservice-publisher

This service publishes a [dataservice](https://www.w3.org/TR/vocab-dcat-2/#Class:Data_Service) catalog published by the[Norwegian Digitalisation Agency](https://digdir.no).

The representation of the catalog accords to the [dcat-ap-no v.2 standard](https://github.com/Informasjonsforvaltning/dcat-ap-no/tree/review).

The API is specified according to [the OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) in [dataservice-catalog.yaml](./dataservice-catalog.yaml)

The API is also published as a dataservice in this catalog.

## Develop and run locally
### Requirements
- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- [poetry](https://python-poetry.org/)
- [nox](https://nox.thea.codes/en/stable/)

### Install software:
```
% git clone https://github.com/Informasjonsforvaltning/dataservice-publisher.git
% cd dataservice-publisher
% pyenv install 3.7.7
% pyenv local 3.7.7
% poetry install
```
### Environment variables
To run the service locally, you need to supply a set of environment variables. A simple way to solve this is to supply a .env file in the root directory, e.g:
```
HOST=localhost
HOST_PORT=8080
ADMIN_USERNAME=admin
ADMIN_PASSWORD=passw123
FUSEKI_HOST=localhost
FUSEKI_PORT=3030
FUSEKI_PASSWORD=passw123
SECRET_KEY=super_secret
TDB=2
FUSEKI_DATASET_1=ds
```
### Running the API locally
 Start the endpoint:
```
% poetry shell
% FLASK_APP=dataservice_publisher FLASK_ENV=development flask run --port=8080
```
## Running the API in a wsgi-server (gunicorn)
```
% poetry shell
% gunicorn  --chdir src "dataservice_publisher:create_app()"  --config=src/dataservice_publisher/gunicorn_config.py
```
## Running the wsgi-server in Docker
To build and run the api in a Docker container:
```
% docker build -t digdir/dataservice-publisher:latest .
% docker run --env-file .env -p 8080:8080 -d digdir/dataservice-publisher:latest
```
## Load data
 - [ ] TODO: document how to load data by using scripts in etl folder of ./scripts
## Running tests
We use [pytest](https://docs.pytest.org/en/latest/) for contract testing.

To run linters, checkers and tests:
```
% nox
```
## Test the endpoint
Regardless if you run the app via Docker or not, in another terminal:
```
% curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"username":"xyz","password":"xyz"}' \
  http://localhost:8080/login
% export ACCESS="" #token from response
% curl --header "Content-Type: application/json" \
  --header "Authorization: Bearer $ACCESS"
  --request POST \
  --data @tests/files/catalog_1.json \
  http://localhost:8080/catalogs
```
