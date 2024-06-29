from django.shortcuts import get_object_or_404, render, redirect
from ordenventa.models import OrdenDeCompra, OrdenVenta
from .models import OrdenCompra, OrdenPago
from .forms import OrdenCompraForm, OrdenPagoForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date, timedelta


def lista_ordenes_compra2(request):
    ordenes_compra = OrdenCompra.objects.all()
    return render(
        request, "lista_ordenes_compra.html", {"ordenes_compra": ordenes_compra}
    )


def crear_orden_compra(request):
    if request.method == "POST":
        form = OrdenCompraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_ordenes_compra"
            )  # Redirige a la lista después de guardar
    else:
        form = OrdenCompraForm()

    return render(request, "crear_orden_compra.html", {"form": form})


def ordenpago(request):
    context = {}
    form = OrdenPagoForm()
    ordenespago = OrdenPago.objects.all()
    context["ordenespago"] = ordenespago

    if request.method == "POST":
        if "save" in request.POST:
            form = OrdenPagoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("ordenpago")
        elif "delete" in request.POST:
            pk = request.POST.get("delete")
            ordenpago = OrdenPago.objects.get(id=pk)
            ordenpago.delete()
            return redirect("ordenpago")
        elif "edit" in request.POST:
            pk = request.POST.get("edit")
            ordenpago = OrdenPago.objects.get(id=pk)
            form = OrdenPagoForm(instance=ordenpago)

    context["form"] = form
    return render(request, "ordenpago.html", context)


# new methods :) ella no te quiere :P
# Vista para listar las órdenes de venta
def lista_ordenes_venta(request):

    query_codigosap = request.GET.get("codigosap", "")
    query_proyecto = request.GET.get("proyecto", "")

    ordenes_venta = OrdenVenta.objects.all().order_by("-id")

    if query_codigosap:
        ordenes_venta = ordenes_venta.filter(codigosap__icontains=query_codigosap)
    if query_proyecto:
        ordenes_venta = ordenes_venta.filter(proyecto__icontains=query_proyecto)

    if "HX-Request" in request.headers:
        # Solo devuelve el fragmento de la tabla para solicitudes HTMX
        return render(
            request,
            "fragmentos/tabla_ordenes_venta.html",
            {"ordenes_venta": ordenes_venta},
        )
    else:
        # Devuelve la página completa para solicitudes no HTMX
        return render(
            request, "lista_ordenes_venta.html", {"ordenes_venta": ordenes_venta}
        )


# Vista para mostrar las órdenes de compra de una orden de venta específica
def detalle_orden_compra(request, pk):
    orden_venta = get_object_or_404(OrdenVenta, pk=pk)
    ordenes_compra = OrdenDeCompra.objects.filter(
        item_orden_venta__ordenventa=orden_venta
    )
    return render(
        request,
        "detalle_orden_compra.html",
        {"orden_venta": orden_venta, "ordenes_compra": ordenes_compra},
    )


#para actulizar con el pago y comprobante:
def ver_detalles_pago(request, ordenventa_id=None):
    ordenes_de_pago = []
    ordenventa = None
    fecha = None

    if ordenventa_id:
        ordenventa = get_object_or_404(OrdenVenta, pk=ordenventa_id)
        ordenes_de_pago = OrdenDeCompra.objects.filter(
            item_orden_venta__ordenventa=ordenventa, precio_total__gt=0.00
        )
    else:
        fecha_str = request.GET.get("fecha_pago")
        if fecha_str:
            fecha = parse_date(fecha_str)
            if fecha:
                ordenes_de_pago = OrdenDeCompra.objects.filter(
                    Q(fecha_pago=fecha) | Q(fecha_pagada=fecha), precio_total__gt=0.00
                )

    context = {
        "ordenes_de_pago": ordenes_de_pago,
        "ordenventa": ordenventa,
        "fecha": fecha,
    }
    return render(request, "ver_detalles_pago.html", context)

# actulaiar el html ;
@csrf_exempt  # Considera la seguridad al usar CSRF exempt
def actualizar_pago(request, pk):
    if request.method == 'POST':
        orden = get_object_or_404(OrdenDeCompra, pk=pk)
        
        # Actualizar monto_pagado
        monto_pagado = request.POST.get('monto_pagado')
        if monto_pagado is not None:
            orden.monto_pagado = monto_pagado
        
        # Actualizar fecha_pagada
        fecha_pagada_str = request.POST.get('fecha_pagada')
        if fecha_pagada_str:
            orden.fecha_pagada = parse_date(fecha_pagada_str)
        
        # Actualizar comprobante_pago si hay un archivo
        comprobante = request.FILES.get('comprobante_pago')
        if comprobante:
            orden.comprobante_pago = comprobante

        orden.save()

        # Puedes decidir el tipo de respuesta dependiendo de tu flujo de trabajo
        # Si estás usando htmx, podrías querer devolver una respuesta JSON
        return JsonResponse({'status': 'success'})

    # Si no es POST, puedes decidir qué hacer, redirigir a otra página quizás
    return redirect('alguna_url_de_redireccionamiento')


#cronograma semaforo
def cronograma_ordenes_compra(request):
    ordenes_compra = OrdenDeCompra.objects.all().order_by('fecha_pago')
    hoy = timezone.localtime(timezone.now()).date()  # Obtiene la fecha actual
    proximo = hoy + timedelta(days=30)  # Define el umbral para "próximo vencimiento"

    for orden in ordenes_compra:
        if not orden.fecha_pago:
            orden.estado_clase = 'table-secondary'  # Caso sin fecha de pago definida
        elif orden.fecha_pago <= hoy:
            orden.estado_clase = 'table-danger'  # Orden de compra vencida o vence hoy
        elif orden.fecha_pago <= proximo:
            orden.estado_clase = 'table-warning'  # Orden de compra próxima a vencer
        else:
            orden.estado_clase = 'table-info'  # Orden de compra con vencimiento lejano

    return render(request, 'cronograma/cronograma_ordenes_compra.html', {
        'ordenes_compra': ordenes_compra,
        'ahora': timezone.localtime(timezone.now()),
    })