from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Budget, BudgetItem
from .forms import BudgetForm, BudgetItemQuantityForm
from inventory.models import EPPS, Equipos, ManoDeObra, Materiales, Misc, Herramientas, Transporte, Consumibles, Alimentos
from .utils import export_budget_report_to_excel 
from django.contrib.contenttypes.models import ContentType

class BudgetListView(ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'

class BudgetDetailView(DetailView):
    model = Budget
    template_name = 'budgets/budget_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = reverse_lazy('budget-export', kwargs={'pk': self.object.pk})
        return context
    
class BudgetCreateView(CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budget-list')

    def get_success_url(self):
        return reverse_lazy('budget-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save()
        inventarios_list = [
            form.cleaned_data.get('inventarios_equipos', []),
            form.cleaned_data.get('inventarios_epps', []),
            form.cleaned_data.get('inventarios_transporte', []),
            form.cleaned_data.get('inventarios_materiales', []),
            form.cleaned_data.get('inventarios_consumibles', []),
            form.cleaned_data.get('inventarios_alimentos', []),
            form.cleaned_data.get('inventarios_manodeobra', []),
            form.cleaned_data.get('inventarios_herramientas', []),
            form.cleaned_data.get('inventarios_misc', [])
        ]
        for inventarios in inventarios_list:
            for inventario in inventarios:
                BudgetItem.objects.create(
                    budget=self.object,
                    content_type=ContentType.objects.get_for_model(inventario),
                    object_id=inventario.id,
                    cantidad=1
                )
        self.object.calcular_valor_total()
        return redirect(self.get_success_url())

class BudgetUpdateView(UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'

    def get_success_url(self):
        return reverse_lazy('budget-detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        initial['inventarios_equipos'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Equipos)).values_list('object_id', flat=True)
        initial['inventarios_epps'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(EPPS)).values_list('object_id', flat=True)
        initial['inventarios_transporte'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Transporte)).values_list('object_id', flat=True)
        initial['inventarios_materiales'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Materiales)).values_list('object_id', flat=True)
        initial['inventarios_consumibles'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Consumibles)).values_list('object_id', flat=True)
        initial['inventarios_alimentos'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Alimentos)).values_list('object_id', flat=True)
        initial['inventarios_manodeobra'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(ManoDeObra)).values_list('object_id', flat=True)
        initial['inventarios_herramientas'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Herramientas)).values_list('object_id', flat=True)
        initial['inventarios_misc'] = self.object.items.filter(content_type=ContentType.objects.get_for_model(Misc)).values_list('object_id', flat=True)
        return initial

    def form_valid(self, form):
        budget = form.save(commit=False)
        existing_items = {item.object_id: item for item in budget.items.all()}
        new_inventarios_list = [
            form.cleaned_data.get('inventarios_equipos', []),
            form.cleaned_data.get('inventarios_epps', []),
            form.cleaned_data.get('inventarios_transporte', []),
            form.cleaned_data.get('inventarios_materiales', []),
            form.cleaned_data.get('inventarios_consumibles', []),
            form.cleaned_data.get('inventarios_alimentos', []),
            form.cleaned_data.get('inventarios_manodeobra', []),
            form.cleaned_data.get('inventarios_herramientas', []),
            form.cleaned_data.get('inventarios_misc', [])
        ]

        new_inventarios = []
        for inventarios in new_inventarios_list:
            new_inventarios.extend(inventarios)

        new_inventarios_pks = [inventario.pk for inventario in new_inventarios]

        # Elimina los ítems que ya no están en el formulario
        for inventario_pk, item in existing_items.items():
            if inventario_pk not in new_inventarios_pks:
                item.delete()

        # Actualiza o crea los ítems
        for inventario in new_inventarios:
            if inventario.pk in existing_items:
                # Si el ítem ya existe, actualiza su cantidad
                item = existing_items[inventario.pk]
                item.cantidad = form.cleaned_data.get(f'{item.pk}-cantidad', item.cantidad)
                item.save()
            else:
                # Si el ítem es nuevo, créalo con la cantidad predeterminada
                BudgetItem.objects.create(
                    budget=budget,
                    content_type=ContentType.objects.get_for_model(inventario),
                    object_id=inventario.id,
                    cantidad=1
                )

        budget.calcular_valor_total()
        return redirect(self.get_success_url())



class BudgetItemUpdateView(UpdateView):
    model = Budget
    template_name = 'budgets/budget_item_update_form.html'
    form_class = BudgetItemQuantityForm

    def get_success_url(self):
        return reverse_lazy('budget-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = BudgetItem.objects.filter(budget=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        items = BudgetItem.objects.filter(budget=self.object)
        form_data = request.POST
        is_valid = True
        
        for item in items:
            item_form = BudgetItemQuantityForm(form_data, instance=item, prefix=str(item.pk))
            if item_form.is_valid():
                item_form.save()
            else:
                is_valid = False
        
        self.object.calcular_valor_total()
        if is_valid:
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form) # type: ignore

class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budget-list')

def export_budget_report(request, pk):
    return export_budget_report_to_excel(request, pk)
