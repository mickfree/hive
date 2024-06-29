from django.db import models
from django.db.models import Sum
from decimal import Decimal


# Create your models here.

class Proveedor(models.Model):
    SOLES = 0
    DOLARES = 1
    MONEDA_CHOICES = (
        (SOLES, 'Soles'),
        (DOLARES, 'Dolares'),
    )

    ruc_dni = models.CharField(max_length=20, unique=True, verbose_name="RUC/DNI", null=True, blank=True, default='')
    nombre_proveedor = models.CharField(max_length=100, verbose_name="Nombre del Proveedor", null=True, blank=True, default='')
    nombre_banco = models.CharField(max_length=100, verbose_name="Nombre del Banco", null=True, blank=True, default='')
    nro_cuenta = models.CharField(max_length=50, verbose_name="Número de Cuenta", null=True, blank=True, default='')
    moneda = models.IntegerField(choices=MONEDA_CHOICES, default=SOLES, verbose_name="Moneda", null=True, blank=True)
    nro_cuenta_interbancario = models.CharField(max_length=50, verbose_name="Número de Cuenta Interbancario", null=True, blank=True, default='')

    def __str__(self):
        return f"{self.nombre_proveedor} - {self.ruc_dni}"

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"