from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_str = (
            (self.post, self.post.text[:15]),
            (self.group, self.group.title),
        )
        for value, expected in test_str:
            with self.subTest(value=value):
                self.assertEqual(str(value), expected)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        task = PostModelTest.group
        help_text = task._meta.get_field('title').help_text
        self.assertEqual(help_text, 'максимум 200 символов')
