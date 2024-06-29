from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from ordenventa.models import OrdenVenta, ItemOrdenVenta, OrdenDeCompra
from reportes.forms import ProveedorForm
from reportes.models import Proveedor
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Sum, F
from django.views.generic import ListView
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from .models import Proveedor


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
            # Total bruto de los ítems de la orden de venta
            items_total_bruto = (
                ItemOrdenVenta.objects.filter(ordenventa=orden_venta).aggregate(
                    total_bruto=Sum("total_bruto")
                )["total_bruto"]
                or 0
            )

            # Total de las órdenes de compra asociadas a los ítems de la orden de venta
            precio_total_orden_compra = (
                OrdenDeCompra.objects.filter(item_orden_venta__ordenventa=orden_venta).aggregate(
                    total_precio=Sum("precio_total")
                )["total_precio"]
                or 0
            )

            # Calcula la utilidad
            utilidad = items_total_bruto - precio_total_orden_compra

            # Añade los valores calculados al diccionario
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

    def get_queryset(self):
        queryset = Proveedor.objects.annotate(
            total_asignado=Coalesce(Sum('ordenes_de_compra__precio_total'), Value(0, output_field=DecimalField()))
        ).order_by('-total_asignado', 'id')
        return queryset

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
    
class ProveedorDetailView(DetailView):
    model = Proveedor
    context_object_name = "proveedor"
    template_name = "proveedores/proveedor_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor = self.get_object()
        
        # Obtener todas las órdenes de compra asociadas a este proveedor
        ordenes_de_compra = OrdenDeCompra.objects.filter(proveedor=proveedor)
        
        # Calcular el total asignado (precio_total de las órdenes de compra)
        total_asignado = ordenes_de_compra.aggregate(
            total_precio=Coalesce(Sum('precio_total'), Value(0, output_field=DecimalField()))
        )['total_precio']

        # Calcular el total rendido (monto_pagado de las órdenes de compra)
        total_rendido = ordenes_de_compra.aggregate(
            total_pagado=Coalesce(Sum('monto_pagado'), Value(0, output_field=DecimalField()))
        )['total_pagado']

        # Calcular el total faltante (total asignado - total rendido)
        total_faltante = total_asignado - total_rendido

        context["ordenes_de_compra"] = ordenes_de_compra
        context["total_asignado"] = total_asignado
        context["total_rendido"] = total_rendido
        context["total_faltante"] = total_faltante

        return context
