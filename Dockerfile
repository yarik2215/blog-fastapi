FROM python:3.8

WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
# RUN pip install pipenv
# COPY ./Pipfile.lock .
# RUN pipenv install --ignore-pipfile
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
WORKDIR /server
COPY . .

