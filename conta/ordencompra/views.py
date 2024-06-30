from django.shortcuts import get_object_or_404, render, redirect
from ordenventa.models import OrdenDeCompra, OrdenVenta
from django.http import JsonResponse
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from extractos.models import Banco

def lista_ordenes_compra(request):
    ordenes_venta = OrdenVenta.objects.all().order_by("-id")
    return render(
        request, "lista_ordenes_compra.html", {"ordenes_venta": ordenes_venta}
    )

def ver_detalles_pago(request, ordenventa_id=None):
    ordenes_de_pago = []
    ordenventa = None
    fecha = None

    bancos = Banco.objects.all() 

    if ordenventa_id:
        ordenventa = get_object_or_404(OrdenVenta, pk=ordenventa_id)
        ordenes_de_pago = OrdenDeCompra.objects.filter(
            item_orden_venta__ordenventa=ordenventa, precio_total__gt=0.00
        ).select_related('proveedor')
    else:
        fecha_str = request.GET.get("fecha_pago")
        if fecha_str:
            fecha = parse_date(fecha_str)
            if fecha:
                ordenes_de_pago = OrdenDeCompra.objects.filter(
                    Q(fecha_pago=fecha) | Q(fecha_pagada=fecha), precio_total__gt=0.00
                ).select_related('proveedor')

    context = {
        "ordenes_de_pago": ordenes_de_pago,
        "ordenventa": ordenventa,
        "fecha": fecha,
        "bancos": bancos
    }
    return render(request, "ver_detalles_pago.html", context)

@csrf_exempt
def actualizar_pago(request, pk):
    if request.method == 'POST':
        orden = get_object_or_404(OrdenDeCompra, pk=pk)

        print(f"Procesando orden {orden.pk} con item_orden_venta {orden.item_orden_venta}")

        monto_pagado = request.POST.get(f'monto_pagado_{pk}')
        if monto_pagado is not None:
            orden.monto_pagado = monto_pagado
        
        fecha_pagada_str = request.POST.get(f'fecha_pagada_{pk}')
        if fecha_pagada_str:
            orden.fecha_pagada = parse_date(fecha_pagada_str)
        
        comprobante = request.FILES.get(f'comprobante_pago_{pk}')

        if comprobante:
            orden.comprobante_pago = comprobante
        
        numero_movimiento_bancario = request.POST.get(f'numero_movimiento_bancario_{pk}')
        if numero_movimiento_bancario:
            orden.numero_movimiento_bancario = numero_movimiento_bancario

        banco_id = request.POST.get(f'banco_relacionado_{pk}')
        if banco_id:
            try:
                banco = Banco.objects.get(pk=banco_id)  # Obtener la instancia de Banco
                orden.banco_relacionado = banco
            except Banco.DoesNotExist:
                print("Banco no encontrado con ID:", banco_id)
                return JsonResponse({'status': 'error', 'message': 'Banco no encontrado'}, status=400)

        with transaction.atomic():
            orden.save()
            if orden.item_orden_venta:
                print("Llamando update_bruto_restante")
                orden.item_orden_venta.update_bruto_restante()
                orden.item_orden_venta.save()
                print("update_bruto_restante llamado y guardado correctamente")
        
        return JsonResponse({'status': 'success'})

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
