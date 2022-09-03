from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group, Comment, Follow
import shutil
import tempfile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPages(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)


    def test_template_auth(self):
        """URL используют соответствующие шаблоны для авторзиванного."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_template_guest_client(self):
        """URL используют соответствующие шаблоны для гостя."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': 1}): 'posts/post_detail.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_group_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:second', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_post_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        first_object = response.context['post']
        self.check_post_context(first_object)

    def test_post_create(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for parameter_1, parameter_2 in form.items():
            with self.subTest(parameter_1=parameter_1):
                form_field = response.context['form'].fields[parameter_1]
                self.assertIsInstance(form_field, parameter_2)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for parameter_1, parameter_2 in form.items():
            with self.subTest(parameter_1=parameter_1):
                form_field = (response.context.get('form').fields.get(
                    parameter_1))
                self.assertIsInstance(form_field, parameter_2)

    def check_post_context(self, post):
        self.assertEqual(post.id, 1)
        self.assertEqual(str(post.author), 'auth')
        self.assertEqual(str(post.text), 'Тестовый пост')
        self.assertEqual(post.group, PostsPages.group)
        self.assertEqual(str(post.image), 'posts/small.gif')

    def test_post_is_not_in_group(self):
        """Созданный пост не относится к группе 1."""
        self.second_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        response = self.authorized_client.get(reverse(
            'posts:second', kwargs={'slug': 'test-slug-2'}))
        self.assertEqual(
            response.context['group'].slug, self.second_group.slug)
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_cash_index(self):
        """Тест кеша."""
        post_create = Post.objects.create(
            author=PostsPages.user,
            text='cash'
        )
        response = self.authorized_client.get(reverse('posts:index'))
        obj = response.context['page_obj'][0]
        Post.objects.get(id=2).delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(obj, post_create)


class PaginatorTest(TestCase):
    """Тестируем пагинатор."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for _ in range(14):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.user)

    def test_paginator_one_list(self):
        """На первой странице десять постов."""
        template_pages_name = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'page_obj',
        }
        for reverse_name, context in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context[context]), 10)

    def test_paginator_second_list(self):
        """На второй странице четыре поста."""
        template_pages_name = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'page_obj',
            reverse('posts:profile', kwargs={
                'username': 'auth'}): 'page_obj',
        }
        for reverse_name, context in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context[context]), 4)


class CommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='пост автора'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='текст коммента'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentsTest.user)

    def test_comment_with_correct_context(self):
        """Проверяем текст и автора при создании коммента."""
        self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}
        ))
        com = Comment.objects.get(id=1)
        text = com.text
        author = com.author
        self.assertEqual(str(text), 'текст коммента')
        self.assertEqual(author, CommentsTest.user)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowTest.follower)

    def test_auth_follow_another_users(self):
        """проверка подписки."""
        resp_fol = self.authorized_client.get(
            reverse('posts:profile_follow',
                kwargs={'username': 'author'}))
        expected = Follow.objects.filter(
            user=FollowTest.follower).exists()
        self.assertTrue(expected)
        self.assertRedirects(
            resp_fol,
            reverse(
                'posts:profile', kwargs={'username': FollowTest.author}
            )
        )

    def test_unfollowng(self):
        """Проверка отписки."""
        Follow.objects.create(
            user=FollowTest.follower,
            author=FollowTest.author
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': 'author'}
            )
        )
        expected = Follow.objects.filter(
            user=FollowTest.follower).count()
        self.assertEqual(expected, 0)

    def test_user_can_see_followed_author(self):
        unfollowed_user = User.objects.create_user(username='auth')
        Post.objects.create(
            author=FollowTest.author,
            text='test text',
        )
        Follow.objects.create(
            user=FollowTest.follower,
            author=FollowTest.author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(str(first_object), 'test text')
        self.authorized_client.force_login(unfollowed_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        second_object = list(response.context['page_obj'])
        self.assertEqual(second_object, [])
