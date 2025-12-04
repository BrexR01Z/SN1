from django import forms
from django.forms import inlineformset_factory
from .models import Establecimiento, Cancha, HorarioEstablecimiento
from django.contrib import messages
#from geopy.geocoders import Nominatim
from django.core.exceptions import ValidationError

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


class CrearCanchaForm(forms.ModelForm):

    class Meta:
        model = Cancha
        fields = [
            'nombre',
            'deporte',
            'superficie',
            'iluminacion',
            'interior',
            'valor_por_bloque'
        ]
        
        labels = {
            'nombre': 'Nombre de la Cancha',
            'deporte': 'Deporte',
            'superficie': 'Tipo de Superficie',
            'iluminacion': 'Tipo de Iluminación',
            'interior': 'Cancha de interior',
            'valor_por_bloque': 'Valor por Bloque',
        }
        
        help_texts = {
            'valor_por_bloque': 'Precio para una bloque de 30 minutos',
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'maxlength': '25'
            }),
            'deporte': forms.Select(attrs={
                'class': 'form-select'
            }),
            'superficie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'iluminacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'interior': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'valor_por_bloque': forms.NumberInput(attrs={
                'placeholder': '$5000',
                'min': '0',
                'step': '1000'
            }),
        }

class HorarioEstablecimientoForm(forms.ModelForm):

    class Meta:

        model = HorarioEstablecimiento
        fields = ["dia", "hora_apertura", "hora_cierre"]

        labels = {
            "dia" : "Día",
            "hora_apertura" : "Apertura",
            "hora_cierre" : "Cierre",
        }

        widgets = {
            "dia" : forms.Select(),
            "hora_apertura" : forms.TimeInput(attrs={"type" : "time"}),
            "hora_cierre" : forms.TimeInput(attrs={"type" : "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_apertura = cleaned_data.get("hora_apertura")
        hora_cierre = cleaned_data.get("hora_cierre")

        if hora_apertura and hora_cierre:
            if hora_apertura>= cleaned_data.get("hora_cierre"):
                
                raise forms.ValidationError("La hora de apertura debe ser antes que la hora de cierre ")

        return cleaned_data
    
HorarioFormSet = inlineformset_factory(
    Establecimiento,
    HorarioEstablecimiento,
    form=HorarioEstablecimientoForm,
    extra=7,  
    can_delete=True
)
