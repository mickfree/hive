from django.db import models


class Proceso(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Subproceso(models.Model):
    proceso = models.ManyToManyField(Proceso, related_name='subprocesos')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
