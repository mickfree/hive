from django.db import models
class Inventario(models.Model):
    num_articulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    en_stock = models.IntegerField(default=0)
    codigo_barras = models.CharField(max_length=100, blank=True, default='')
    grupo_articulos = models.CharField(max_length=100, blank=True, default='')
    fabricante = models.CharField(max_length=100, blank=True, default='')
    unidad_medida = models.CharField(max_length=50, blank=True, default='')
    ultima_revalorizacion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimo_precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.descripcion