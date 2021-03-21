from typing import Dict, Optional, Union
from abc import ABC, abstractmethod
from pydantic.main import BaseModel
import requests
from .services import (
    UserData,
    UserCreate,
    UserLogin,
    JwtTokenPair,
    Post,
    PostCreate,
    LikeData,
    InstanceCreatorInterafce,
    GenerationError
)

class ApiError(GenerationError):
    
    def __init__(self, status_code: int ,*args: object) -> None:
        super().__init__(f'Status code: {status_code}' ,*args)
        self.status_code = status_code


class InstanceCreatorApi(InstanceCreatorInterafce):

    def create_instance(self, data: BaseModel, **kwargs) -> BaseModel:
        NotImplemented

    def _request(self, method: str, url: str, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        if headers is None:
            headers = {}
        response = requests.request(
            method,
            url,
            headers=headers,
            json=json,
        )
        if not (200 <= response.status_code <= 299):
            raise ApiError(status_code=response.status_code)
        return response.json()


class ApiUserCreator(InstanceCreatorApi):
    def __init__(self, register_url: str, login_url: str) -> None:
        self._register_url = register_url
        self._login_url = login_url

    def create_instance(self, user_data: UserCreate) -> UserData:
        self._register(user_data)
        tokens = self._login(user_data)
        return UserData(
            **user_data.dict(),
            **tokens.dict(),
        )

    def _register(self, user_data: UserCreate) -> None:
        self._request(
            'POST',
            self._register_url,
            json=user_data.dict()
        )
        
    def _login(self, user_data: UserLogin) -> JwtTokenPair:
        data = self._request(
            'POST',
            self._login_url,
            json=user_data.dict()
        )
        return JwtTokenPair(**data)


class ApiPostCreator(InstanceCreatorApi):
    def __init__(self, post_create_url: str) -> None:
        self._post_create_url = post_create_url

    def create_instance(self, user: UserData, post_data: PostCreate) -> Post:
        data = self._request(
            'POST',
            self._post_create_url,
            json=post_data.dict(),
            headers={'Authorization': f'Bearer {user.access_token}'}
        )
        return Post(**data)
        

class ApiLikeCreator(InstanceCreatorApi):
    def __init__(self, post_like_url: str) -> None:
        '''
        post_like_url should be string with format like "api/posts/{post_id}/like"
        '''
        self._post_like_url = post_like_url
    
    def create_instance(self, user: UserData, post: Post) -> LikeData:
        status = "Liked"
        try:
            self._request(
                'POST',
                self._post_like_url.format(post_id=str(post.id)),
                headers={'Authorization': f'Bearer {user.access_token}'}
            )
        except ApiError as error:
            status = "Can't like"
        return LikeData(
            post_id = str(post.id),
            username = user.username,
            status = status
        ) 
