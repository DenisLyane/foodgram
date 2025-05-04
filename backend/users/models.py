from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

from users.constants import EMEIL_LENGTH, NAME_LENGTH


class User(AbstractUser):

    first_name = models.CharField(
        'Имя',
        max_length=NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_LENGTH,
        blank=False
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='users/avatar/'
    )
    email = models.EmailField(
        'Адрес эл.почты',
        max_length=EMEIL_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Логин',
        max_length=NAME_LENGTH,
        unique=True,
        blank=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):

    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'subscribing'], name='unique_together'
            ),
            CheckConstraint(
                check=~Q(user=F('subscribing')),
                name='chek_self_subscription'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.subscribing}'
