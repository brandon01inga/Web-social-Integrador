from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .forms import FormularioRegistro
from .models import UsuarioPersonalizado
from django.http import HttpResponse




# Create your views here.
def registrar_usuario(request):
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inactivar hasta que confirme el correo
            user.save()
            dominio = get_current_site(request).domain
            asunto = "Activa tu cuenta"
            mensaje = render_to_string('Usuarios/activacion_email.html', {
                'user': user,
                'dominio': dominio,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(asunto, mensaje, None, [user.email])
            return render(request, 'Usuarios/correo_enviado.html')
    else:
        form = FormularioRegistro()
    return render(request, 'Usuarios/registro.html', {'form': form})



def activar_usuario(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UsuarioPersonalizado.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UsuarioPersonalizado.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'usuarios/activacion_exitosa.html')
    else:
        return render(request, 'usuarios/activacion_fallida.html')
    


def enviar_correo_prueba(request):
    send_mail(
        subject='Prueba de correo desde Django',
        message='Este es un correo de prueba enviado desde tu proyecto Django.',
        from_email=None,  # Usará DEFAULT_FROM_EMAIL
        recipient_list=['ssuarezvi5@ucvvirtual.edu.pe'],  # Cambia por el correo donde quieres recibirlo
        fail_silently=False,
    )
    return HttpResponse("Correo enviado correctamente.")
