from django import forms
from .models import Reserva
from datetime import date
from django.core.exceptions import ValidationError
from datetime import datetime,timedelta
from establecimientos.models import HorarioEstablecimiento
from establecimientos.models import Cancha


class CrearReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora_inicio', 'duracion_bloques', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, cancha=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancha = cancha

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha < datetime.now().date():
            raise forms.ValidationError('La fecha no puede ser en el pasado')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        duracion_bloques = cleaned_data.get('duracion_bloques')

        if not (fecha and hora_inicio and duracion_bloques and self.cancha):
            return cleaned_data

        dias_semana = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        dia_semana = dias_semana[fecha.weekday()]

        horario = HorarioEstablecimiento.objects.filter(
            establecimiento=self.cancha.establecimiento,
            dia=dia_semana
        ).first()

        if not horario:
            raise forms.ValidationError(f"El establecimiento está cerrado el {dia_semana}")

        if hora_inicio < horario.hora_apertura or hora_inicio >= horario.hora_cierre:
            raise forms.ValidationError(
                f"La hora debe estar entre {horario.hora_apertura.strftime('%H:%M')} "
                f"y {horario.hora_cierre.strftime('%H:%M')}"
            )

        minutos_disponibles = int(
            (horario.hora_cierre.hour * 60 + horario.hora_cierre.minute) - 
            (hora_inicio.hour * 60 + hora_inicio.minute)
        )
        max_bloques = minutos_disponibles // 30

        if max_bloques <= 0:
            raise forms.ValidationError("La reserva debe terminar antes del cierre del establecimiento")

        if duracion_bloques > max_bloques:
            raise forms.ValidationError(f"La reserva no puede exceder {max_bloques} bloques")

        return cleaned_data


class CambiarEstadoForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {'estado': forms.Select()}