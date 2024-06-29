from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from ordenventa.models import OrdenVenta, ItemOrdenVenta
from reportes.forms import ProveedorForm
from reportes.models import Proveedor
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Sum, F


def reportes_registros(request):
    return render(request, "reportes_registros.html")


# REPORTES
class ReportesVentaListView(ListView):
    model = OrdenVenta
    template_name = "reportes/reportes.html"  # Asegúrate de crear este template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordenes_venta_con_totales = []
        for orden_venta in context["object_list"]:
            items_total_bruto = (
                ItemOrdenVenta.objects.filter(ordenventa=orden_venta).aggregate(
                    total_bruto=Sum("total_bruto")
                )["total_bruto"]
                or 0
            )

            # Calcula el precio_total_orden_compra aquí antes de usarlo
            precio_total_orden_compra = sum(
                item.orden_de_compra.precio_total
                for item in orden_venta.items.all()
                if hasattr(item, "orden_de_compra")
            )

            # Calcula la utilidad aquí antes de usarla
            utilidad = items_total_bruto - precio_total_orden_compra

            # Añade los valores calculados al diccionario una sola vez
            ordenes_venta_con_totales.append(
                {
                    "orden_venta": orden_venta,
                    "total_bruto_items": items_total_bruto,
                    "total_precio_orden_compra": precio_total_orden_compra,
                    "utilidad": utilidad,
                }
            )

        context["ordenes_venta_con_totales"] = ordenes_venta_con_totales
        return context


##### PROVEEDORES CUIDADO :T
class ProveedorListView(ListView):
    model = Proveedor
    context_object_name = "proveedores"
    template_name = "proveedores/proveedor_list.html"


class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    success_url = reverse_lazy("proveedor_list")
    template_name = "proveedores/proveedor_form.html"


class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    success_url = reverse_lazy("proveedor_list")
    template_name = "proveedores/proveedor_form.html"


class ProveedorDeleteView(DeleteView):
    model = Proveedor
    success_url = reverse_lazy("proveedor_list")
    template_name = "proveedores/proveedor_confirm_delete.html"
