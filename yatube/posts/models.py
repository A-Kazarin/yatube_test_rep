from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст поста здесь')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey('Group',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              verbose_name='Сообщество',
                              related_name='posts')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:settings.LETTERS_LIMIT]


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='максимум 200 символов')
    slug = models.SlugField(max_length=100,
                            unique=True,
                            db_index=True,
                            verbose_name='Адрес',
                            help_text='адрес сообщества')
    description = models.TextField(verbose_name='Описание',
                                   help_text='введите описание сообщества')

    def __str__(self):
        return self.title
