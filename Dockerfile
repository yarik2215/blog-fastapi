FROM python:3.8

WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install pipenv
# copy project
COPY . /app

WORKDIR /app
# install dependencies
RUN pipenv install --system --ignore-pipfile
