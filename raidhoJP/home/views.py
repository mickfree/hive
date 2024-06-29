from django.shortcuts import render
from django.shortcuts import render
from projects.models import Project
from budgets.models import Budget

def index(request):
    projects = Project.objects.all()
    budgets = Budget.objects.all()

    context = {
        'projects': projects,
        'budgets': budgets,
    }
    return render(request, 'home/index.html', context)
