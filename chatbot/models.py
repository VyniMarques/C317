from django.db import models

class Usuario(models.Model):
    email = models.TextField(primary_key = True)
    nome = models.TextField(max_length= 255)
    area = models.TextField(max_length=150)
    senha = models.TextField(max_length=100)