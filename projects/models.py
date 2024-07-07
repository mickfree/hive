from django.db import models
from datetime import date


class Contractor(models.Model):
    contractor_name = models.CharField(max_length=100, verbose_name="Nombre del contratista")
    address = models.CharField(max_length=150,verbose_name="Dirección")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    contractor_ruc = models.CharField(max_length=20,verbose_name="RUC del contratista") 
    email = models.EmailField(verbose_name="Correo Electronico")

    def __str__(self):
        return self.contractor_name

class Client(models.Model):
    client_name = models.CharField(max_length=100,verbose_name="Nombre del Cliente")
    email = models.EmailField(verbose_name="Correo")
    phone = models.CharField(max_length=20,verbose_name="Teléfono")

    def __str__(self):
        return self.client_name

class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE,verbose_name="Cliente")
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE,verbose_name="Contratistas")
    project_name = models.CharField(max_length=100,verbose_name="Nombre del Proyecto")
    sap_code = models.CharField(max_length=50,verbose_name="Código SAP")
    ov_name = models.CharField(max_length=100,verbose_name="Orden de venta")
    start_date = models.DateField()
    end_date = models.DateField()
    
    @property
    def days_since_start(self):
        return (date.today() - self.start_date).days
    
    @property
    def total_budget(self):
        total = sum(budget.valor_total for budget in self.budgets.all())
        return total

    def __str__(self):
        return self.project_name

