from django.shortcuts import render, redirect, get_object_or_404
from .forms import PublicacionForm
from django.contrib.auth.decorators import login_required
from .models import Publicacion
from Usuarios.models import UsuarioPersonalizado

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()
            return redirect('lista_publicaciones')
    else:
        form = PublicacionForm()
    
    return render(request, 'publicaciones/crear_publicacion.html', {'form': form})


def lista_publicaciones(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.autor = request.user
            pub.save()
            return redirect('lista_publicaciones')
    else:
        form = PublicacionForm()

    publicaciones = Publicacion.objects.filter(fecha_eliminacion__isnull=True).order_by('-fecha_publicacion')
    return render(request, 'publicaciones/lista_publicaciones.html', {
        'form': form,
        'publicaciones': publicaciones
    })


def publicaciones_por_usuario(request, username):
    usuario = get_object_or_404(UsuarioPersonalizado, username=username)
    publicaciones = Publicacion.objects.filter(fecha_eliminacion__isnull=True).order_by('-fecha_publicacion')
    return render(request, 'publicaciones/publicaciones_usuario.html', {
        'usuario': usuario,
        'publicaciones': publicaciones
    })

@login_required
def eliminar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.user == publicacion.autor:
        publicacion.eliminar()  # 🧠 usa el método lógico
    return redirect('lista_publicaciones')
