from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from server.utils.security import create_tokens
from server.models.user import User, UserCreate, UserInfo, UserLogin
from server.settings import engine
from .dependencies import get_authorized_user, Selector, get_selector


router = APIRouter()


@router.post('/register', response_model=UserInfo)
async def register_user(user: UserCreate, Authorize: AuthJWT = Depends()):
    existing_users = await engine.find(
        User, (User.email == user.email) | (User.username == user.username)
    )
    if existing_users:
        raise HTTPException(400, detail="User with this email or username already exists")
    user = User(**user.dict())
    user.set_password(user.password)
    user = await engine.save(user)
    return user


@router.post('/login')
async def login_user(data: UserLogin, Authorize: AuthJWT = Depends()):
    user = await engine.find_one(User, (User.email == data.email) & (User.deleted == False))
    if not user:
        raise HTTPException(404)
    if not user.verify_pswd(data.password):
        raise HTTPException(400, detail='Wrong login data')
    user.update_login_time()
    await engine.save(user)
    return create_tokens(Authorize, str(user.id), is_admin=user.super_user)


@router.get('/refresh', dependencies=[Depends(HTTPBearer())])
async def refresh_tokens(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    raw_jwt = Authorize.get_raw_jwt()
    return create_tokens(Authorize, raw_jwt['sub'], is_admin=raw_jwt['is_admin'])


@router.get('/', dependencies=[Depends(get_authorized_user)])
async def list_users(
    selector: Selector = Depends(get_selector(User, User.username, User.email))
):
    users = await selector.get_objects()
    return {'count': selector.count, 'users': users}


@router.get('/{username}', response_model=UserInfo, dependencies=[Depends(get_authorized_user)])
async def read_user(username: str):
    user = await engine.find_one(User, User.username == username)
    if user is None:
        raise HTTPException(404)
    return user


@router.delete('/{username}')
async def delete_user(username: str, req_user: User = Depends(get_authorized_user)):
    user = await engine.find_one(User, User.username == username)
    if user is None:
        raise HTTPException(404)
    if req_user.id != user.id:
        raise HTTPException(403)
    user.deleted = True
    await engine.save(user)
