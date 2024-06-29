from django.db import models

# estos no sirven la verdad
class OrdenCompra(models.Model):
    descripcion = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    igv = models.DecimalField(max_digits=5, decimal_places=2)
    detraccion = models.DecimalField(max_digits=5, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(max_length=50)
    clase = models.CharField(max_length=50)
    banco = models.CharField(max_length=50)
    numero_bancario = models.CharField(max_length=20)
    cuotas = models.IntegerField()

    def __str__(self):
        return self.descripcion


class OrdenPago(models.Model):
    numero_operacion = models.CharField(max_length=50)
    orden_compra = models.CharField(max_length=50)
    proyecto = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    ruc_dni = models.CharField(max_length=20)
    proveedor = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=50)
    banco = models.CharField(max_length=50)
    monto_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante_pdf = models.FileField(upload_to="comprobantes/", blank=True, null=True)

    def __str__(self):
        return f"{self.numero_operacion} - {self.observaciones}"
#estos no sriven la verdad
    

# desde aqui si servirian las cosas supongo y recuerda que lamentablemente mezcle ordenes de venta con com pras desde la misma app por eso aveces esta un poco entreverado
    