from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, area, password=None):
        if not email:
            raise ValueError('O email é obrigatório')
        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
            area=area,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, area, password):
        user = self.create_user(
            email=email,
            nome=nome,
            area=area,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser):
    email = models.TextField(primary_key=True)
    nome = models.TextField(max_length=255)
    area = models.TextField(max_length=150)
    senha = models.CharField(max_length=100)

    objects = UsuarioManager()

    @property
    def password(self):
        return self.senha

    @password.setter
    def password(self, raw_password):
        self.senha = make_password(raw_password)

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome
from django.db import models

class TokenizedPhrase(models.Model):
    tokenized_phrase = models.CharField(max_length=255)
    original_phrase = models.CharField(max_length=255)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.tokenized_phrase
