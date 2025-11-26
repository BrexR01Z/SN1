from django.contrib import admin
from .models import Cancha,Establecimiento,HorarioEstablecimiento, Deporte
# Register your models here.
admin.site.register(Cancha)
admin.site.register(Establecimiento)
admin.site.register(HorarioEstablecimiento)
admin.site.register(Deporte)