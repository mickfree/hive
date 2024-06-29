from django import forms
from .models import Inventario

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = '__all__'  # Usa todos los campos del modelo Inventario


class UploadExcelForm(forms.Form):
    archivo_excel = forms.FileField(label='Seleccionar archivo Excel')
