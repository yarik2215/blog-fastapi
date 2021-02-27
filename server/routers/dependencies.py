from server.models.user import User
from fastapi import Depends, HTTPException
from odmantic import ObjectId
from bson.objectid import ObjectId as BsonId
from fastapi_jwt_auth import AuthJWT
from server.models.user import User
from server.settings import engine

async def get_authorized_user(Authorize: AuthJWT = Depends()) -> User:
    Authorize.jwt_required()
    user_id = BsonId(Authorize.get_jwt_subject())
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(400, detail="No user found")
    user.update_request_time()
    await engine.save(user)
    return user

async def get_admin_user(user_id: ObjectId = Depends(get_authorized_user)) -> User:
    user = await engine.find_one(User, User.id == user_id)
    if not user.super_user:
        raise HTTPException(403)
    return user