from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UsuarioPersonalizado(AbstractUser):
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(max_length=150)
    dni = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')], blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    tipoUsuario = models.CharField(max_length=20, choices=[('estudiante', 'Estudiante'), ('profesor', 'Profesor')])
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Docente(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE)
    facultadDirigido = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Docente: {self.usuario.username} - {self.departamento}"
    
class Estudiante(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    anio_ingreso = models.IntegerField(blank=True, null=True)
    ciclo = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"Estudiante: {self.usuario.username}"
    
class TokensVerificacion(models.Model):
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()

    def __str__(self):
        return f"Token de verificación para {self.usuario.username}"
    