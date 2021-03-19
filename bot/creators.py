from typing import Union
import requests
from requests.sessions import default_headers
from .services import (
    UserData,
    UserCreate,
    UserLogin,
    JwtTokenPair,
    UserCreatorBase,
    Post,
    PostCreate,
    PostCreatorBase,
    LikeData,
    LikeCreatorBase
)


class ApiUserCreator(UserCreatorBase):
    def __init__(self, register_url: str, login_url: str) -> None:
        self._register_url = register_url
        self._login_url = login_url

    def create_user(self, user_data: UserCreate) -> Union[UserData, None]:
        try:
            self._register(user_data)
            tokens = self._login(user_data)
            return UserData(
                **user_data.dict(),
                **tokens.dict(),
            )
        except AssertionError:
            return None

    def _register(self, user_data: UserCreate) -> None:
        response = requests.post(
            self._register_url,
            json=user_data.dict()
        )
        assert response.status_code == 200

    def _login(self, user_data: UserLogin) -> JwtTokenPair:
        response = requests.post(
            self._login_url,
            json=user_data.dict()
        )
        assert response.status_code == 200
        return JwtTokenPair(**response.json())


class ApiPostCreator(PostCreatorBase):
    def __init__(self, post_create_url: str) -> None:
        self._post_create_url = post_create_url

    def create_post(self, user: UserData, post_data: PostCreate) -> Post:
        response = requests.post(
            self._post_create_url,
            json=post_data.dict(),
            headers={'Authorization': f'Bearer {user.access_token}'}
        )
        if response.status_code > 299:
            return None
        return Post(**response.json())
        

class ApiLikeCreator(LikeCreatorBase):
    def __init__(self, post_like_url: str) -> None:
        '''
        post_like_url should be string with format like "api/posts/{post_id}/like"
        '''
        self._post_like_url = post_like_url
    
    def create_like(self, user: UserData, post: Post) -> LikeData:
        response = requests.post(
            self._post_like_url.format(post_id=str(post.id)),
            headers={'Authorization': f'Bearer {user.access_token}'}
        )
        return LikeData(
            post_id = str(post.id),
            username = user.username,
            status_code = response.status_code
        ) 
