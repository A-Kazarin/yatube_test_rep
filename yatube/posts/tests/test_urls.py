from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

URL_INDEX = reverse('posts:index')
URL_POST_DETAIL = reverse('posts:post_detail')
URL_PROFILE = reverse('posts:profile')
URL_GROUP_LIST = reverse('posts:group_list')
URL_CREATE_POST = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовая группа.Описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            author=cls.test_post_author,
            group= self.group
        )
        cls.URL_TEST_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.test_post.id]
        )
        cls.URL_TEST_POST_EDIT = reverse(
            'posts:post_edit',
            args=[cls.test_post.id]
        )

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.test_post_author)


    def test_posts_urls_use_correct_template(self):
        """Проверка шаблонов приложения posts прошла успешно."""
        address_template_guest_client = {
            'posts/index.html': '/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/create_post.html': '/create/',
        }
        for address, expected_template in address_template_guest_client.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(
                    response,
                    expected_template,
                    f'неверный шаблон - {expected_template}'
                    f'для адресса {address}'
                )

    def test_location(self):
        addresses = [
            [URL_INDEX, HttpSTATUS.OK, self.client],
            [PostURLSTest.URL_TEST_POST_EDIT, HttpSTATUS.OK, self.author_client],
            [PostURLSTest.URL_TEST_POST_EDIT, HttpSTATUS.FOUND, self.authorized_client],
        ]
        for test in addresses:
            address, status, client = test
            self.assertEqual(
                client.get(address).status_code,
                status,
                f'{address} для {client} работает неправильно'

    def test_redirect(self):
        address_redirect_client = [
            [
                URL_CREATE_POST,
                f'/auth/login/?next={revesrse(posts:create_post)}',
                self.client
            ]
        ]
        for test in address_redirect_client :
            address, exp_redirect, client = test
            response = client.get(f'/auth/login/?next={revesrse(posts:create_post)}') # кое что добавить в get
            self.assertRedirects(
                response,
                exp_redirect
            )
