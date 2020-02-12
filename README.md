# dataservice-publisher

This service publishes a [dataservice](https://www.w3.org/TR/vocab-dcat-2/#Class:Data_Service) catalog published by Digdir.

The representation of the catalog accords to the [dcat-ap-no v.2 standard](https://github.com/difi/dcat-ap-no/tree/review).

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
pip3 install --no-cache-dir -r requirements.txt
```
## Running the API locally
 Start the endpoint by simply:
```
% cd src
% python3 app.py
```
## Running the API in a wsgi-server (gunicorn)
```
% cd src
% gunicorn wsgi:app --config=config.py
```
## Running the wsgi-server in Docker

To build and run the api in a Docker container:
```
% docker build -t digdir/dataservice-publisher:latest .
% docker run -p 8080:8080 -d digdir/dataservice-publisher:latest
```

## Running tests
We use [pytest](https://docs.pytest.org/en/latest/) and [schemathesis](https://github.com/kiwicom/schemathesis) for testing the API against the [openAPI specification](./dataservice-catalog.yaml).

To run the tests:
```
pytest test_api.py
```

## Test the endpoint

Regardless if you run the app via Docker or not, in another terminal:
```
% curl -H "Accept: text/turtle" "http://localhost:8080/"
```
