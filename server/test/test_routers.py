import asyncio
import os
from typing import List
from unittest import TestCase
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

# hack to use 
os.environ['DATABASE'] = 'test'

from server.settings import engine
from server.main import app
from server.models.user import User, UserInfo
from server.models.post import Post, Like
from server.utils.security import create_tokens, JwtTokenPair


loop = asyncio.get_event_loop()

async def create_user(email : str = 'test@mail.com', username : str = 'test', password : str = 'test') -> User:
    user = User(email=email, username=username, password=password)
    user.set_password(password)
    user = await engine.save(user)
    return user


async def create_post(owner: User, title: str = 'post', text: str = 'some text', likes: List[Like] = []):
    post = Post(owner=owner.id, title=title, text=text, likes=likes)
    post = await engine.save(post)
    return post


def login_user(client: TestClient, user: User) -> JwtTokenPair:
    tokens = create_tokens(AuthJWT(), str(user.id), is_admin=user.super_user)
    client.headers['Authorization'] = f'Bearer {tokens.access_token}'
    return tokens


class UserRouterTest(TestCase):

    def setUp(self) -> None:
        self.user = loop.run_until_complete(create_user())
        self.dummy_user1 = loop.run_until_complete(create_user('dummy1@test.com', 'dummy1'))
        self.client = TestClient(app)

    def tearDown(self) -> None:
        engine.client.drop_database('test')

    def test_ping_200_ok(self) -> None:
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'pong')

    def test_register_200_ok(self) -> None:
        user_data = {
            'email': 'test2@mail.com',
            'username': 'test2',
            'password': 'test'
        }
        response = self.client.post(
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
        response = self.client.post(
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
        response = self.client.post(
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
        response = self.client.post(
            '/api/users/register',
            json = user_data,
        )
        self.assertEqual(response.status_code, 400)

    def test_login_200_ok(self) -> None:
        login_data = {
            'email': 'test@mail.com',
            'password': 'test',
        }
        response = self.client.post(
            '/api/users/login',
            json = login_data,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['access_token'])
        self.assertTrue(response_data['refresh_token'])

    def test_login_400_wrong_credentials(self) -> None:
        login_data = {
            'email': 'test@mail.com',
            'password': 'wrongpass',
        }
        response = self.client.post(
            '/api/users/login',
            json = login_data,
        )
        self.assertEqual(response.status_code, 400)
        
    def test_refresh_token_200_ok(self) -> None:
        tokens = login_user(self.client, self.user)
        self.client.headers['Authorization'] = f'Bearer {tokens.refresh_token}'
        response = self.client.get('/api/users/refresh')
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['access_token'])
        self.assertTrue(response_data['refresh_token'])
        
    def test_list_users_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.get(
            '/api/users/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        
    def test_get_user_by_username_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.get(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], str(self.user.id))
        
    def test_get_user_by_username_404_not_found(self):
        login_user(self.client, self.user)
        response = self.client.get(
            '/api/users/uknown',
        )
        self.assertEqual(response.status_code, 404)
        
    def test_delete_user_403_not_authorized(self):
        response = self.client.delete(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_user_403_no_permission(self):
        user = loop.run_until_complete(create_user('test2@mail.com', 'test2'))
        login_user(self.client, user)
        response = self.client.delete(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_user_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.delete(
            f'/api/users/{self.user.username}',
        )
        self.assertEqual(response.status_code, 200)
        user = loop.run_until_complete(
            engine.find_one(User, User.id == self.user.id)
        )
        self.assertEqual(user.deleted, True)


class PostRouterTest(TestCase):

    def setUp(self) -> None:
        self.user = loop.run_until_complete(create_user())
        self.post1 = loop.run_until_complete(create_post(self.user, 'post1'))
        self.post2 = loop.run_until_complete(
            create_post(self.user, 'post2', likes=[Like(user_id=self.user.id)])
        )
        self.client = TestClient(app)

    def tearDown(self) -> None:
        engine.client.drop_database('test')

    def test_list_posts_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.get(
            '/api/posts/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_list_posts_403_not_authorized(self):
        response = self.client.get(
            '/api/posts/'
        )
        self.assertEqual(response.status_code, 403)

    def test_get_post_by_id_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.get(
            f'/api/posts/{self.post1.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], str(self.post1.id))
            

    def test_get_post_by_id_403_not_authorized(self):
        response = self.client.get(
            f'/api/posts/{self.post1.id}'
        )
        self.assertEqual(response.status_code, 403)

    def test_create_post_200_ok(self):
        login_user(self.client, self.user)
        post_data = {
            'title': 'new post',
            'text': 'Some text',
        }
        response = self.client.post(
            '/api/posts/',
            json = post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['owner'], str(self.user.id))

    def test_create_post_403_not_authorized(self):
        post_data = {
            'title': 'new post',
            'text': 'Some text',
        }
        response = self.client.post(
            '/api/posts/',
            json = post_data,
        )
        self.assertEqual(response.status_code, 403)
        
    def test_update_post_200_ok(self):
        login_user(self.client, self.user)
        update_data = {
            'title': 'new title',
            'text': 'new text',
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}',
            json = update_data,
        )
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['title'], update_data['title'])
        self.assertEqual(resp_data['text'], update_data['text'])
        self.assertEqual(resp_data['id'], str(self.post1.id))

    def test_partial_update_post_200_ok(self):
        login_user(self.client, self.user)
        update_data = {
            'title': 'new title',
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}',
            json = update_data,
        )
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['title'], update_data['title'])
        self.assertEqual(resp_data['id'], str(self.post1.id))

    def test_update_post_403_not_authorized(self):
        update_data = {
            'title': 'new title',
            'text': 'new text',
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}',
            json = update_data,
        )
        self.assertEqual(response.status_code, 403)

    def test_update_post_403_no_permission(self):
        user = loop.run_until_complete(create_user('noname@mail.com', 'noname'))
        login_user(self.client, user)
        update_data = {
            'title': 'new title',
            'text': 'new text',
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}',
            json = update_data,
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_post_204_no_data(self):
        login_user(self.client, self.user)
        response = self.client.delete(
            f'/api/posts/{self.post1.id}',
        )
        post = loop.run_until_complete(
            engine.find_one(Post, Post.id == self.post1.id)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(post, None)
        
    def test_delete_post_403_no_permission(self):
        user = loop.run_until_complete(create_user('noname@mail.com', 'noname'))
        login_user(self.client, user)
        response = self.client.delete(
            f'/api/posts/{self.post1.id}',
        )
        self.assertEqual(response.status_code, 403)

    def test_like_post_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.post(
            f'/api/posts/{self.post1.id}/like'
        )
        post = loop.run_until_complete(
            engine.find_one(Post, Post.id == self.post1.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(post.likes), 1)

    def test_like_post_twice_400_bad_request(self):
        login_user(self.client, self.user)
        response = self.client.post(
            f'/api/posts/{self.post2.id}/like'
        )
        post = loop.run_until_complete(
            engine.find_one(Post, Post.id == self.post2.id)
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(post.likes), 1)

    def test_post_unlike_200_ok(self):
        login_user(self.client, self.user)
        response = self.client.post(
            f'/api/posts/{self.post2.id}/unlike'
        )
        post = loop.run_until_complete(
            engine.find_one(Post, Post.id == self.post2.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(post.likes), 0)

    def test_post_unlike_not_liked_post_400_bad_request(self):
        login_user(self.client, self.user)
        response = self.client.post(
            f'/api/posts/{self.post1.id}/unlike'
        )
        post = loop.run_until_complete(
            engine.find_one(Post, Post.id == self.post1.id)
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(post.likes), 0)
