from django.db import models
from django.contrib.auth.models import User

class SimpleTask(models.Model):
    descripcion = models.CharField(max_length=255)
    priority = models.CharField(max_length=50, default='')

    def __str__(self):
        return f"{self.descripcion} ({self.priority})"

class Backlog(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    simple_tasks = models.ManyToManyField(SimpleTask)
    date = models.DateField()

    def __str__(self):
        return f"{self.date} - {self.usuario.username}"
