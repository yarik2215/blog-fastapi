from .services import UserCreate, UserRandomizerBase, PostCreate, PostRandomizerBase
from datetime import datetime

class TimeUserRandomizer(UserRandomizerBase):
    def __init__(self) -> None:
        super().__init__()
        self._last_user_number = 0
    
    def get_random_user(self) -> UserCreate:
        time_mixin = f'{datetime.now().timestamp()}{self._last_user_number}'
        user = UserCreate(
            email = f'user{time_mixin}@bot.com',
            username = f'user{time_mixin}',
            password = 'test',
        )
        self._last_user_number += 1
        return user

class SimplePostRandomizer(PostRandomizerBase):
    
    def get_random_post(self, post_title_mixin: str) -> PostCreate:
        post = PostCreate(
            title = f'Post{post_title_mixin}',
            text = 'Some text here.'
        )
        return post