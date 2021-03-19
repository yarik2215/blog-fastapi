from random import randint
from bot.config import Config, JsonConfigReader
from bot.services import UserGenerator, PostGenerator, UserLikesGenerator
from bot.creators import ApiUserCreator, ApiPostCreator, ApiLikeCreator
from bot.randomizers import TimeUserRandomizer, SimplePostRandomizer

if __name__ == "__main__":
    config = Config(JsonConfigReader('./bot-config.json')).get_config()
    print('Starting automated bot')
    print('Config:', *str(config).split(), sep='\n  ')
    
    # generating users
    print('Creating users')
    user_generator = UserGenerator(
        ApiUserCreator(
            config.api_url + '/users/register',
            config.api_url + '/users/login',
        ),
        TimeUserRandomizer()
    )
    users = user_generator.generate(
        config.number_of_users
    )
    print('Users:', *[u.username for u in users], sep='\n  ')

    #generating posts
    print('Creating posts')
    post_generator = PostGenerator(
        ApiPostCreator(
            config.api_url + '/posts',
        ),
        SimplePostRandomizer()
    )
    for user in users:
        post_generator.generate(
            randint(1, config.max_posts_per_user),
            user
        )
    print('Posts:', *[p.title for p in post_generator.posts], sep='\n  ')

    #like posts
    print('Creating likes')
    like_generator = UserLikesGenerator(
        ApiLikeCreator(
            config.api_url + '/posts/{post_id}/like'
        )
    )
    for user in user_generator.users:
        like_generator.generate(
            randint(1, config.max_likes_per_user),
            user,
            post_generator.posts
        )
    print('Likes:', *like_generator.likes, sep='\n  ')