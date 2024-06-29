from django.db import models
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils import timezone

class Banco(models.Model):
    nombre_banco = models.CharField(max_length=100)
    numero_cuenta_banco = models.CharField(max_length=100)
    detalle_banco = models.CharField(max_length=100)
    monto_actual = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_fijacion = models.DateField(default=timezone.now)

    def __str__(self):
        return self.nombre_banco

    def actualizar_monto_actual(self):
        # Obtiene todos los extractos después de la fecha de fijación
        extractos = ExtractosBancarios.objects.filter(banco=self, fecha_operacion__gt=self.fecha_fijacion)
        
        # Calcula la suma de los importes
        total_importe = extractos.aggregate(total_importe=Sum('importe'))['total_importe'] or 0
        total_itf = extractos.aggregate(total_itf=Sum('itf'))['total_itf'] or 0
        
        # Actualiza el monto actual
        self.monto_actual = total_importe - total_itf
        self.save()


class ExtractosBancarios(models.Model):
    banco = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Banco')
    fecha_operacion = models.DateField(verbose_name='Fecha de Operación', null=True, blank=True)
    referencia = models.CharField(max_length=100, default='')
    importe = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    itf = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='ITF', null=True, blank=True)
    numero_movimiento = models.CharField(max_length=50, verbose_name='Número de Movimiento', default='')

    def __str__(self):
        return f'Movimiento: {self.numero_movimiento} - Referencia: {self.referencia}'   
    

class ExtractoBancarioManager(models.Manager):
    def por_mes(self, año, mes):
        return self.annotate(
            mes=TruncMonth('fecha_valor')
        ).filter(
            fecha_valor__year=año,
            fecha_valor__month=mes
        )
