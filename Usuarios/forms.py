from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado

class FormularioRegistro(UserCreationForm):
    email = forms.EmailField(help_text="Solo correos institucionales @utp.edu.pe")

    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email', 'carrera', 'password1', 'password2']
