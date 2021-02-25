from ..settings import engine, MIN_PASSWORD_LENGTH
from ..models.user import User


def create_user():
    email = input('email: ')
    if engine.find(User, User.email == email):
        raise ValueError('Email already exists')
    username = input('username: ')
    if engine.find(User, User.username == username):
        raise ValueError('This username already exists')
    password = input('password: ')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError('Password too short')
    user = User(
        username=username,
        email=email,
        super_user = True
    )
    user.set_password(password)
    engine.save(user)
    print('Done')


if __name__ == '__main__':
    try:
        create_user()
    except ValueError as e:
        print(f'Error: {e}')