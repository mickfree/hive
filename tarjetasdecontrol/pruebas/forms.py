from django import forms
from .models import NewTarea, NewTarjeta, Incident

class NewTareaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ordenes = kwargs.pop('ordenes', [])
        super().__init__(*args, **kwargs)

        self.ordenes_list = ordenes

        self.fields['orden_venta'] = forms.ChoiceField(
            choices=[('', 'Seleccione una orden')] + [(ov_name, f"{ov_name} ({client_name})") for ov_name, client_name in ordenes],
            label='Orden de Venta',
            required=True
        )

    class Meta:
        model = NewTarea
        fields = ['verbo', 'objeto', 'orden_venta', 'unidad_de_medida', 'tiempo_tarea']

    def clean(self):
        cleaned_data = super().clean()
        orden_venta = cleaned_data.get('orden_venta')
        if orden_venta:
            for ov_name, client_name in self.ordenes_list:
                if orden_venta.startswith(ov_name):
                    cleaned_data['cliente'] = client_name
                    break
            else:
                self.add_error('orden_venta', 'Cliente no encontrado para la orden de venta seleccionada.')
        return cleaned_data 


class NewTarjetaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['tareas'].queryset = NewTarea.objects.filter(usuario=user).order_by('-id')
        if self.instance and self.instance.pk:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%d')

    class Meta:
        model = NewTarjeta
        fields = ['tareas', 'fecha']
        widgets = {
            'tareas': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '15'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['descripcion', 'duracion']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del incidente'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duración en minutos'}),
        }

    def clean_duracion(self):
        duracion = self.cleaned_data.get('duracion')
        if duracion <= 0:
            raise forms.ValidationError('La duración debe ser un número positivo.')
        return duracion
