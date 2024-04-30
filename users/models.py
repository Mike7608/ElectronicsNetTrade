from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='E-mail')
    phone = models.CharField(max_length=35, verbose_name='Телефон', null=True, blank=True)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', null=True, blank=True)
    city = models.CharField(max_length=30, verbose_name='Город')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
