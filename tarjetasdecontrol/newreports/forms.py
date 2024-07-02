from django import forms
from pruebas.models import NewTarjeta, NewTarea
from cuentas.models import UserProfile
from django import forms
from .models import Backlog, SimpleTask


class NewGroupTarjetaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Obtener el grupo del perfil del usuario
            perfil = UserProfile.objects.get(user=user)
            grupo = perfil.grupo
            # Filtrar las tareas según el grupo del usuario
            self.fields['tareas'].queryset = NewTarea.objects.filter(usuario__userprofile__grupo=grupo).order_by('-id')
        
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
class BacklogForm(forms.ModelForm):
    simple_tasks = forms.ModelMultipleChoiceField(
        queryset=SimpleTask.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='Tareas Simples'
    )

    class Meta:
        model = Backlog
        fields = ['simple_tasks']