# Blog FastAPI

## Run
First create `.env` file

To run localy use: 
```
pipenv install
pipenv run dev
```

To run with docker run:
```
docker-compose build
docker-compose up
```

## Create superuser
For creating a superuser run `pipenv run create_superuser` and follow the steps, or if using docker - from container shell run `python -m server.scripts.create_superuser`


## Testing
For testing run `pipenv run test` localy or `python -m unittest discover ./server/test` in docker container shell
> It will  it will create database `test` for testing purpose
