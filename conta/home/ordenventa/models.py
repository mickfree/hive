from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

from reportes.models import Proveedor


# Definición de los modelos
class OrdenVenta(models.Model):
    codigosap = models.CharField(max_length=50)
    proyecto = models.CharField(max_length=255)
    direccion_proyecto = models.CharField(max_length=255)
    observacion = models.CharField(max_length=255)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.codigosap} - {self.proyecto} - {self.observacion}"


class ItemOrdenVenta(models.Model):
    ordenventa = models.ForeignKey(
        OrdenVenta, related_name="items", on_delete=models.CASCADE
    )
    nro_articulo = models.CharField(max_length=50, null=True, default="")
    desc_articulo = models.CharField(max_length=50, null=True, default="")
    cantidad = models.IntegerField(null=True, default=0)
    precio_bruto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nro_articulo} - {self.ordenventa} - {self.desc_articulo}"


class OrdenDeCompra(models.Model):
    item_orden_venta = models.OneToOneField(
        ItemOrdenVenta, on_delete=models.CASCADE, related_name="orden_de_compra"
    )
    clase = models.CharField(max_length=50, default="")
    tipo_pago = models.CharField(max_length=50, default="")
    # Establece una relación ForeignKey con Proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes_de_compra",
        verbose_name="Proveedor",
    )
    # Elimina los campos proveedor, banco y numero_bancario, ya que ahora usarás la relación con Proveedor
    desc_articulo = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    codigo_sap = models.CharField(max_length=50)
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igv = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Porcentaje
    detraccion = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # Porcentaje
    precio_total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=0
    )
    cuotas = models.IntegerField(default=0)
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    fecha_pagada = models.DateField(null=True, blank=True, verbose_name="Fecha Pagada")
    monto_detraccion = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    # Añade el campo comprobante_pago
    comprobante_pago = models.FileField(
        upload_to="comprobantes_pago/",  # Directorio donde se guardarán los archivos
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"])
        ],  # Asegura que solo se puedan subir archivos PDF
        null=True,
        blank=True,
        verbose_name="Comprobante de Pago",
    )

    def save(self, *args, **kwargs):
        # Convertir todos los valores a Decimal antes de realizar cálculos
        cantidad_decimal = Decimal(self.cantidad)
        precio_actual_decimal = Decimal(self.precio_actual)
        igv_decimal = Decimal(self.igv) / Decimal(100)
        detraccion_decimal = Decimal(self.detraccion) / Decimal(100)

        self.precio_total = cantidad_decimal * precio_actual_decimal * (Decimal(1) + igv_decimal) - (cantidad_decimal * precio_actual_decimal * detraccion_decimal)
        self.monto_detraccion = cantidad_decimal * precio_actual_decimal * detraccion_decimal

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.desc_articulo} - {self.cantidad} - {self.codigo_sap}"


# Señal para crear o actualizar OrdenDeCompra cuando se guarda un ItemOrdenVenta
@receiver(post_save, sender=ItemOrdenVenta)
def create_or_update_orden_de_compra(sender, instance, created, **kwargs):
    OrdenDeCompra.objects.update_or_create(
        item_orden_venta=instance,
        defaults={
            "desc_articulo": instance.desc_articulo,
            "cantidad": instance.cantidad,
            "codigo_sap": instance.ordenventa.codigosap,
            "precio_actual": 0,  # Asumiendo un valor por defecto
            "igv": 0,  # Valor por defecto, actualizable posteriormente
            "detraccion": 0,  # Valor por defecto, actualizable posteriormente
            # No es necesario definir precio_total aquí ya que se calcula en el método save de OrdenDeCompra
        },
    )



### mmodelo orden de cobranza

class CobrosOrdenVenta(models.Model):
    TIPO_MONEDA_CHOICES = (
        ('soles', 'Soles'),
        ('dolares', 'Dólares'),
    )
    TIPO_COBRO_CHOICES = (
        ('factoring', 'Factoring'),
        ('directo', 'Directo'),
    )

    orden_venta = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE, related_name='cobros')
    serie_correlativo = models.CharField(max_length=255)
    fecha_emision_factura = models.DateField()
    cliente_factura = models.CharField(max_length=255)
    ruc_factura = models.CharField(max_length=11)
    tipo_moneda = models.CharField(max_length=7, choices=TIPO_MONEDA_CHOICES)
    descripcion_factura = models.TextField()
    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    detraccion = models.DecimalField(max_digits=5, decimal_places=2, help_text='Porcentaje de la detracción')
    neto_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    tipo_cobro_factura = models.CharField(max_length=9, choices=TIPO_COBRO_CHOICES)
    dscto_factoring = models.DecimalField(max_digits=5, decimal_places=2, help_text='Porcentaje del descuento por factoring', default=0)
    extracto_banco = models.ForeignKey('extractos.ExtractosBancarios', on_delete=models.SET_NULL, null=True, blank=True)


    def save(self, *args, **kwargs):
        self.neto_total = self.importe_total - (self.importe_total * self.detraccion / 100)
        if self.tipo_cobro_factura == 'factoring':
            self.neto_total -= self.neto_total * self.dscto_factoring / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.serie_correlativo} - {self.cliente_factura}"


## nevo model de factura
class FacturaElectronica(models.Model):
    TIPO_COBRO_CHOICES = [
        ('factoring', 'Factoring'),
        ('directo', 'Directo'),
    ]
    orden_venta = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE, verbose_name="Orden de Venta")
    serie_correlativo = models.CharField(max_length=100, verbose_name="Serie y Correlativo")
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    cliente = models.CharField(max_length=255, verbose_name="Cliente")
    ruc_cliente = models.CharField(max_length=11, verbose_name="RUC Cliente")
    tipo_moneda = models.CharField(max_length=20, verbose_name="Tipo de Moneda")
    descripcion = models.TextField(verbose_name="Descripción")
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Total")
    detraccion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Detracción")
    monto_neto_cobrar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Neto a Cobrar")
    total_cuotas = models.IntegerField(verbose_name="Total de Cuotas")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    tipo_cobro = models.CharField(max_length=20, choices=TIPO_COBRO_CHOICES, verbose_name="Tipo de Cobro", null=True, blank=True)
    desc_factoring = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Descuento Factoring (%)", null=True, blank=True)
    extracto_banco = models.ForeignKey('extractos.ExtractosBancarios', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Extracto Bancario")

    def save(self, *args, **kwargs):
        # Si existe un descuento de factoring, ajusta el monto_neto_cobrar
        if self.desc_factoring and self.monto_neto_cobrar:
            descuento = (self.desc_factoring / 100) * self.monto_neto_cobrar
            self.monto_neto_cobrar -= descuento

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.serie_correlativo} - {self.cliente}"
