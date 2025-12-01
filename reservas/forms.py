from django import forms
from .models import Reserva
from datetime import date
from django.core.exceptions import ValidationError
from datetime import datetime
from establecimientos.models import HorarioEstablecimiento
from establecimientos.models import Cancha

"""
class CrearReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora_inicio', 'duracion_bloques', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        
        if not fecha or not hora_inicio:
            return cleaned_data
        
        if fecha < datetime.now().date():
            raise ValidationError('La fecha no puede ser en el pasado')
        
        dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        dia_semana = dias_semana[fecha.weekday()]
        
        horario = HorarioEstablecimiento.objects.filter(
            establecimiento=self.instance.cancha.establecimiento,
            dia=dia_semana
        ).first()
        
        if not horario:
            raise ValidationError(f'No hay horario disponible para {dia_semana}')
        
        if hora_inicio < horario.hora_apertura or hora_inicio >= horario.hora_cierre:
            raise ValidationError(
                f'La hora debe estar entre {horario.hora_apertura.strftime("%H:%M")} '
                f'y {horario.hora_cierre.strftime("%H:%M")}'
            )
        
        return cleaned_data
"""

class CrearReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora_inicio', 'duracion_bloques', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha < datetime.now().date():
            raise forms.ValidationError('La fecha no puede ser en el pasado')
        return fecha


class CambiarEstadoForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {'estado': forms.Select()}