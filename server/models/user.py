from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from odmantic import Model
from odmantic.bson import ObjectId

from server.utils.security import hash_password, verify_password
from server.settings import MIN_PASSWORD_LENGTH


class User(Model):
    email: EmailStr
    username: str    
    password: str
    last_login: Optional[datetime] = None
    last_request: Optional[datetime] = None
    registration_date: datetime = datetime.now()
    super_user: bool = False
    deleted: bool = False

    def update_login_time(self):
        self.last_login = datetime.now()
    
    def update_request_time(self):
        self.last_request = datetime.now()

    def set_password(self, raw_password: str):
        self.password = hash_password(raw_password)

    def verify_pswd(self, raw_password: str) -> bool:
        return verify_password(raw_password, self.password)


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, value):
        if type(value) != str:
            raise TypeError("Not a valid type, expected str")
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError("Too short")
        return value


class UserInfo(UserBase, Model):
    last_login: Optional[datetime] = None
    last_request: Optional[datetime] = None
    registration_data: datetime = datetime.now()
    deleted: bool = False


