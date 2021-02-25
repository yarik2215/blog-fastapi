from typing import Optional
import datetime as dt
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..settings import engine
from ..models.post import Post
from ..models.user import User
from .dependencies import get_admin_user


router = APIRouter(
    # dependencies=[Depends(get_admin_user)]
)

class DateFilter():
    date_from: Optional[dt.datetime]
    date_to: Optional[dt.datetime]

    def __init__(self, date_from:Optional[dt.date] = None, date_to: Optional[dt.date] = None) -> None:
        self.date_from = dt.datetime.combine(date_from, dt.time(0)) if date_from else None
        self.date_to = dt.datetime.combine(date_to, dt.time(0)) if date_to else None

    def get_filter_dict(self):
        res = dict()
        if self.date_from:
            res["$gte"] = self.date_from
        if self.date_to:
            res["$lte"] = self.date_to        
        return res


@router.get('/likes')
async def get_likes(date_filter: DateFilter = Depends()):
    collection = engine.get_collection(Post)
    pipeline = [
        { "$unwind": "$likes"},
        {"$group":{"_id": "$likes.date", "count":{"$sum":1}}},
    ]
    date_match = date_filter.get_filter_dict()
    if date_match:
        pipeline.append({"$match": {"_id":  date_match}})
    res = await collection.aggregate(pipeline).to_list(length=None)
    return res
    

@router.get('/user-activity/{username}')
async def get_user_activity(username: str):
    user = await engine.find_one(User, User.username == username)
    return {
        "last_login": user.last_login,
        "last_request": user.last_request
    }