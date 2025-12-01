from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Dueno, Cliente
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Usuario
from django.contrib.auth import get_user_model


class RegistroForm(UserCreationForm):
    TIPO_USUARIO = [("cliente", "Cliente - Quiero reservar"),
                    ("dueno", "Dueno - Quiero gestionar")]
    
    # luego cambiar a true  required/blank

    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO,
        widget=forms.RadioSelect
    )

    telefono = forms.CharField(max_length=20, required=True)
    rut = forms.CharField(max_length=12,required=False)
    # validacion rut
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={"type" : "date"}), required=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "first_name", "last_name", 
                  "fecha_nacimiento", "telefono", "password1", "password2"]
       

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

class InvitationForm(forms.Form): #Formulario para invitar usuarios (Poner el nombre de usuario)
    username = forms.CharField(label="Nombre de usuario a invitar", max_length=50)

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "telefono", "fecha_nacimiento"]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
        def clean_email(self):
            email = self.cleaned_data["email"]
            usuario_actual = self.instance  # El usuario que está editando

            # Si un usuario con este correo ya existe y no es el usuario actual, lanzar error
            if Usuario.objects.filter(email=email).exclude(id=usuario_actual.id).exists():
                raise forms.ValidationError("Este correo ya está en uso por otro usuario.")

            return email