import random
from typing import List, Tuple
from abc import ABC, abstractmethod
from pydantic.main import BaseModel
from server.models.user import UserCreate, UserLogin
from server.models.post import Like, PostCreate, Post
from server.utils.security import JwtTokenPair


class DataCreatorInterface(ABC):
    
    @abstractmethod
    def get_object(self, *args, **kwargs) -> BaseModel:
        NotImplemented


# __________________ Users _____________________

class UserData(UserCreate, JwtTokenPair):
    pass


class UserCreatorBase:
    def create_user(self, user_data: UserCreate) -> UserData:
        NotImplemented


class UserGenerator:
    def __init__(self, creator: UserCreatorBase, data_creator: DataCreatorInterface) -> None:
        self._creator = creator
        self._data_creator = data_creator
        self._users: List[UserData] = []

    @property
    def users(self) -> Tuple[UserData]:
        return tuple(self._users)
    
    def generate(self, quantity: int) -> Tuple[UserData]:
        for _ in range(0, quantity):
            user_data = self._data_creator.get_object()
            user = self._creator.create_user(user_data)
            if user:
                self._users.append(user)
        return self.users


# __________________ Posts _____________________


class PostCreatorBase:
    def create_post(self, user: UserData, post_data: PostCreate) -> Post:
        NotImplemented


class PostGenerator:
    def __init__(self, creator: PostCreatorBase, data_creator: DataCreatorInterface) -> None:
        self._creator = creator
        self._data_creator = data_creator
        self._posts : List[Post] = []

    @property
    def posts(self) -> Tuple[Post]:
        return tuple(self._posts)

    def generate(self, quantity: int, user: UserData) -> Tuple[Post]:
        for i in range(0, quantity):
            post_data = self._data_creator.get_object(
                f' #{i} by {user.username}'
            )
            post = self._creator.create_post(user, post_data)
            if post:
                self._posts.append(post)
        return self.posts



# ___________ Likes ________________

class LikeData(BaseModel):
    post_id: str
    username: str
    status_code: int


class LikeCreatorBase:
    def create_like(self, user: UserData, post: Post) -> LikeData:
        NotImplemented


class UserLikesGenerator:
    def __init__(self, creator: LikeCreatorBase) -> None:
        self._creator = creator
        self._likes: List[Like] = []

    @property
    def likes(self) -> Tuple[Like]:
        return tuple(self._likes)

    def generate(self, quantity: int, user: UserData, posts: List[Post]) -> Tuple[Like]:
        for _ in range(0,quantity):
            like = self._creator.create_like(user, random.choice(posts))
            self._likes.append(like)
        return self.likes