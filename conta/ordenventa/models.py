from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.forms import ValidationError
from decimal import Decimal, InvalidOperation
from reportes.models import Proveedor
from django.db import models
from django.db.models import Sum
from decimal import Decimal

# Definición de los modelos
class OrdenVenta(models.Model):
    CODIGO_EMPRESA = [
        ('JP', 'JP'),
        ('AWL', 'AWL'),
    ]
    
    codigosap = models.CharField(max_length=50)
    proyecto = models.CharField(max_length=255)
    observacion = models.CharField(max_length=255)
    fecha = models.DateField()
    empresa = models.CharField(max_length=3, choices=CODIGO_EMPRESA, default='JP')

    def __str__(self):
        return f"{self.codigosap} - {self.proyecto} - {self.observacion}"

class ItemOrdenVenta(models.Model):
    ordenventa = models.ForeignKey(
        OrdenVenta, 
        related_name="items", 
        on_delete=models.CASCADE
    )
    nro_articulo = models.CharField(max_length=50, null=True, default="")
    desc_articulo = models.CharField(max_length=50, null=True, default="")
    cantidad = models.IntegerField(null=True, default=0)
    cantidad_pedida = models.IntegerField(default=0)
    cantidad_restante = models.IntegerField(null=True, default=0)
    precio_bruto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bruto_restante = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('0.00'))
    enviado = models.BooleanField(default=False)
    solicitar_nueva_orden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nro_articulo} - {self.ordenventa} - {self.desc_articulo}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.total_bruto is not None:
            self.update_bruto_restante()

    def update_bruto_restante(self):
        total_pagado = self.ordenes_de_compra.aggregate(Sum('precio_total'))['precio_total__sum'] or Decimal('0.00')
        new_bruto_restante = Decimal(self.total_bruto) - Decimal(total_pagado)
        
        if self.bruto_restante != new_bruto_restante:
            self.bruto_restante = new_bruto_restante
            # Guardar solo `bruto_restante` sin llamar a `save` de nuevo
            ItemOrdenVenta.objects.filter(pk=self.pk).update(bruto_restante=new_bruto_restante)

class OrdenDeCompra(models.Model):
    item_orden_venta = models.ForeignKey(
        ItemOrdenVenta, 
        on_delete=models.CASCADE, 
        related_name="ordenes_de_compra"
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
    desc_articulo = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    codigo_sap = models.CharField(max_length=50)
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igv = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Porcentaje
    detraccion = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    precio_total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=0
    )
    cuotas = models.IntegerField(default=0)
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    fecha_pagada = models.DateField(null=True, blank=True, verbose_name="Fecha Pagada")
    monto_detraccion = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    
    # Aqui sera la orden de pago
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Añade el campo comprobante_pago
    comprobante_pago = models.FileField(
        upload_to="comprobantes_pago/",  # Directorio donde se guardarán los archivos
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"])
        ],  
        null=True,
        blank=True,
        verbose_name="Comprobante de Pago",
    )
    numero_movimiento_bancario = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default='',  # Establece el valor predeterminado como cadena vacía
        verbose_name="Número de Movimiento Bancario"
    )
    banco_relacionado = models.ForeignKey(
        'extractos.Banco',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Banco Relacionado"
    )
    restante_rendir = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Restante por Rendir")


    def save(self, *args, **kwargs):
        cantidad_decimal = Decimal(self.cantidad)
        precio_actual_decimal = Decimal(self.precio_actual)
        igv_decimal = Decimal(self.igv) / Decimal(100)
        detraccion_decimal = Decimal(self.detraccion) / Decimal(100)

        # Calcular precio_total
        precio_total_calculado = cantidad_decimal * precio_actual_decimal * (Decimal(1) + igv_decimal) - (cantidad_decimal * precio_actual_decimal * detraccion_decimal)

        # Verifica si el precio_total ha cambiado
        if self.precio_total != precio_total_calculado:
            self.precio_total = precio_total_calculado
            self.monto_pagado = self.precio_total

        try:
            # Asegurarse de que precio_total y monto_pagado sean Decimales
            precio_total_decimal = Decimal(self.precio_total)
            monto_pagado_decimal = Decimal(self.monto_pagado)
        except InvalidOperation:
            return

        # Calcular restante_rendir
        self.restante_rendir = precio_total_decimal - monto_pagado_decimal
        self.monto_detraccion = cantidad_decimal * precio_actual_decimal * detraccion_decimal

        super().save(*args, **kwargs)# Actualizar el ItemOrdenVenta asociado


    def __str__(self):
        return f"{self.desc_articulo} - {self.cantidad} - {self.codigo_sap}"

@receiver(post_save, sender=ItemOrdenVenta)
def create_or_update_orden_de_compra(sender, instance, created, **kwargs):
    if instance.solicitar_nueva_orden:
        OrdenDeCompra.objects.create(
            item_orden_venta=instance,
            cantidad=instance.cantidad_pedida,
            desc_articulo=instance.desc_articulo,
            precio_actual=instance.precio_bruto,
        )
        instance.solicitar_nueva_orden = False
        instance.save(update_fields=['solicitar_nueva_orden'])

@receiver(post_save, sender=OrdenDeCompra)
def update_item_orden_venta(sender, instance, **kwargs):
    item_orden_venta = instance.item_orden_venta
    item_orden_venta.update_bruto_restante()

### mmodelo orden de cobranza
# este talvez no sirva veremos
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

class FacturaElectronica(models.Model):
    TIPO_COBRO_CHOICES = [
        ('factoring', 'Factoring'),
        ('directo', 'Directo'),
    ]
    orden_venta = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE, verbose_name="Orden de Venta")
    serie_correlativo = models.CharField(max_length=100, verbose_name="Serie y Correlativo", null=True, blank=True)
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión", null=True, blank=True)
    cliente = models.CharField(max_length=255, verbose_name="Cliente", null=True, blank=True)
    ruc_cliente = models.CharField(max_length=11, verbose_name="RUC Cliente", null=True, blank=True)
    tipo_moneda = models.CharField(max_length=20, verbose_name="Tipo de Moneda", null=True, blank=True)
    descripcion = models.TextField(verbose_name="Descripción", null=True, blank=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Total", null=True, blank=True)
    detraccion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Detracción", null=True, blank=True)
    monto_neto_cobrar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Neto a Cobrar", null=True, blank=True)
    total_cuotas = models.IntegerField(verbose_name="Total de Cuotas", null=True, blank=True)
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento", null=True, blank=True)
    tipo_cobro = models.CharField(max_length=20, choices=TIPO_COBRO_CHOICES, verbose_name="Tipo de Cobro", null=True, blank=True)
    desc_factoring = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Descuento Factoring (%)", null=True, blank=True)
    extracto_banco = models.ForeignKey('extractos.ExtractosBancarios', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Extracto Bancario")
    factura_pagado = models.BooleanField(default=False, verbose_name="Factura Pagada")

    def save(self, *args, **kwargs):
        # Si existe un descuento de factoring, ajusta el monto_neto_cobrar
        if self.desc_factoring and self.monto_neto_cobrar:
            descuento = (self.desc_factoring / 100) * self.monto_neto_cobrar
            self.monto_neto_cobrar -= descuento

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.serie_correlativo} - {self.cliente}"

