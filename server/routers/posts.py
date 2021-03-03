from typing import Optional, List
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from odmantic.bson import ObjectId
from fastapi_jwt_auth import AuthJWT
from pydantic.utils import Obj

from server.models.post import Like, PostCreate, PostUpdate, Post
from server.models.user import User
from server.settings import engine
from .dependencies import get_authorized_user, Selector, get_selector


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


@router.get('/', dependencies=[Depends(get_authorized_user)])
async def post_list(selector: Selector = Depends(get_selector(Post, Post.title))):
    posts = await selector.get_objects()
    return {'count': selector.count, 'posts': posts}


@router.post('/', response_model=Post)
async def post_create(post: PostCreate, user: ObjectId = Depends(get_authorized_user)):
    post = await engine.save(Post(**post.dict(), owner=user.id))
    return post


@router.get('/{post_id}', response_model=Post, dependencies=[Depends(get_authorized_user)])
async def post_detail(post : Post = Depends(get_post_by_id), Authorize: AuthJWT = Depends()):
    return post


@router.put('/{post_id}', response_model=Post)
async def post_update(*, post : Post = Depends(get_post_only_owner), data: PostUpdate):
    updated_data = {**post.dict(), **data.dict(exclude_unset=True)}
    post = Post(**updated_data)
    await engine.save(post)
    return post

@router.delete('/{post_id}', status_code=204)
async def post_delete(*, post : Post = Depends(get_post_only_owner)):
    await engine.delete(post)

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
