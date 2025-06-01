from django.urls import path
from . import views
from .views import enviar_correo_prueba

urlpatterns = [
    path('registro/', views.registrar_usuario, name='registro'),
    path('activar/<uidb64>/<token>/', views.activar_usuario, name='activar'),
    path('probar-correo/', enviar_correo_prueba),
]
