import asyncio

from server.settings import engine, MIN_PASSWORD_LENGTH
from server.models.user import User

loop = asyncio.get_event_loop()

async def create_user():
    email = input('email: ')
    if await engine.find(User, User.email == email):
        raise ValueError('Email already exists')
    username = input('username: ')
    if await engine.find(User, User.username == username):
        raise ValueError('This username already exists')
    password = input('password: ')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError('Password too short')
    user = User(
        username=username,
        email=email,
        super_user = True,
        password=password,
    )
    user.set_password(password)
    user = await engine.save(user)
    print('Done')
    print(user)


if __name__ == '__main__':
    try:
        loop.run_until_complete(create_user())
    except ValueError as e:
        print(f'Error: {e}')
    finally:
        pass