from django.db import models
# from django.contrib.auth.models import User
#rom django.conf import settings
from cuentas.models import Usuario
from establecimientos.models import Cancha
from datetime import timedelta, datetime
# Create your models here.

class Reserva (models.Model):
    ESTADOS = [("PENDIENTE","Pendiente"),
               ("CONFIRMADA","Confirmada"),
               ("CANCELADA","Cancelada"),
               ("TERMINADA","Terminada"),
               ]

    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name="reservas")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reservas")
    fecha = models.DateField(blank=False, null=False)
    hora_inicio = models.TimeField(blank=False, null=False)
    # prueba 
    # hora_y_fecha = models.DateTimeField()
    duracion_bloques = models.PositiveIntegerField(default=1,blank=False, null=False )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")
    precio_total = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank = True)
    comentario = models.CharField(max_length=100, blank=True, null =True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


    def calcular_precio(self):
        self.precio_total = self.cancha.valor_por_bloque * self.duracion_bloques
        return self.precio_total
    
    def hora_fin (self):
        inicio = datetime.combine(self.fecha, self.hora_inicio)
        fin = inicio + timedelta(minutes=self.duracion_bloques*30)
        return fin.time()

    def save(self, *args, **kwargs):
        if not self.precio_total:
            self.calcular_precio()
        super().save(*args, **kwargs)