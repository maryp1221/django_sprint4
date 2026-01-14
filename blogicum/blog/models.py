from core.models import CreatedAtMixin, PublishedMixin
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(PublishedMixin):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = 'blog_category'
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedMixin):
    name = models.CharField('Название места', max_length=256)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'blog_location'
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(PublishedMixin):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    image = models.ImageField(
        'Фото', blank=True, null=True, upload_to='post_attach/'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = 'blog_post'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', 'author')


class Comment(CreatedAtMixin):
    text = models.TextField(
        'Текст',
        max_length=4096,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        null=True,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments',
    )

    class Meta:
        db_table = 'blog_comment'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created_at',)
