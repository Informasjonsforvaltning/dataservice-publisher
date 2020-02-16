FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD gunicorn "dataservicecatalog:create_app()"  --config=dataservicecatalog/gunicorn_config.py
