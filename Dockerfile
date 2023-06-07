FROM python:3.10

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install "poetry==1.5.1"
COPY poetry.lock pyproject.toml /usr/src/app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ADD dataservice_publisher /usr/src/app/dataservice_publisher

EXPOSE 8080

CMD gunicorn dataservice_publisher:create_app  --config=dataservice_publisher/gunicorn_config.py --worker-class aiohttp.GunicornWebWorker --timeout 300
