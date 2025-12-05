from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.conf import settings

# Create your models here.


# usuario abstracto, dueno y cliente herendan 

class Usuario (AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    telefono = models.CharField(max_length=20, blank=False, null=False)
    fecha_nacimiento = models.DateField(default=timezone.now,blank=False, null=False)


    # cambiar validaciones a respectivo form
    def edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - self.fecha_nacimiento.year
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad -= 1
            return edad
        return 0

    
    def es_mayor(self):
        return self.edad() >= 18
    
    def clean(self):
        super().clean()
        if self.fecha_nacimiento:
            edad_minima = date.today() - relativedelta(years=18)
            if self.fecha_nacimiento > edad_minima:
                raise ValidationError ({ "fecha_nacimiento" : "Debes ser mayor de 18 para registrarte"})

class Dueno (models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_dueno", unique=True)
    # validar rut
    rut = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Usuario Dueño : {self.usuario.get_username()}"

class Cliente (models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_cliente", unique=True)

    def __str__(self):
        return f"Usuario Cliente : {self.usuario.get_username()}"
    
# Modelo para gestionar invitaciones entre usuarios
class Invitation(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    reserva = models.ForeignKey("reservas.Reserva", on_delete=models.CASCADE, null=True, blank=True, related_name='invitaciones')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.sender} -> {self.receiver}"