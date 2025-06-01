from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UsuarioPersonalizado(AbstractUser):
    email = models.EmailField(unique=True)
    carrera = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username