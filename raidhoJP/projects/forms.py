# projects/forms.py
from django import forms
from .models import Contractor, Client, Project

class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = '__all__'

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Project
        fields = '__all__'