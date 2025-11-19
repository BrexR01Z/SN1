from django.db import models

from cuentas.models import Dueno


# Create your models here.

"""
class Deporte(models.Model):
    DEPORTES = [
        ("FUTBOL", "Futbol"),
        ("BASQUETBALL","Basquetball"),
        ("VOLEYBALL","Voleyball"),
        ("TENIS","Tenis"),
        ("RUGBY","Rugby"),
        ("HANDBALL","Handball"),
        ("BOWLING","Bowling"),
        ("SQUASH","Squash"),
        ("PADEL","Padel"),
        ("OTRO","Otro"),
        ("---","---"),        
    ]
    deporte = models.CharField(max_length=20, choices=DEPORTES)

    def __str__(self):
        return f"Nombre deporte = {self.deporte}"

"""
    
class Establecimiento (models.Model):
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE, related_name="establecimientos")
    nombre = models.CharField(max_length=50)
    # editar a futuro para integrar mapa
    direccion = models.CharField(max_length=100)
    telefono_contacto = models.CharField(max_length=20)
    correo_contacto = models.EmailField()
    estacionamiento_disponible = models.BooleanField(default=False)
    camarines_disponible = models.BooleanField(default=False)

    def __str__(self):
        return f"Nombre establecimietno = {self.nombre} , Dueno = {self.dueno}"


class HorarioEstablecimiento(models.Model):
    DIAS_SEMANA = [
        ("LUNES","Lunes"),
        ("MARTES","Martes"),
        ("MIERCOLES","Miercoles"),
        ("JUEVES","Jueves"),
        ("VIERNES","Viernes"),
        ("SABADO","Sabado"),
        ("DOMINGO","Domingo")
    ]
    
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="horarios")
    dia = models.CharField(max_length=20, choices=DIAS_SEMANA, unique=True)
    # hacer validacion para q hora_apertura<hora_cierre
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()

    def __str__(self):
        return f"Horario {self.establecimiento}, dia {self.dia}, desde {self.hora_apertura} hasta {self.hora_cierre}"
    
class Cancha (models.Model):
    TIPOS_SUPERFICIES = [
        ("PASTO_NATURAL", "Pasto Natural"),
        ("PASTO_SINTETICO","Pasto Sintético"),
        ("CEMENTO","Cemento"),
        ("ARCILLA","Arcilla"),
        ("MADERA","Madera"),
        ("CAUCHO","Caucho"),
        ("VINILO","Vinilo"),
        ]
    
    DEPORTES = [
        ("FUTBOL", "Futbol"),
        ("BASQUETBALL","Basquetball"),
        ("VOLEYBALL","Voleyball"),
        ("TENIS","Tenis"),
        ("RUGBY","Rugby"),
        ("HANDBALL","Handball"),
        ("BOWLING","Bowling"),
        ("SQUASH","Squash"),
        ("PADEL","Padel"),
        ("OTRO","Otro"),
        ("---","---"),        
    ]
    
    
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="canchas")
    deporte = models.CharField(max_length=20, choices=DEPORTES, default="---")
    #deporte = models.ManyToManyField(Deporte, related_name="canchas")
    nombre = models.CharField(max_length=25, unique=True)
    superficie = models.CharField(max_length=25, choices=TIPOS_SUPERFICIES)
    iluminacion = models.CharField(max_length=20)
    # true = interior , false = exterior
    interior = models.BooleanField()
    # validar 
    valor_por_bloque = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Cancha = {self.nombre}, Deporte = {self.deporte}, Establecimiento {self.establecimiento} "

    


# integrar imagenes para canchas
