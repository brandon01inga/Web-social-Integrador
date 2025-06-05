from django.db import models
from Usuarios.models import Usuario

# Create your models here.

class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='imagenes_publicaciones/')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo