from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from mailing_service.settings import MANAGER_GROUP_NAME


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)

        # Убедимся, что username установлен
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Никнейм'
    )
    email = models.EmailField('Email', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    is_blocked = models.BooleanField(default=False)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    is_staff = models.BooleanField('Статус персонала', default=False)
    is_active = models.BooleanField('Активный', default=True)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

        permissions = [
            ("can_view_all", "Can view all objects"),
            ("can_block_users", "Can block users"),
            ("can_disable_mailings", "Can disable mailings"),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def is_manager(self):
        return self.groups.filter(name=MANAGER_GROUP_NAME).exists()
