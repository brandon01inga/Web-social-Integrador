from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registrar_usuario, name='registro'),
    path('registro/registro-alumno/', views.vista_registro_alumno, name='registro_alumno'),
    path('registro/registro-profesor/', views.vista_registro_profesor, name='registro_profesor'),
    path('activar/<str:token>/', views.activar_cuenta, name='activar'),
]
