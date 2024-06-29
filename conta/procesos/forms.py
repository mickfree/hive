from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from procesos.models import Proceso, Subproceso
from tareas.models import Tarea

class ProcesoForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'nombre-proceso-input',
                'placeholder': 'Crea tu proceso aqui',
                'class': 'form-control'  # Asegúrate de tener esta clase para el estilo de Crispy Forms
            }
        ),
        label=''  # Etiqueta vacía para no mostrarla
    )

    class Meta:
        model = Proceso
        fields = ['nombre']
        labels = {
            'nombre': '',  # También establece una etiqueta vacía aquí
        }

    def __init__(self, *args, **kwargs):
        super(ProcesoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'  # Método de envío del formulario
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar', css_class='btn btn-primary mt-2')  # Botón de envío con estilo
        )

class ProcesoEditForm(forms.ModelForm):
    subprocesos = forms.ModelMultipleChoiceField(
        queryset=Subproceso.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    tareas = forms.ModelMultipleChoiceField(
        queryset=Tarea.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Proceso
        fields = ['nombre', 'subprocesos', 'tareas']

class SubprocesoForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'nombre-subproceso-input',
                'placeholder': 'Crea Subproceso',
                'class': 'form-control'
            }
        ),
        label=''  # Etiqueta vacía para no mostrarla
    )

    class Meta:
        model = Subproceso
        fields = ['proceso', 'nombre']
        labels = {
            'proceso': '',  # Etiqueta vacía
            'nombre': '',  # Etiqueta vacía
        }

    def __init__(self, *args, **kwargs):
        super(SubprocesoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('proceso', css_class='form-group col-md-6 mb-0'),  # Ajusta el tamaño del campo proceso
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar', css_class='btn btn-primary mt-2')
        )

        # Configuración del queryset y valor inicial para el campo 'proceso'
        ultimo_proceso = Proceso.objects.order_by('-id').first()
        if self.instance.pk and self.instance.proceso.exists():
            proceso_actual = self.instance.proceso.first()
        else:
            proceso_actual = None

        queryset_proceso = Proceso.objects.filter(
            id__in=filter(None, [ultimo_proceso.id if ultimo_proceso else None, proceso_actual.id if proceso_actual else None])
        )
        self.fields['proceso'].queryset = queryset_proceso

        if ultimo_proceso:
            self.fields['proceso'].queryset = Proceso.objects.filter(id=ultimo_proceso.id)
            self.fields['proceso'].initial = ultimo_proceso.id

class SubprocesoEditForm(forms.ModelForm):
    proceso = forms.ModelMultipleChoiceField(
        queryset=Subproceso.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Subproceso
        fields = ['proceso', 'nombre']

class TareaPruebaForm(forms.ModelForm):
    # Define los campos con sus respectivos widgets y placeholders
    verbo = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'verbo-tarea-input',  # ID único para el campo 'verbo'
                'placeholder': 'Describa la acción',
                'class': 'form-control'
            }
        ),
        label=''
    )
    objeto = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Objeto'}), label='')
    unidad_de_medida = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Unidad de Medida'}), label='')
    tiempo_tarea = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Tiempo de la Tarea'}), label='')

    class Meta:
        model = Tarea
        fields = ['subproceso', 'verbo', 'objeto', 'unidad_de_medida', 'tiempo_tarea']
        labels = {
            'subproceso': '',  # Sin etiqueta
            'verbo': '',       # Confirmado que no hay etiqueta
            'objeto': '',      # Sin etiqueta
            'unidad_de_medida': '',  # Sin etiqueta
            'tiempo_tarea': '',     # Sin etiqueta
        }

    def __init__(self, *args, **kwargs):
        super(TareaPruebaForm, self).__init__(*args, **kwargs)

        ultimo_subproceso = Subproceso.objects.order_by('-id').first()
        subproceso_actual = self.instance.subproceso if self.instance and self.instance.pk and self.instance.subproceso else None

        queryset_subproceso = Subproceso.objects.filter(
            id__in=filter(None, [ultimo_subproceso.id if ultimo_subproceso else None, subproceso_actual.id if subproceso_actual else None])
        )
        self.fields['subproceso'].queryset = queryset_subproceso

        if ultimo_subproceso:
            self.fields['subproceso'].initial = ultimo_subproceso.id

        # Establecer placeholders para el campo 'subproceso' si es necesario
        self.fields['subproceso'].widget.attrs.update({'placeholder': 'Subproceso'})





#forms para
class ProcesosForm(forms.ModelForm):
    subprocesos = forms.ModelMultipleChoiceField(
        queryset=Subproceso.objects.all(),
        required=False,
        label='Subprocesos',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Proceso
        fields = ['nombre', 'subprocesos']

