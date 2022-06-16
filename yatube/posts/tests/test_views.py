from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',

        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.wrong_group = Group.objects.create(
            title='Тестовое название группы 2',
            slug='test-slug2',
            description='Тестовое описание группы 2'
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.user)

    def test_pages_with_posts_show_correct_context(self):
        """Шаблоны index, group_list и profile сформированы
        с правильным контекстом.
        """
        templates_page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author}),
        }
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertIn(self.post, response.context.get('page_obj'))

    def test_both_profile_and_group_show_correct_context(self):
        """Шаблоны group_posts и  profile сформированы
        с правильным контекстом
        """
        templates_page_names = [
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                'group',
                self.group),
            (reverse('posts:profile', kwargs={'username': self.user.username}),
                'author',
                self.user),
        ]
        for reverse_name, context_name, expected in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(response.context.get(context_name), expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get(
            'form').instance,
            self.post
        )

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_new_post_not_in_a_wrong_group(self):
        """Пост не появляется в не своей группе"""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.wrong_group.slug
            })
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        self.post = Post.objects.bulk_create(
            [
                Post(
                    text='Тестируем  паджинатор',
                    author=self.user,
                    group=self.group,
                ),
            ] * 13
        )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            reverse('posts:index'): settings.POSTS_PER_PAGE,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): settings.POSTS_PER_PAGE,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            settings.POSTS_PER_PAGE,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template)
                self.assertEqual(len(response.context['page_obj']), expected)
