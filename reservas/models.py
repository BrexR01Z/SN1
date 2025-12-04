from django.db import models
# from django.contrib.auth.models import User
#rom django.conf import settings
from cuentas.models import Usuario
from establecimientos.models import Cancha
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
# Create your models here.

class Reserva (models.Model):
    ESTADOS = [("PENDIENTE","Pendiente"),
               ("CONFIRMADA","Confirmada"),
               ("CANCELADA","Cancelada"),
               ("TERMINADA","Terminada"),
               ("EN_CURSO","En Curso"),
               ]
    # al borrar cancha, que quede cancelada
    cancha = models.ForeignKey(Cancha, on_delete=models.SET_NULL, related_name="reservas",null=True,default="---")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reservas")
    #correo_usuario = models.ForeignKey(Usuario.email, on_delete=models.CASCADE, related_name="reservas")
    #telefono_usuario = models.ForeignKey(Usuario.telefono, on_delete=models.CASCADE, related_name="reservas")
    fecha = models.DateField(default=timezone.now,blank=False, null=False)
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
    
    def actualizar_estado(self):
        # actualizar estado automaticamente
        if self.estado in ['CANCELADA', 'TERMINADA']:
            return

        ahora = timezone.now()
        fecha_hora_inicio = datetime.combine(self.fecha, self.hora_inicio)
        fecha_hora_fin = datetime.combine(self.fecha, self.hora_fin())

        fecha_hora_inicio_tz = timezone.make_aware(fecha_hora_inicio) if not timezone.is_aware(fecha_hora_inicio) else fecha_hora_inicio
        fecha_hora_fin_tz = timezone.make_aware(fecha_hora_fin) if not timezone.is_aware(fecha_hora_fin) else fecha_hora_fin

        if ahora >= fecha_hora_fin_tz:
            self.estado = 'TERMINADA'
        elif ahora >= fecha_hora_inicio_tz:
            self.estado = 'EN_CURSO'

    def puede_ser_editada(self):
        # las reservas terminadas y canceladas no pueden ser editadas
        self.actualizar_estado()
        return self.estado not in ['TERMINADA', 'CANCELADA']

    def puede_ser_cancelada(self):
        # reservas canceladas y terminadas no pueden cancelarse
        self.actualizar_estado()
        return self.estado not in ['TERMINADA', 'CANCELADA']

    def save(self, *args, **kwargs):
        if not self.precio_total:
            self.calcular_precio()
        super().save(*args, **kwargs)

def actualizar_reservas_por_cambio_horario(establecimiento):
    # al editar horarios de un establecimiento, sus reservas vuelven a estar en "pendiente"
    reservas_confirmadas = Reserva.objects.filter(
        cancha__establecimiento=establecimiento,
        estado='CONFIRMADA'
    )
    
    reservas_confirmadas.update(estado='PENDIENTE')
    return reservas_confirmadas.count()


def actualizar_estados_reservas_activas():
    # automaticamente actualizar horarios dependiendo de la hora actual
    reservas_activas = Reserva.objects.exclude(estado__in=['CANCELADA', 'TERMINADA'])
    
    ahora = timezone.now()
    actualizadas = 0
    
    for reserva in reservas_activas:
        fecha_hora_inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        fecha_hora_fin = datetime.combine(reserva.fecha, reserva.hora_fin())
        
        fecha_hora_inicio_tz = timezone.make_aware(fecha_hora_inicio) if not timezone.is_aware(fecha_hora_inicio) else fecha_hora_inicio
        fecha_hora_fin_tz = timezone.make_aware(fecha_hora_fin) if not timezone.is_aware(fecha_hora_fin) else fecha_hora_fin
        
        estado_anterior = reserva.estado
        
        if ahora >= fecha_hora_fin_tz:
            reserva.estado = 'TERMINADA'
        elif ahora >= fecha_hora_inicio_tz:
            reserva.estado = 'EN_CURSO'
        
        if estado_anterior != reserva.estado:
            reserva.save(update_fields=['estado'])
            actualizadas += 1
    
    return actualizadas

@receiver(pre_delete, sender=Cancha)
def cancelar_reservas_al_eliminar_cancha(sender, instance, **kwargs):
    print("1")
    reservas = Reserva.objects.filter(cancha=instance)
    print("2")
    reservas.update(estado='CANCELADA')
    print("3")