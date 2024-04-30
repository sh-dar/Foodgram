from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import MAX_LENGHT_FIELD


class MyUser(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGHT_FIELD,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGHT_FIELD,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGHT_FIELD,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='following',
    )
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author',
            ),
        )
