from django.db import models
from datetime import date

class Contractor(models.Model):
    contractor_name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    contractor_ruc = models.CharField(max_length=20) 
    email = models.EmailField()

    def __str__(self):
        return self.contractor_name
    
class Client(models.Model):
    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.client_name

class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=100)
    sap_code = models.CharField(max_length=50)
    ov_name = models.CharField(max_length=100)
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

