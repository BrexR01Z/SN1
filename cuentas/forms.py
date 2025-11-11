from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Dueno, Cliente

class RegistroForm(UserCreationForm):
    TIPO_USUARIO = [("cliente", "Cliente - Quiero reservas"),
                    ("dueno", "Dueno - Quiero gestionar")]
    
    # luego usar required/blank

    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO,
        widget=forms.RadioSelect
    )

    telefono = forms.CharField(max_length=20)
    rut = forms.CharField(max_length=12)
    fecha_nacimiento = forms.DateField(widget=forms.SelectDateWidget)


