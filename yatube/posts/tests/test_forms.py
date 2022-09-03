from email.mime import image
from xml.etree.ElementTree import Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from posts.models import Post,  Comment
import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateForm(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = PostForm()


    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestCreateForm.user)

    def test_create_post_auth(self):
        """
        Валидная форма создаёт новую запись в базе данных,
        затем перенаправляет на страницу профиля.
        """
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост',
            'author': TestCreateForm.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        obj = Post.objects.get(id=1)
        text = obj.text
        author = obj.author
        image = obj.image
        self.assertEqual(str(text), 'Тестовый пост')
        self.assertEqual(str(author), 'auth')
        self.assertEqual(image, 'posts/small.gif')

    def test_create_guest_client(self):
        """Проверка создание записи неавторизованного юзера"""
        form_data = {
            'text': 'Тестовый пост',
            'author': TestCreateForm.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_auth(self):
        """Изменение записи зарегестрировнным пользователем"""
        self.existing_post = Post.objects.create(
            text='Тестовый пост',
            author=TestCreateForm.user,)
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'author': TestCreateForm.user
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.existing_post.id}),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.existing_post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        obj = Post.objects.get(id=1)
        text = obj.text
        author = obj.author
        self.assertEqual(str(text), 'Тестовый пост 2')
        self.assertEqual(str(author), 'auth')

    def test_edit_post_guest_client(self):
        """Проверка изменения записи неавторизованного юзера"""
        self.existing_post = Post.objects.create(
            text='Тестовый пост',
            author=TestCreateForm.user,)
        form_data = {
            'text': 'Тестовый пост 2',
            'author': TestCreateForm.user
        }
        response = self.guest_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.existing_post.id}),
            data=form_data
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.existing_post.id}/edit/'
        )

    def test_comment_auth(self):
        """Возможность комментировать авторизованному"""
        len_comment = Comment.objects.count()
        post = Post.objects.create(
            author=TestCreateForm.user,
            text='test text',
        )
        form_data = {
            'post': post,
            'author': TestCreateForm.user,
            'text': 'Комментарий'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(str(Comment.objects.get(id=1)), 'Комментарий')
        self.assertEqual(Comment.objects.count(), len_comment + 1)