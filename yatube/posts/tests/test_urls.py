from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR_USERNAME = username
GROUP_SLUG = slug

URL_INDEX = reverse('posts:index')
URL_POST_DETAIL = reverse('posts:post_detail', args='PostURLTests.URL_TEST_POST_DETAIL')
URL_PROFILE = reverse('posts:profile', args='AUTHOR_USERNAME')
URL_GROUP_LIST = reverse('posts:group_list', args='GROUP_SLUG')
URL_CREATE_POST = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            AUTHOR_USERNAME
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            GROUP_SLUG,
            description='Тестовая группа.Описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            author=cls.test_post_author,
            group=cls.group.id
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
            URL_INDEX: 'posts/index.html',
            URL_POST_DETAIL: 'posts/post_detail.html',
            URL_PROFILE: 'posts/profile.html',
            URL_GROUP_LIST: 'posts/group_list.html',
            URL_CREATE_POST: 'posts/create_post.html',
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
            [PostURLSTest.URL_TEST_POST_EDIT, HTTPStatus.OK, self.author_client],
            [PostURLSTest.URL_TEST_POST_EDIT, HTTPStatus.FOUND, self.authorized_client],
        ]
        for test in addresses:
            address, status, client = test
            self.assertEqual(
                client.get(address).status_code,
                status,
                f'{address} для {client} работает неправильно')

    def test_redirect(self):
        address_redirect_client = [
            [
                URL_CREATE_POST,
                f'/auth/login/?next={reverse(URL_CREATE_POST)}',
                self.client
            ]
        ]
        for test in address_redirect_client:
            address, exp_redirect, client = test
            response = client.get(f'/auth/login/?next={reverse(URL_CREATE_POST)}')  # кое что добавить в get
            self.assertRedirects(
                response,
                exp_redirect
            )
