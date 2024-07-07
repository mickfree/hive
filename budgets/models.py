from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from projects.models import Project

class Budget(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets')
    dias = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.project.nombre} - {self.dias} días'

    def calcular_valor_total(self):
        total = 0
        for item in self.items.all():
            total += item.precio_total_diario * self.dias
        self.valor_total = total
        self.save()

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    inventario = GenericForeignKey('content_type', 'object_id')
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.inventario.descripcion} - {self.cantidad}'

    @property
    def precio_total_diario(self):
        return self.cantidad * self.inventario.precio_unitario_diario


