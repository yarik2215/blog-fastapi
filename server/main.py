import inspect
import re
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

from fastapi_jwt_auth.exceptions import AuthJWTException

from .routers import users, posts, analytics
from .settings import engine


app = FastAPI(title='BlogAPI')


app.include_router(
    router=posts.router,
    prefix='/api/posts',
    tags=['Posts'],
)

app.include_router(
    router=users.router,
    prefix='/api/users',
    tags=['Users'],
)

app.include_router(
    router=analytics.router,
    prefix='/api/analytic',
    tags=['Analytic'],
)


@app.get('/ping')
def ping_pong():
    return 'pong'


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title = "My Auth API",
        version = "1.0",
        description = "Simple blog api, based on FastAPI framework.",
        routes = app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi