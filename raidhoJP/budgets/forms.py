from django import forms
from inventory.models import Equipos, EPPS, Materiales, Transporte, Consumibles, Alimentos, ManoDeObra, Herramientas, Misc
from .models import Budget, BudgetItem

class BudgetForm(forms.ModelForm):
    inventarios_equipos = forms.ModelMultipleChoiceField(
        queryset=Equipos.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_epps = forms.ModelMultipleChoiceField(
        queryset=EPPS.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_transporte = forms.ModelMultipleChoiceField(
        queryset=Transporte.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_materiales = forms.ModelMultipleChoiceField(
        queryset=Materiales.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_consumibles = forms.ModelMultipleChoiceField(
        queryset=Consumibles.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_alimentos = forms.ModelMultipleChoiceField(
        queryset=Alimentos.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_manodeobra = forms.ModelMultipleChoiceField(
        queryset=ManoDeObra.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_herramientas = forms.ModelMultipleChoiceField(
        queryset=Herramientas.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
    inventarios_misc = forms.ModelMultipleChoiceField(
        queryset=Misc.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    class Meta:
        model = Budget
        fields = ['project', 'dias']


class BudgetItemQuantityForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['cantidad']
