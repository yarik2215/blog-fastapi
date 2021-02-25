from typing import List, Optional, Set
import datetime as dt
from pydantic import BaseModel

from odmantic import Field, Model
from odmantic.bson import ObjectId


class Like(BaseModel):
    user_id: ObjectId
    date: dt.datetime = dt.datetime.combine(dt.date.today(), dt.time(0))


class Post(Model):
    owner: ObjectId
    title: str
    text: str
    created_at: dt.datetime = dt.datetime.now()
    likes: List[Like] = []


class PostBase(BaseModel):
    title: str
    text: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


