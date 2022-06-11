from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR_USERNAME = 'TestName'
GROUP_SLUG = 'TestSlug'

URL_INDEX = reverse('posts:index')
URL_PROFILE = reverse('posts:profile', args=[AUTHOR_USERNAME])
URL_GROUP_LIST = reverse('posts:group_list', args=[GROUP_SLUG])
URL_CREATE_POST = reverse('posts:post_create')


class PostFormsTests(TestCase):
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
        cls.FORM_TEST_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.test_post.id]
        )
        cls.FORM_TEST_POST_EDIT = reverse(
            'posts:post_edit',
            args=[cls.test_post.id]
        )

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.author_client = Client()
        self.author_client.force_login(PostFormsTests.test_post_author)

    def test_create_post_form(self):
        """Создание поста с помощью формы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostFormsTests.test_group.id,
        }
        response = self.author_client.post(
            URL_CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, URL_PROFILE)
        self.assertTrue(Post.objects.filter(
            group__slug=self.test_group.slug,
            text=form_data.get('text'),
            author=self.test_post_author,
        ).exists())

    def test_edit_post_form(self):
        """Изменение поста с помощью формы"""
        form_data = {
            'text': 'Измененный пост',
            'group': PostFormsTests.test_group.id,
        }
        posts_count = Post.objects.count()
        response = self.author_client.post(
            PostFormsTests.FORM_TEST_POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, PostFormsTests.FORM_TEST_POST_DETAIL)
        self.assertTrue(Post.objects.filter(
            group__slug=self.test_group.slug,
            text=form_data.get('text'),
            post=PostFormsTests.test_post,
        ).exists())
