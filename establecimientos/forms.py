from django import forms
from .models import Establecimiento

class CrearEstablecimientoForm(forms.ModelForm):

    # luego cambiar a true  required/blank
    
    nombre = forms.CharField(max_length=50)   
    direccion = forms.CharField(max_length=100)
    telefono_contacto = forms.CharField(max_length=20)
    correo_contacto = forms.EmailField()
    estacionamiento_disponible = forms.NullBooleanField()
    camarines_disponible = forms.NullBooleanField()
    # editar a futuro para integrar mapa
    
    class Meta:
        model = Establecimiento
        fields = [
            'nombre', 
            'direccion', 
            'telefono_contacto', 
            'correo_contacto',
            'estacionamiento_disponible', 
            'camarines_disponible'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Cancha Central Sport',
                'maxlength': '50'
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Ej: Calle Principal 123, Talcahuano',
                'maxlength': '100'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'placeholder': 'Ej: +56 9 1234 5678',
                'type': 'tel',
                'maxlength': '20'
            }),
            'correo_contacto': forms.EmailInput(attrs={
                'placeholder': 'Ej: contacto@establecimiento.com'
            }),
            'estacionamiento_disponible': forms.CheckboxInput(),
            'camarines_disponible': forms.CheckboxInput(),
        }

