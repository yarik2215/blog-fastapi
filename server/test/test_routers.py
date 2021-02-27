from unittest import TestCase
import asyncio
import os
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

# hack to use 
os.environ['DATABASE'] = 'test'

from server.settings import engine
from server.main import app
from server.models.user import User, UserInfo

client = TestClient(app)

loop = asyncio.get_event_loop()

async def create_user(email : str = 'test@mail.com', username : str = 'test', password : str = 'test') -> User:
    user = User(email=email, username=username, password=password)
    user.set_password(password)
    user = await engine.save(user)
    return user


def login_user(user: User) -> str:
    token = AuthJWT().create_access_token(subject=str(user.id))
    return token


class UserRouterTest(TestCase):

    def setUp(self) -> None:
        self.user = loop.run_until_complete(create_user())

    def tearDown(self) -> None:
        engine.client.drop_database('test')

    def test_ping_200_ok(self) -> None:
        response = client.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'pong')

    def test_register_200_ok(self) -> None:
        user_data = {
            'email': 'test2@mail.com',
            'username': 'test2',
            'password': 'test'
        }
        response = client.post(
            '/api/users/register',
            json = user_data,
        )
        self.assertEqual(response.status_code, 200)

    def test_register_422_short_password(self) -> None:
        user_data = {
            'email': 'test2@mail.com',
            'username': 'test2',
            'password': 't'
        }
        response = client.post(
            '/api/users/register',
            json = user_data,
        )
        self.assertEqual(response.status_code, 422)


    def test_register_400_email_already_exists(self) -> None:
        user_data = {
            'email': 'test@mail.com',
            'username': 'test2',
            'password': 'test'
        }
        response = client.post(
            '/api/users/register',
            json = user_data,
        )
        self.assertEqual(response.status_code, 400)

    def test_register_400_username_already_exists(self) -> None:
        user_data = {
            'email': 'test2@mail.com',
            'username': 'test',
            'password': 'test'
        }
        response = client.post(
            '/api/users/register',
            json = user_data,
        )
        self.assertEqual(response.status_code, 400)

    def test_login_200_ok(self) -> None:
        login_data = {
            'email': 'test@mail.com',
            'password': 'test',
        }
        response = client.post(
            '/api/users/login',
            json = login_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('access_token'))

    def test_login_400_wrong_credentials(self) -> None:
        login_data = {
            'email': 'test@mail.com',
            'password': 'wrongpass',
        }
        response = client.post(
            '/api/users/login',
            json = login_data,
        )
        self.assertEqual(response.status_code, 400)
        
    def test_list_users_200_ok(self):
        response = client.get(
            '/api/users/',
        )
        self.assertEqual(response.status_code, 200)
        
    def test_get_user_by_username_200_ok(self):
        response = client.get(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserInfo(**response.json()), UserInfo(**self.user.dict()))
        
    def test_get_user_by_username_404_not_found(self):
        response = client.get(
            '/api/users/uknown',
        )
        self.assertEqual(response.status_code, 404)
        
    def test_delete_user_401_not_authorized(self):
        response = client.delete(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_user_403_no_permission(self):
        user = loop.run_until_complete(create_user('test2@mail.com', 'test2'))
        token = login_user(user)
        response = client.delete(
            f'/api/users/{self.user.username}',
            headers = {'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_user_200_ok(self):
        token = login_user(self.user)
        response = client.delete(
            f'/api/users/{self.user.username}',
            headers = {'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        user = loop.run_until_complete(
            engine.find_one(User, User.id == self.user.id)
        )
        self.assertEqual(user.deleted, True)


