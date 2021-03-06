from http import HTTPStatus

from .const import AUTHOR_USERNAME, GROUP_SLUG, URL_INDEX, URL_PROFILE
from .const import URL_GROUP_LIST, URL_CREATE_POST
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


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
            group=cls.test_group
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
        """Проверка шаблонов приложения posts."""
        address_template_guest_client = {
            URL_INDEX: 'posts/index.html',
            PostURLTests.URL_TEST_POST_DETAIL: 'posts/post_detail.html',
            URL_PROFILE: 'posts/profile.html',
            URL_GROUP_LIST: 'posts/group_list.html',
            URL_CREATE_POST: 'posts/create_post.html',
        }
        for address, expected_template in (
                address_template_guest_client.items()):
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(
                    response,
                    expected_template,
                    f'неверный шаблон - {expected_template}'
                    f'для адресса {address}'
                )

    def test_location(self):
        """Проверка адресов приложения posts."""
        addresses = [
            [URL_INDEX, HTTPStatus.OK, self.client],
            [PostURLTests.URL_TEST_POST_EDIT,
             HTTPStatus.OK, self.author_client],
            [PostURLTests.URL_TEST_POST_EDIT,
             HTTPStatus.FOUND, self.authorized_client],
            [URL_GROUP_LIST, HTTPStatus.OK, self.client],
            [URL_PROFILE, HTTPStatus.OK, self.client],
            [URL_CREATE_POST, HTTPStatus.OK, self.authorized_client]

        ]
        for test in addresses:
            address, status, client = test
            self.assertEqual(
                client.get(address).status_code,
                status,
                f'{address} для {client} работает неправильно')

    def test_redirect(self):
        """Проверка перенаправлений."""
        address_redirect_client = [
            [
                URL_CREATE_POST,
                f'/auth/login/?next={URL_CREATE_POST}',
                self.client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                f'/auth/login/?next={PostURLTests.URL_TEST_POST_EDIT}',
                self.client
            ],
        ]
        for test in address_redirect_client:
            address, exp_redirect, client = test
            response = client.get(address, follow=True)
            self.assertRedirects(
                response,
                exp_redirect
            )
