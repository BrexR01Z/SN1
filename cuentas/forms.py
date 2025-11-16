from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Dueno, Cliente
from datetime import date
from dateutil.relativedelta import relativedelta


class RegistroForm(UserCreationForm):
    TIPO_USUARIO = [("cliente", "Cliente - Quiero reservar"),
                    ("dueno", "Dueno - Quiero gestionar")]
    
    # luego usar required/blank

    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO,
        widget=forms.RadioSelect
    )

    telefono = forms.CharField(max_length=20, required=False)
    rut = forms.CharField(max_length=12, required=False)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={"type" : "date"}), required=False)

    class Meta:
        model = Usuario
        fields = ["username", "email", "first_name", "last_name", 
                  "fecha_nacimiento", "telefono", "password1", "password2"]
        widgets = {"fecha_nacimiento" : forms.DateInput(attrs={"type" : "date"})}

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        edad_minima = date.today() - relativedelta(years=18)

        if fecha > edad_minima:
            raise forms.ValidationError ("La edad minima es 18 años")
        return fecha
 
    def clean(self):
        data = super().clean()
        tipo_usuario = data.get("tipo_usuario")
        rut = data.get("rut")

        if tipo_usuario == "dueno" and not rut:
            raise forms.ValidationError ({
                "rut" : "Los usuarios tipo dueño deben ingresar un rut"
            })
        return data

    