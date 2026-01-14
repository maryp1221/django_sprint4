from django.db import models


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class PublishedMixin(CreatedAtMixin):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    class Meta:
        abstract = True
