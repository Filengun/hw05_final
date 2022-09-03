from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.temp_url = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:second', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': StaticURLTests.post.id}):
                'posts/post_detail.html',
        }

    def test_status_auth(self):
        """Страница доступные гостю."""
        for i in StaticURLTests.temp_url:
            with self.subTest(i=i):
                response = self.guest_client.get(i)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f"Не ок со статусом у гостя {i}"
                )

    def test_status_guest_client(self):
        """Страницы доступные авторизованному пользователю."""
        for i in StaticURLTests.temp_url:
            with self.subTest():
                response = self.guest_client.get(i)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK, "Ок со статусом у авториз"
                )

    def test_na_status_auth(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK, "два")

    def test_edit(self):
        """Страница /posts/1/edit/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK, "три")

    def test_no_post(self):
        """Страница /posts/6/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/posts/6/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, "четыре")
