from django import forms
from .models import Banco

class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nombre_banco', 'numero_cuenta_banco', 'detalle_banco']

class CargaExtractoForm(forms.Form):
    banco = forms.ModelChoiceField(queryset=Banco.objects.all(), required=True, label='Banco')
    archivo_excel = forms.FileField(label='Archivo Excel')
