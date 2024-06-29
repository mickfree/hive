from django.db import models

class BaseInventario(models.Model):
    num_articulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    en_stock = models.IntegerField(default=0)
    codigo_barras = models.CharField(max_length=100, blank=True, default='')
    grupo_articulos = models.CharField(max_length=100, default='MISC')
    fabricante = models.CharField(max_length=100, blank=True, default='')
    unidad_medida = models.CharField(max_length=50, blank=True, default='')
    precio_unitario_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimo_precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.descripcion

class Equipos(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='EQUIPOS')

class EPPS(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='EPPS')

class Transporte(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='TRANSPORTE')

class Materiales(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='MATERIALES')

class Consumibles(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='CONSUMIBLES')

class Alimentos(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='ALIMENTOS')

class ManoDeObra(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='MANODEOBRA')

class Herramientas(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='HERRAMIENTAS')

class Misc(BaseInventario):
    grupo_articulos = models.CharField(max_length=100, default='MISC')
