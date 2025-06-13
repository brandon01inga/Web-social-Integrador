from django import forms
from .models import Publicacion

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'contenido', 'imagen']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'post-input',
                'rows': 1,
                'placeholder': '¿Qué estás pensando?',
                 'style': 'resize: none; border: none; background-color: #f5f5f5; border-radius: 8px; padding: 10px;'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título (opcional)',
                'style': 'display:none;'  # si no quieres mostrarlo
            }),
            'imagen': forms.ClearableFileInput(attrs={
                 'id': 'id_imagen',
                'style': 'display: none;'
            })
        }
