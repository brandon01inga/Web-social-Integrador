"""
VIEWS.PY - MÓDULO DE GESTIÓN DE USUARIOS
==========================================

Este módulo contiene todas las vistas relacionadas con la gestión de usuarios en la plataforma social.
Incluye funcionalidades para:

1. REGISTRO DE USUARIOS:
   - Registro de estudiantes (email debe empezar con 'u' y usar dominio @utp.edu.pe)
   - Registro de docentes (email debe empezar con 'c' y usar dominio @utp.edu.pe)
   - Validación de datos y verificación por correo electrónico

2. VERIFICACIÓN DE CUENTAS:
   - Envío de correos de verificación con tokens temporales
   - Activación de cuentas mediante enlaces únicos
   - Manejo de tokens expirados con regeneración automática

3. AUTENTICACIÓN:
   - Inicio de sesión con validación de credenciales
   - Verificación del estado de activación de cuentas
   - Manejo de errores de autenticación

REGLAS DE NEGOCIO:
- Estudiantes: email empieza con 'u' + dominio @utp.edu.pe
- Docentes: email empieza con 'c' + dominio @utp.edu.pe
- Tokens de verificación válidos por 24 horas
- Cuentas inactivas hasta verificar email

AUTOR: [Tu nombre]
FECHA: [Fecha actual]
"""

# Importaciones necesarias para el manejo de fechas, vistas de Django y envío de correos
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

# Importamos la configuración del proyecto y los modelos de usuarios
from WebSocial import settings
from .models import UsuarioPersonalizado, Estudiante, Docente, TokensVerificacion


def enviar_correo_verificacion(usuario, token):
    """
    Envía un correo electrónico de verificación al usuario recién registrado.
    
    Args:
        usuario: Instancia del modelo UsuarioPersonalizado
        token: Token único para verificar la cuenta del usuario
    
    Returns:
        None (envía el correo pero no retorna nada)
    """
    # Definimos el asunto del correo
    asunto = 'Verificación de cuenta'
    
    # Creamos el mensaje personalizado con el nombre del usuario y el enlace de verificación
    mensaje = f""" Hola {usuario.nombre} {usuario.apellido},
    Gracias por registrarte en nuestra plataforma. Para completar tu registro, necesitamos que verifiques tu cuenta.

    Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:
    http://127.0.0.1:8000/activar/{token}/

    Este enlace es válido por 24 horas.

    Saludos.
    """

    # Enviamos el correo usando la configuración SMTP del proyecto
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,  # Remitente configurado en settings
        [usuario.email],           # Destinatario
        fail_silently=False,       # Si hay error, lanza excepción
    )

def registro_estudiante(request):
    """
    Maneja el registro de nuevos estudiantes en la plataforma.
    
    Valida los datos del formulario, verifica que el email sea de estudiante (@utp.edu.pe y empiece con 'u'),
    crea el usuario y estudiante en la base de datos, y envía un correo de verificación.
    
    Args:
        request: HttpRequest object que contiene los datos del formulario
        
    Returns:
        HttpResponse: Renderiza la página correspondiente según el resultado
    """
    if request.method == 'POST':
        # Extraemos todos los datos del formulario POST
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
        tipo_usuario = 'Estudiante'  # Tipo fijo para esta función
        anio_ingreso = request.POST.get('anio_ingreso')
        ciclo = request.POST.get('ciclo')
        dni = request.POST.get('dni')
        
        # Generamos un username único combinando nombre + apellido + dni
        username = nombre + apellido + dni

        # VALIDACIONES DE DATOS
        
        # 1. Verificamos que todos los campos obligatorios estén completos
        if not nombre or not apellido or not email or not password or not carrera or not telefono or not fecha_nacimiento or not sexo or not ubicacion or not anio_ingreso or not ciclo or not dni:
            error = "Todos los campos son obligatorios."
            return render(request, 'usuarios/registro_alumno.html', {'error': error})
        
        # 2. Verificamos que el email de estudiante empiece con 'u' (regla de negocio UTP)
        if not email.casefold().startswith('u'):
            error = "El correo electrónico de los estudiantes empieza con u."
            return render(request, 'usuarios/registro_alumno.html', {'error': error})

        # 3. Verificamos que el email no esté ya registrado en el sistema
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            error = "El correo electrónico ya está en uso, porfavor intente iniciar sesion."
            return render(request, 'Usuarios/registro_alumno.html', {'error': error})

        # 4. Verificamos que el email tenga el dominio institucional correcto
        dominio = '@utp.edu.pe'
        if not email.endswith(dominio):
            error = f"El correo electrónico debe tener el dominio {dominio}."
            return render(request, 'usuarios/registro_alumno.html', {'error': error})

        # 5. Verificamos que las contraseñas coincidan
        if password != password2:
            error = "Las contraseñas no coinciden."
            return render(request, 'Usuarios/registro_alumno.html', {'error': error})
        
        
        # CREACIÓN DE USUARIO Y ESTUDIANTE
        
        # Creamos el usuario personalizado con is_active=False (requiere verificación por email)
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
            is_active=False  # Usuario inactivo hasta verificar email
        )

        # Creamos el registro específico de estudiante con datos académicos
        Estudiante.objects.create(
            usuario=usuarioCreado,
            carrera=carrera,
            anio_ingreso= anio_ingreso,
            ciclo=ciclo
        )

        # GENERACIÓN Y ENVÍO DE TOKEN DE VERIFICACIÓN
        
        # Creamos un token de verificación válido por 24 horas
        token = TokensVerificacion.objects.create(
            usuario=usuarioCreado,
            token=default_token_generator.make_token(usuarioCreado),
            fecha_expiracion= timezone.now() + timezone.timedelta(hours=24)
        )

        # Enviamos el correo de verificación
        enviar_correo_verificacion(usuarioCreado, token.token)

        # Mostramos página de confirmación con el email del usuario
        return render(request, 'usuarios/registro-espera.html', {'email': email}) 
    else:
        # Si es GET, solo mostramos el formulario de registro
        return render(request, 'usuarios/registro_alumno.html')

def registro_profesor(request):
    """
    Maneja el registro de nuevos docentes en la plataforma.
    
    Valida los datos del formulario, verifica que el email sea de docente (@utp.edu.pe y empiece con 'c'),
    crea el usuario y docente en la base de datos, y envía un correo de verificación.
    
    Args:
        request: HttpRequest object que contiene los datos del formulario
        
    Returns:
        HttpResponse: Renderiza la página correspondiente según el resultado
    """
    if request.method == 'POST':
        # Extraemos todos los datos del formulario POST
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirmPassword')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        ubicacion = request.POST.get('ubicacion')
        tipo_usuario = 'Profesor'  # Tipo fijo para esta función
        facultad_dirigido = request.POST.get('facultad_dirigido')
        carrera = request.POST.get('carrera')
        dni = request.POST.get('dni')
        
        # Generamos un username único combinando nombre + apellido + dni
        username = nombre + apellido + dni

        # VALIDACIONES DE DATOS
        
        # 1. Verificamos que el email no esté ya registrado en el sistema
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            error = "El correo electrónico ya está en uso, porfavor intente iniciar sesion."
            return render(request, 'usuarios/registro_docente.html', {'error': error})

        # 2. Verificamos que todos los campos obligatorios estén completos
        if not nombre or not apellido or not email or not password or not telefono or not fecha_nacimiento or not sexo or not ubicacion or not facultad_dirigido or not carrera or not dni:
            error = "Todos los campos son obligatorios."
            return render(request, 'usuarios/registro_docente.html', {'error': error})
        
        # 3. Verificamos que el email de docente empiece con 'c' (regla de negocio UTP)
        if not email.casefold().startswith('c'):
            error = "El correo electrónico de los docentes empieza con c."
            return render(request, 'usuarios/registro_docente.html', {'error': error})

        # 4. Verificamos que el email tenga el dominio institucional correcto
        dominio = '@utp.edu.pe'
        if not email.endswith(dominio):
            error = f"El correo electrónico debe tener el dominio {dominio}."
            return render(request, 'usuarios/registro_docente.html', {'error': error})

        # 5. Verificamos que las contraseñas coincidan
        if password != password2:
            error = "Las contraseñas no coinciden."
            return render(request, 'usuarios/registro_docente.html', {'error': error})
        
        # CREACIÓN DE USUARIO Y DOCENTE
        
        # Creamos el usuario personalizado con is_active=False (requiere verificación por email)
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
            is_active=False  # Usuario inactivo hasta verificar email
        )

        # Creamos el registro específico de docente con datos académicos
        Docente.objects.create(
            usuario=usuarioCreado,
            facultadDirigido=facultad_dirigido            
        )

        # GENERACIÓN Y ENVÍO DE TOKEN DE VERIFICACIÓN
        
        # Creamos un token de verificación válido por 24 horas
        token = TokensVerificacion.objects.create(
            usuario=usuarioCreado,
            token=default_token_generator.make_token(usuarioCreado),
            fecha_expiracion=timezone.now() + timedelta(hours=24)
        )

        # Enviamos el correo de verificación
        enviar_correo_verificacion(usuarioCreado, token.token)

        # Mostramos página de confirmación con el email del usuario
        return render(request, 'usuarios/registro-espera.html', {'email': email})
    else:
        # Si es GET, solo mostramos el formulario de registro
        return render(request, 'usuarios/registro_docente.html')


def activar_cuenta(request, token):
    """
    Activa la cuenta de un usuario usando el token enviado por correo electrónico.
    
    Verifica que el token sea válido y no haya expirado, luego activa la cuenta del usuario
    y elimina el token de la base de datos.
    
    Args:
        request: HttpRequest object
        token: String del token de verificación enviado por URL
        
    Returns:
        HttpResponse: Página de éxito o error según el resultado
    """
    try:
        # Intentamos encontrar el token en la base de datos
        token_obj = TokensVerificacion.objects.get(token=token)
    except TokensVerificacion.DoesNotExist:
        # Si el token no existe, mostramos error
        return render(request, 'usuarios/registro-error.html', {'error': 'Token inválido o expirado.'})

    # Verificamos si el token ha expirado comparando con la fecha actual
    if token_obj.fecha_expiracion < timezone.now():
        return render(request, 'usuarios/registro-error.html', {'error': 'Token expirado.'})

    # Si todo está bien, activamos la cuenta del usuario
    usuario = token_obj.usuario
    usuario.is_active = True  # Activamos la cuenta
    usuario.save()            # Guardamos los cambios
    
    # Eliminamos el token ya que ya fue usado (seguridad)
    token_obj.delete()

    # Mostramos página de éxito
    return render(request, 'usuarios/bienvenido.html', {'success': 'Cuenta activada exitosamente.'})


def registrar_usuario(request):
    """
    Vista simple que muestra las opciones de registro (estudiante o docente).
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Página con opciones de registro
    """
    return render(request, 'usuarios/registroOpcion.html')

def vista_registro_alumno(request):
    """
    Vista wrapper para el registro de alumnos.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Resultado de registro_estudiante() o formulario
    """
    if request.method == 'POST':
        return registro_estudiante(request)
    return render(request, 'usuarios/registro_alumno.html')

def vista_registro_profesor(request):
    """
    Vista wrapper para el registro de profesores.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Resultado de registro_profesor() o formulario
    """
    if request.method == 'POST':
        return registro_profesor(request)
    return render(request, 'usuarios/registro_docente.html')



def iniciar_sesion(request):
    """
    Maneja el proceso de inicio de sesión de usuarios.
    
    Valida las credenciales, verifica el estado de activación de la cuenta,
    maneja tokens expirados regenerándolos automáticamente.
    
    Args:
        request: HttpRequest object que contiene email y contraseña
        
    Returns:
        HttpResponse: Página de bienvenida si es exitoso, o error si falla
    """
    if request.method == 'POST':
        # Extraemos las credenciales del formulario
        email = request.POST.get('email')
        password = request.POST.get('contrasena')
        
        # VALIDACIÓN BÁSICA DE CAMPOS
        if not email or not password:
            error = "Por favor, completa todos los campos."
            return render(request, 'usuarios/iniciar_sesion.html', {'error': error})
        
        try:
            # BÚSQUEDA Y VALIDACIÓN DEL USUARIO
            
            # Buscamos el usuario por email
            usuario = UsuarioPersonalizado.objects.get(email=email)
            
            # MANEJO DE TOKENS DE VERIFICACIÓN
            
            # Verificamos si existe un token de verificación para este usuario
            token = TokensVerificacion.objects.filter(usuario=usuario).first()
            
            # Si hay un token y está expirado, lo regeneramos automáticamente
            if token and token.fecha_expiracion < timezone.now():
                token.delete()  # Eliminamos el token expirado
                
                # Creamos un nuevo token válido por 24 horas
                nuevo_token = TokensVerificacion.objects.create(
                    usuario=usuario,
                    token=default_token_generator.make_token(usuario),
                    fecha_expiracion=timezone.now() + timedelta(hours=24)
                )

                # Reenviamos el correo de verificación
                enviar_correo_verificacion(usuario, nuevo_token.token)

                return render(request, 'usuarios/registro-error.html', 
                            {'error': 'Token expirado. Por favor, verifica tu correo electrónico nuevamente.'})

            # VERIFICACIÓN DE ESTADO DE LA CUENTA
            
            # Si la cuenta no está activa y no tiene token, mostrar error
            if not usuario.is_active:
                if not TokensVerificacion.objects.filter(usuario=usuario).exists():
                    return render(request, 'usuarios/registro-error.html', 
                                {'error': 'Cuenta no activada. Por favor, verifica tu correo electrónico.'})

            # VALIDACIÓN DE CREDENCIALES
            
            # Verificamos que el email coincida (verificación adicional)
            if not usuario.check_email(email):
                error = "El correo electrónico no coincide con el usuario."
                return render(request, 'usuarios/iniciar_sesion.html', {'error': error})
            
            # Verificamos la contraseña
            if usuario.check_password(password):
                # Si la contraseña es correcta pero la cuenta no está activa
                if not usuario.is_active:
                    return render(request, 'usuarios/registro-error.html', 
                                {'error': 'Cuenta no activada. Por favor, verifica tu correo electrónico.'})
                
                # LOGIN EXITOSO - redirigimos a la página de bienvenida
                return render(request, 'usuarios/bienvenido.html', {'usuario': usuario})
            else:
                # Contraseña incorrecta
                error = "Contraseña incorrecta."
                return render(request, 'usuarios/iniciar_sesion.html', {'error': error})
                
        except UsuarioPersonalizado.DoesNotExist:
            # El email no está registrado en el sistema
            error = "El correo electrónico no está registrado."
            return render(request, 'usuarios/iniciar_sesion.html', {'error': error})

    # Si es GET, mostramos el formulario de login
    return render(request, 'usuarios/iniciar_sesion.html')

def vista_iniciar_sesion(request):
    """
    Vista wrapper para el inicio de sesión.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Resultado de iniciar_sesion() o formulario
    """
    if request.method == 'POST':
        return iniciar_sesion(request)
    return render(request, 'usuarios/iniciar_sesion.html')

def vista_bienvenido(request):
    """
    Vista que muestra la página de bienvenida.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Página de bienvenida
    """
    if request.method == 'POST':
        return render(request, 'usuarios/bienvenido.html')
    return render(request, 'usuarios/bienvenido.html')