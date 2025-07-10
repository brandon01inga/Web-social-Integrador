"""
VIEWS.PY - MÓDULO DE GESTIÓN DE PUBLICACIONES
============================================

Este módulo contiene todas las vistas relacionadas con el manejo de publicaciones en la red social.
Incluye funcionalidades para:

1. CREACIÓN DE PUBLICACIONES:
   - Formulario para crear nuevas publicaciones
   - Subida de archivos e imágenes
   - Asignación automática del autor (usuario logueado)

2. VISUALIZACIÓN DE PUBLICACIONES:
   - Lista general de todas las publicaciones activas
   - Publicaciones filtradas por usuario específico
   - Ordenamiento por fecha de publicación (más recientes primero)

3. ELIMINACIÓN DE PUBLICACIONES:
   - Eliminación lógica (soft delete) para preservar datos
   - Verificación de permisos (solo el autor puede eliminar)
   - Redirección automática después de eliminar

CARACTERÍSTICAS TÉCNICAS:
- Usa decorador @login_required para proteger funciones
- Implementa eliminación lógica (fecha_eliminacion) en lugar de borrado físico
- Maneja formularios con archivos adjuntos
- Filtros por estado activo (fecha_eliminacion__isnull=True)

AUTOR: [Tu nombre]
FECHA: [Fecha actual]
"""

# Importaciones necesarias para vistas, formularios y autenticación
from django.shortcuts import render, redirect, get_object_or_404  # Funciones para renderizar, redireccionar y obtener objetos
from .forms import PublicacionForm  # Formulario personalizado para crear publicaciones
from django.contrib.auth.decorators import login_required  # Decorador para proteger vistas que requieren autenticación
from .models import Publicacion  # Modelo de publicaciones
from Usuarios.models import UsuarioPersonalizado  # Modelo de usuarios personalizado

@login_required  #  PROTECCIÓN: Solo usuarios autenticados pueden crear publicaciones
def crear_publicacion(request):
    """
    Maneja la creación de nuevas publicaciones por parte de usuarios autenticados.
    
    Esta vista permite a los usuarios crear publicaciones con texto e imágenes.
    El autor de la publicación se asigna automáticamente al usuario logueado.
    
    Args:
        request: HttpRequest object que contiene los datos del formulario
        
    Returns:
        HttpResponse: 
        - Si POST exitoso: Redirección a lista de publicaciones
        - Si GET o error: Formulario de creación de publicación
        
    Flujo:
        1. Usuario envía formulario (POST)
        2. Se valida el formulario
        3. Se asigna el autor automáticamente
        4. Se guarda en base de datos
        5. Se redirige a la lista de publicaciones
    """
    if request.method == 'POST':
        # PROCESAMIENTO DEL FORMULARIO ENVIADO
        
        # Creamos el formulario con los datos POST y archivos subidos
        form = PublicacionForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Guardamos el formulario pero sin commitear a la BD todavía
            publicacion = form.save(commit=False)
            
            # 👤 ASIGNACIÓN AUTOMÁTICA: El autor es el usuario logueado
            publicacion.autor = request.user
            
            # Ahora sí guardamos en la base de datos
            publicacion.save()
            
            # ÉXITO: Redirigimos a la lista de publicaciones
            return redirect('lista_publicaciones')
    else:
        # Si es GET, creamos un formulario vacío
        form = PublicacionForm()
    
    # Renderizamos la página con el formulario (vacío o con errores)
    return render(request, 'publicaciones/crear_publicacion.html', {'form': form})


def lista_publicaciones(request):
    """
    Vista híbrida que maneja tanto la visualización como la creación de publicaciones.
    
    Esta vista tiene doble funcionalidad:
    1. Muestra todas las publicaciones activas en orden cronológico inverso
    2. Permite crear nuevas publicaciones directamente desde la lista
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Página con lista de publicaciones y formulario de creación
        
    Características:
        - Muestra solo publicaciones NO eliminadas (eliminación lógica)
        - Orden: Más recientes primero (-fecha_publicacion)
        - Formulario integrado para crear publicaciones rápidamente
    """
    if request.method == 'POST':
        # CREACIÓN RÁPIDA DE PUBLICACIÓN DESDE LA LISTA
        
        # Creamos formulario con datos POST y archivos (si los hay)
        form = PublicacionForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            # Guardamos sin commitear para asignar el autor
            pub = form.save(commit=False)
            
            #  ASIGNACIÓN AUTOMÁTICA: El autor es el usuario logueado
            pub.autor = request.user
            
            # Guardamos en la base de datos
            pub.save()
            
            #  RECARGA: Redirigimos para evitar reenvío de formulario
            return redirect('lista_publicaciones')
    else:
        # Si es GET, creamos formulario vacío para mostrar
        form = PublicacionForm()

    # OBTENCIÓN DE PUBLICACIONES ACTIVAS
    
    #  FILTRO IMPORTANTE: Solo publicaciones NO eliminadas lógicamente
    # fecha_eliminacion__isnull=True significa que no tienen fecha de eliminación
    publicaciones = Publicacion.objects.filter(fecha_eliminacion__isnull=True).order_by('-fecha_publicacion')
    
    # Renderizamos la página con las publicaciones y el formulario
    return render(request, 'publicaciones/lista_publicaciones.html', {
        'form': form,                    # Formulario para crear nueva publicación
        'publicaciones': publicaciones   # Lista de publicaciones existentes
    })


def publicaciones_por_usuario(request, username):
    """
    Muestra todas las publicaciones activas de un usuario específico.
    
    Esta vista permite ver el "perfil de publicaciones" de cualquier usuario,
    mostrando solo sus publicaciones que no han sido eliminadas.
    
    Args:
        request: HttpRequest object
        username: String del nombre de usuario cuyas publicaciones queremos ver
        
    Returns:
        HttpResponse: Página con las publicaciones del usuario específico
        
    Raises:
        Http404: Si el usuario no existe en la base de datos
        
    Características:
        - Usa get_object_or_404 para manejo seguro de usuarios inexistentes
        - Filtra solo publicaciones activas (no eliminadas)
        - Orden cronológico inverso (más recientes primero)
    """
    # BÚSQUEDA SEGURA: Si el usuario no existe, lanza error 404
    usuario = get_object_or_404(UsuarioPersonalizado, username=username)
    
    #  FILTRO DE PUBLICACIONES:
    # - Solo publicaciones NO eliminadas (fecha_eliminacion__isnull=True)
    # - Ordenadas por fecha de publicación descendente
    # NOTA: Aquí falta filtrar por autor=usuario para mostrar solo sus publicaciones
    publicaciones = Publicacion.objects.filter(
        autor=usuario, 
        fecha_eliminacion__isnull=True
    ).order_by('-fecha_publicacion')
    
    # Renderizamos la página del perfil del usuario
    return render(request, 'publicaciones/publicaciones_usuario.html', {
        'usuario': usuario,              # Información del usuario
        'publicaciones': publicaciones   # Sus publicaciones activas
    })

@login_required  #  PROTECCIÓN: Solo usuarios autenticados pueden eliminar publicaciones
def eliminar_publicacion(request, pk):
    """
    Realiza eliminación lógica de una publicación.
    
    Esta vista permite eliminar publicaciones usando el concepto de "soft delete"
    (eliminación lógica), donde no se borra físicamente el registro sino que
    se marca con una fecha de eliminación.
    
    Args:
        request: HttpRequest object
        pk: Primary key (ID) de la publicación a eliminar
        
    Returns:
        HttpResponse: Redirección a la lista de publicaciones
        
    Características de Seguridad:
        - Solo usuarios autenticados pueden acceder (@login_required)
        - Solo el autor de la publicación puede eliminarla
        - Usa eliminación lógica para preservar datos
        
    Flujo:
        1. Busca la publicación por ID (404 si no existe)
        2. Verifica que el usuario sea el autor
        3. Marca la publicación como eliminada (método eliminar())
        4. Redirige a la lista de publicaciones
    """
    #  BÚSQUEDA SEGURA: Si la publicación no existe, lanza error 404
    publicacion = get_object_or_404(Publicacion, pk=pk)
    
    #  VERIFICACIÓN DE PERMISOS: Solo el autor puede eliminar su publicación
    if request.user == publicacion.autor:
        # ELIMINACIÓN LÓGICA: Usa el método personalizado del modelo
        # Este método probablemente asigna timezone.now() a fecha_eliminacion
        publicacion.eliminar()  # usa el método lógico
    
    #  REDIRECCIÓN: Volvemos a la lista de publicaciones
    # La publicación eliminada ya no aparecerá porque el filtro excluye
    # registros con fecha_eliminacion no nula
    return redirect('lista_publicaciones')

# ===============================================================================
# NOTAS TÉCNICAS Y POSIBLES MEJORAS:
# ===============================================================================

"""
 POSIBLE BUG DETECTADO:
En la función publicaciones_por_usuario(), falta filtrar por autor:

CÓDIGO ACTUAL:
publicaciones = Publicacion.objects.filter(fecha_eliminacion__isnull=True)

CÓDIGO SUGERIDO:
publicaciones = Publicacion.objects.filter(
    autor=usuario, 
    fecha_eliminacion__isnull=True
).order_by('-fecha_publicacion')

Sin este filtro, se muestran todas las publicaciones de todos los usuarios,
no solo las del usuario específico solicitado.

 MEJORAS SUGERIDAS:

1. PAGINACIÓN: Para listas largas de publicaciones
2. PERMISOS: Middleware para verificar permisos de manera centralizada
3. AJAX: Para crear publicaciones sin recargar la página
4. VALIDACIÓN: Verificar tamaño y tipo de archivos subidos
5. CACHE: Para optimizar consultas frecuentes
6. LOGGING: Para auditar eliminaciones de publicaciones

 PATRONES IMPLEMENTADOS:
- Repository Pattern: Uso de managers de Django
- Soft Delete: Eliminación lógica preservando datos
- Authentication Decorators: Protección de vistas
- Safe Object Retrieval: get_object_or_404 para manejo de errores
"""
