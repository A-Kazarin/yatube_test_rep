from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

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
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

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


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='comments',
        verbose_name='Пост комментария',
        help_text='Пост комментария'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор подписки',
        help_text='Автор подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            name='unique_follow',
            fields=['author', 'user'],
        )]
