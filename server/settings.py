from datetime import timedelta
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
import os

# JWT auth settings
SECRET_KEY = os.environ.get('SECRET_KEY', '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7')

# Password validation setting
MIN_PASSWORD_LENGTH = 3

DATABASE = os.environ.get('DATABASE', 'blog')
DB_CLIENT = os.environ.get('DB_CLIENT' ,"mongodb://root:root@db:27017/")
# DB settings
client = AsyncIOMotorClient(DB_CLIENT)
engine = AIOEngine(client, database=DATABASE)


# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_access_token_expires: timedelta = timedelta(days = 1)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)

# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()
