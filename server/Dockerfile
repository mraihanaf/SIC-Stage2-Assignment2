# Use an official Python image as base
FROM python:3.12.3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy --ignore-pipfile
CMD ["pipenv", "run", "prod"]
