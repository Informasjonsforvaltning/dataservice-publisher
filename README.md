# dataservice-publisher

This service publishes a [dataservice](https://www.w3.org/TR/vocab-dcat-2/#Class:Data_Service) catalog published by Digdir.

The representation of the catalog accords to the [dcat-ap-no v.2 standard](https://github.com/difi/dcat-ap-no/tree/review).

The API is specified according to [the OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) in [dataservice-catalog.yaml](./dataservice-catalog.yaml)

The API is also published as a dataservice in this catalog.

## Install requirements
You should work in a virtual environment. To do that, install [venv](https://docs.python.org/3/library/venv.html)
```
sudo apt-get install python3-venv
```
Create and activate your virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
Install software:
```
python3 -m pip install --upgrade pip
pip3 install --no-cache-dir -r requirements.txt
```
## Environment variables
To run the service you need to supply a set of environment variables. A simple way to solve this is to supply a .env file in the root directory:
```
HOST_URL = "http://localhost"
HOST_PORT = "8080"
PUBLISHER_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"
```
## Running the API locally
 Start the endpoint:
```
% FLASK_APP=dataservicecatalog FLASK_ENV=development flask run --port=8080
% FLASK_APP=dataservicecatalog FLASK_ENV=development flask init-db
```
## Running the API in a wsgi-server (gunicorn)
```
% gunicorn "dataservicecatalog:create_app()"  --config=dataservicecatalog/gunicorn_config.py
```
## Running the wsgi-server in Docker

To build and run the api in a Docker container:
```
% docker build -t digdir/dataservice-publisher:latest .
% docker run -p 8080:8080 -d digdir/dataservice-publisher:latest
```

## Running tests
We use [pytest](https://docs.pytest.org/en/latest/) for contract testing.

To run the tests:
```
pytest -rA
```

## Test the endpoint

Regardless if you run the app via Docker or not, in another terminal:
```
% curl -H "Accept: text/turtle" "http://localhost:8080/"
```
