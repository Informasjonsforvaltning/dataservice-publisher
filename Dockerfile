FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install "poetry==1.0.5"
COPY poetry.lock pyproject.toml /usr/src/app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ADD src /usr/src/app/src

EXPOSE 8080

RUN cd src && python3 dataservice_publisher/model/loadDB.py

CMD gunicorn  --chdir src "dataservice_publisher:create_app()"  --config=src/dataservice_publisher/gunicorn_config.py
