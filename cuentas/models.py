from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
# Create your models here.


# usuario abstracto, dueno y cliente herendan 

class Usuario (AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            return  hoy.year - self.fecha_nacimiento.year - (hoy.month, hoy.day) < (self.fecha_nacimiento.month,self.fecha_nacimiento.day)
        return 0
    
    def es_mayor(self):
        return self.edad() >= 18

class Dueno (models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_dueno")
    rut = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Usuario Dueño : {self.usuario.get_username()}"

class Cliente (models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_cliente")

    def __str__(self):
        return f"Usuario Cliente : {self.usuario.get_username()}"