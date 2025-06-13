from django.db import models
from django.utils import timezone
from Usuarios.models import UsuarioPersonalizado


class Publicacion(models.Model):
    titulo = models.CharField(max_length=200,blank=True, null=True)
    imagen = models.ImageField(upload_to='imagenes_publicaciones/')
    autor = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return self.titulo or f"Publicación de {self.autor.username} - {self.fecha_publicacion.strftime('%Y-%m-%d')}"

    def eliminar(self):
        self.fecha_eliminacion = timezone.now()
        self.save()