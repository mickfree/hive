from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from datetime import date

from resources.models import Resource

class NewTarea(models.Model):
    verbo = models.CharField(max_length=100)
    objeto = models.CharField(max_length=100)
    orden_venta = models.CharField(max_length=200, db_index=True)  # Añadir índice
    gestion_tipo = models.CharField(
        max_length=100, 
        choices=[
            ('Inicio', 'Gestion Inicio'),
            ('Requerimientos', 'Gestion Requerimientos'),
            ('Proyecto', 'Gestion Proyecto'),
            ('Interesados', 'Gestion Interesados'),
            ('Control', 'Gestion Control'),
            ('Desarrollo', 'Gestion Desarrollo'),
        ],
        blank=True, 
        null=True,
        default='Inicio',
        db_index=True  # Añadir índice
    )
    cliente = models.CharField(
        max_length=200,
        blank=True, 
        null=True
    )
    unidad_de_medida = models.CharField(max_length=50, default='minutos', blank=True)
    tiempo_tarea = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    resources = models.ManyToManyField(Resource, related_name='tasks')

    class Meta:
        indexes = [
            models.Index(fields=['usuario', 'orden_venta']),
        ]

    def __str__(self):
        return f"{self.verbo} {self.objeto} {self.tiempo_tarea}"

class NewTarjeta(models.Model):
    tareas = models.ManyToManyField('NewTarea', through='NewOrden', related_name='tarjetas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)
    total_minutos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_minutos_completados = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_minutos_incidentes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    porcentaje_completado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    porcentaje_incidentes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valorizacion = models.CharField(max_length=2, default='D') 

    def __str__(self):
        return f"Tarjeta de {self.usuario.username} - {self.fecha}"

    def get_ordered_tareas(self):
        return self.tareas.order_by('neworden__order')

class NewOrden(models.Model):
    ESTADO_CHOICES = [
        ('completa', 'Completa'),
        ('incompleta', 'Incompleta'),
        ('reprogramada', 'Reprogramada'),
    ]

    tarjeta = models.ForeignKey(NewTarjeta, on_delete=models.CASCADE)
    tarea = models.ForeignKey(NewTarea, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='completa')

    class Meta:
        ordering = ['order']
        unique_together = [('tarjeta', 'tarea')]

    def __str__(self):
        return f"{self.tarjeta} - {self.tarea} - {self.get_estado_display()}"

    def save(self, *args, **kwargs):
        if self.order is None:  # Si no tiene orden
            last_order = NewOrden.objects.filter(tarjeta=self.tarjeta).aggregate(models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)


class Incident(models.Model):
    tarjeta = models.ForeignKey('NewTarjeta', related_name='incidents', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    duracion = models.IntegerField()

    def __str__(self):
        return self.descripcion