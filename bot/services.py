import random
from typing import List, Tuple
from abc import ABC, abstractmethod
from pydantic.main import BaseModel
from server.models.user import UserCreate, UserLogin
from server.models.post import Like, PostCreate, Post
from server.utils.security import JwtTokenPair


class GenerationError(Exception):
    ...


class DataCreatorInterface(ABC):
    
    @abstractmethod
    def get_data(self, *args, **kwargs) -> BaseModel:
        ...


class InstanceCreatorInterafce(ABC):

    @abstractmethod
    def create_instance(self, data: BaseModel, **kwargs) -> BaseModel:
        ...


# __________________ Users _____________________

class UserData(UserCreate, JwtTokenPair):
    pass


class UserGenerator:
    def __init__(self, instance_creator: InstanceCreatorInterafce, data_creator: DataCreatorInterface) -> None:
        self._instance_creator = instance_creator
        self._data_creator = data_creator
        self._users: List[UserData] = []

    @property
    def users(self) -> Tuple[UserData]:
        return tuple(self._users)
    
    def generate(self, quantity: int) -> Tuple[UserData]:
        for _ in range(0, quantity):
            user_data = self._data_creator.get_data()
            user = self._instance_creator.create_instance(user_data)
            if user:
                self._users.append(user)
        return self.users


# __________________ Posts _____________________


class PostGenerator:
    def __init__(self, instance_creator: InstanceCreatorInterafce, data_creator: DataCreatorInterface) -> None:
        self._instance_creator = instance_creator
        self._data_creator = data_creator
        self._posts : List[Post] = []

    @property
    def posts(self) -> Tuple[Post]:
        return tuple(self._posts)

    def generate(self, quantity: int, user: UserData) -> Tuple[Post]:
        for i in range(0, quantity):
            post_data = self._data_creator.get_data(
                f' #{i} by {user.username}'
            )
            post = self._instance_creator.create_instance(user, post_data)
            if post:
                self._posts.append(post)
        return self.posts



# ___________ Likes ________________

class LikeData(BaseModel):
    post_id: str
    username: str
    status: str


class UserLikesGenerator:
    def __init__(self, instance_creator: InstanceCreatorInterafce) -> None:
        self._instance_creator = instance_creator
        self._likes: List[Like] = []

    @property
    def likes(self) -> Tuple[Like]:
        return tuple(self._likes)

    def generate(self, quantity: int, user: UserData, posts: List[Post]) -> Tuple[Like]:
        for _ in range(0,quantity):
            like = self._instance_creator.create_instance(user, random.choice(posts))
            self._likes.append(like)
        return self.likes