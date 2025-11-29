from django import forms
from .models import Reserva
from datetime import date

class CrearReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["fecha", "hora_inicio", "duracion_bloques", "comentario"]

        labels = {
            'fecha': 'Fecha de la Reserva',
            'hora_inicio': 'Hora de Inicio',
            'duracion_bloques': 'Duración (bloques de 30 min)',
            'comentario': 'Comentario (Opcional)',
        }
        
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'duracion_bloques': forms.NumberInput(attrs={'min': '1', 'max': '12', 'value': '1'}),
            'comentario': forms.TextInput(attrs={'placeholder': 'Comentario...', 'maxlength': '100'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha and fecha < date.today():
            raise forms.ValidationError("Ha seleccionado una fecha pasada")
        return fecha


class CambiarEstadoForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {'estado': forms.Select()}