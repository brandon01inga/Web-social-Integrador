from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from WebSocial import settings
from .models import UsuarioPersonalizado, Estudiante, Docente, TokensVerificacion


def enviar_correo_verificacion(usuario, token):
    asunto = 'Verificación de cuenta'
    mensaje = f""" Hola {usuario.nombre} {usuario.apellido},
    Gracias por registrarte en nuestra plataforma. Para completar tu registro, necesitamos que verifiques tu cuenta.

    Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:
    http://127.0.0.1:8000/activar/{token}/

    Este enlace es válido por 24 horas.

    Saludos.
    """

    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario.email],
        fail_silently=False,
    )

def registro_estudiante(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirmPassword')
        carrera = request.POST.get('carrera')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        ubicacion = request.POST.get('ubicacion')
        tipo_usuario = 'Estudiante'
        anio_ingreso = request.POST.get('anio_ingreso')
        ciclo = request.POST.get('ciclo')
        dni = request.POST.get('dni')
        username = nombre + apellido + dni

        if not nombre or not apellido or not email or not password or not carrera or not telefono or not fecha_nacimiento or not sexo or not ubicacion or not anio_ingreso or not ciclo or not dni:
            error = "Todos los campos son obligatorios."
            return render(request, 'usuarios/registro_alumno.html', {'error': error})

        dominio = '@utp.edu.pe'
        if not email.endswith(dominio):
            error = f"El correo electrónico debe tener el dominio {dominio}."
            return render(request, 'usuarios/registro_alumno.html', {'error': error})

        if password != password2:
            error = "Las contraseñas no coinciden."
            return render(request, 'Usuarios/registro_alumno.html', {'error': error})
        
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            error = "El correo electrónico ya está en uso."
            return render(request, 'Usuarios/registro_alumno.html', {'error': error})
        
        usuarioCreado = UsuarioPersonalizado.objects.create_user(
            username=username,
            email=email,
            password=password,
            nombre=nombre,
            apellido=apellido,
            carrera=carrera,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            ubicacion=ubicacion,
            tipoUsuario=tipo_usuario,
            dni=dni,
            is_active=False
        )

        Estudiante.objects.create(
            usuario=usuarioCreado,
            carrera=carrera,
            anio_ingreso= anio_ingreso,
            ciclo=ciclo
        )

        token = TokensVerificacion.objects.create(
            usuario=usuarioCreado,
            token=default_token_generator.make_token(usuarioCreado),
            fecha_expiracion= timezone.now() + timezone.timedelta(hours=24)
        )

        enviar_correo_verificacion(usuarioCreado, token.token)

        return render(request, 'usuarios/registro-espera.html', {'email': email}) 
    else:
        return render(request, 'usuarios/registro_alumno.html')

def registro_profesor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirmPassword')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        ubicacion = request.POST.get('ubicacion')
        tipo_usuario = 'Profesor'
        facultad_dirigido = request.POST.get('facultad_dirigido')
        carrera = request.POST.get('carrera')
        dni = request.POST.get('dni')
        username = nombre + apellido + dni

        if not nombre or not apellido or not email or not password or not telefono or not fecha_nacimiento or not sexo or not ubicacion or not facultad_dirigido or not carrera or not dni:
            error = "Todos los campos son obligatorios."
            return render(request, 'usuarios/registro_docente.html', {'error': error})

        if password != password2:
            error = "Las contraseñas no coinciden."
            return render(request, 'usuarios/registro_docente.html', {'error': error})
        
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            error = "El correo electrónico ya está en uso."
            return render(request, 'usuarios/registro_docente.html', {'error': error})
        
        usuarioCreado = UsuarioPersonalizado.objects.create_user(
            username=username,
            email=email,
            password=password,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            carrera=carrera,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            ubicacion=ubicacion,
            tipoUsuario=tipo_usuario,
            dni=dni,
            is_active=False
        )

        Docente.objects.create(
            usuario=usuarioCreado,
            facultadDirigido=facultad_dirigido            
        )

        token = TokensVerificacion.objects.create(
            usuario=usuarioCreado,
            token=default_token_generator.make_token(usuarioCreado),
            fecha_expiracion=timezone.now() + timedelta(hours=24)
        )

        enviar_correo_verificacion(usuarioCreado, token.token)

        return render(request, 'usuarios/registro-espera.html', {'email': email})
    else:
        return render(request, 'usuarios/registro_docente.html')


def activar_cuenta(request, token):
    try:
        token_obj = TokensVerificacion.objects.get(token=token)
    except TokensVerificacion.DoesNotExist:
        return render(request, 'usuarios/registro-error.html', {'error': 'Token inválido o expirado.'})

    if token_obj.fecha_expiracion < timezone.now():
        return render(request, 'usuarios/registro-error.html', {'error': 'Token expirado.'})

    usuario = token_obj.usuario
    usuario.is_active = True
    usuario.save()
    token_obj.delete()

    return render(request, 'usuarios/bienvenido.html', {'success': 'Cuenta activada exitosamente.'})


def registrar_usuario(request):
    return render(request, 'usuarios/registroOpcion.html')


def vista_registro_alumno(request):
    if request.method == 'POST':
        return registro_estudiante(request)
    return render(request, 'usuarios/registro_alumno.html')

def vista_registro_profesor(request):
    if request.method == 'POST':
        return registro_profesor(request)
    return render(request, 'usuarios/registro_docente.html')

