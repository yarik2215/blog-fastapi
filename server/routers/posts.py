from typing import Optional, List
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from odmantic.bson import ObjectId
from fastapi_jwt_auth import AuthJWT
from pydantic.utils import Obj

from ..models.post import Like, PostCreate, PostUpdate, Post
from ..models.user import User
from ..settings import engine
from .dependencies import get_authorized_user
from server.routers import dependencies

router = APIRouter()


async def get_post_by_id(post_id: ObjectId) -> Post:
    post = await engine.find_one(Post, Post.id == post_id)
    if post is None:
        raise HTTPException(404)
    return post


async def get_post_only_owner(
    post: Post = Depends(get_post_by_id),
    user: User = Depends(get_authorized_user)
) -> Post:
    if user.id != post.owner:
        raise HTTPException(403)
    return post


@router.get('/', response_model=List[Post], dependencies=[Depends(get_authorized_user)])
async def post_list():
    posts = await engine.find(Post)
    return posts


@router.post('/', response_model=Post)
async def post_create(post: PostCreate, user: ObjectId = Depends(get_authorized_user)):
    post = await engine.save(Post(**post.dict(), owner=user.id))
    return post


@router.get('/{post_id}', response_model=Post, dependencies=[Depends(get_authorized_user)])
async def post_detail(post : Post = Depends(get_post_by_id), Authorize: AuthJWT = Depends()):
    return post


@router.put('/{post_id}', response_model=Post)
async def post_update(*, post : Post = Depends(get_post_only_owner), data: PostUpdate):
    updated_data = {**post.dict(), **data.dict()}
    post = Post(**updated_data)
    await engine.save(post)
    return post


@router.post('/{post_id}/like', response_model=Post)
async def post_like(*, 
    post : Post = Depends(get_post_by_id), 
    user: ObjectId = Depends(get_authorized_user),
):
    for like in post.likes:
        if like.user_id == user.id:
            raise HTTPException(400, detail="Already liked")
    post.likes.append(Like(user_id = user.id))
    await engine.save(post)
    return post


@router.post('/{post_id}/unlike', response_model=Post)
async def post_unlike(*, 
    post : Post = Depends(get_post_by_id),
    user: ObjectId = Depends(get_authorized_user)
):
    for i, like in enumerate(post.likes):
        if like.user_id == user.id:
            post.likes.pop(i)
            await engine.save(post)
            return post
    raise HTTPException(400, "No like found")
