ARG PYTHON_VERSION=3.7.5-slim-buster

FROM python:${PYTHON_VERSION} AS build-stage
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip

RUN mkdir -p /app/ \
    && mkdir -p /app/output/ \
    && mkdir -p /app/logs/

copy src/ /app/src
RUN pip3 install -r ./app/src/requirements.txt

WORKDIR /app/src/

ENTRYPOINT [ "python3", "main.py" , "-fm", "csv", "-api", "iex"]