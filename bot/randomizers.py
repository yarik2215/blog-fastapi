from .services import UserCreate, PostCreate, DataCreatorInterface
from datetime import datetime


class TimeUserRandomizer(DataCreatorInterface):
    def __init__(self) -> None:
        super().__init__()
        self._last_user_number = 0
    
    def get_data(self, *args, **kwargs) -> UserCreate:
        time_mixin = f'{datetime.now().timestamp()}{self._last_user_number}'
        user = UserCreate(
            email = f'user{time_mixin}@bot.com',
            username = f'user{time_mixin}',
            password = 'test',
        )
        self._last_user_number += 1
        return user


class SimplePostRandomizer(DataCreatorInterface):
    
    def get_data(self, post_title_mixin: str, *args, **kwargs) -> PostCreate:
        post = PostCreate(
            title = f'Post{post_title_mixin}',
            text = 'Some text here.'
        )
        return post