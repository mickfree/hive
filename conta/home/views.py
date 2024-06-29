from django.shortcuts import render
from ordenventa.models import FacturaElectronica, ItemOrdenVenta, OrdenVenta, OrdenDeCompra
from cronogramas.models import Cronograma
from django.db.models import Sum
from cronogramas.models import Pago, PagoCronograma
from extractos.models import Banco
from django.utils import timezone

class DashboardView:

    @staticmethod
    def calcular_totales():
        total_ingresos_facturas = round(FacturaElectronica.objects.aggregate(Sum('monto_neto_cobrar'))['monto_neto_cobrar__sum'] or 0, 2)
        total_ingresos_cronogramas = round(Cronograma.objects.aggregate(Sum('monto_total'))['monto_total__sum'] or 0, 2)
        total_ingresos = round(total_ingresos_facturas + total_ingresos_cronogramas, 2)
        
        total_ventas = round(FacturaElectronica.objects.aggregate(Sum('monto_neto_cobrar'))['monto_neto_cobrar__sum'] or 0, 2)
        total_compras = round(OrdenDeCompra.objects.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0, 2)
        total_pagos_cronograma = round(PagoCronograma.objects.aggregate(Sum('monto_pago'))['monto_pago__sum'] or 0, 2)
        total_pagos_sunat = round(Pago.objects.aggregate(Sum('monto_pagado_sunat'))['monto_pagado_sunat__sum'] or 0, 2)

        total_egresos = round(total_compras + total_pagos_cronograma + total_pagos_sunat, 2)

        # Calcular el saldo
        saldo = round(total_ingresos - total_egresos, 2)

        return {
            'total_ingresos': total_ingresos,
            'total_ingresos_facturas': total_ingresos_facturas,
            'total_ingresos_cronogramas': total_ingresos_cronogramas,
            'total_ventas': total_ventas,
            'total_compras': total_compras,
            'total_egresos': total_egresos,
            'saldo': saldo,
        }

    @staticmethod
    def home(request):
        bancos = Banco.objects.all()
        totales = DashboardView.calcular_totales()
        context = {
            'bancos': bancos,
            **totales,
        }
        return render(request, 'home.html', context)


def compra_detalle(request):
    ordenes_de_compra = OrdenDeCompra.objects.all().order_by('clase')
    context = {
        'ordenes_de_compra': ordenes_de_compra,
    }
    return render(request, 'compra_detalle.html', context)

def ingresos_detalle(request):
    facturas = FacturaElectronica.objects.all()
    cronogramas = Cronograma.objects.all()
    context = {
        'facturas': facturas,
        'cronogramas': cronogramas,
    }
    return render(request, 'ingresos_detalle.html', context)

def egresos_detalle(request):
    clase_seleccionada = request.GET.get('clase', 'Todas')
    if clase_seleccionada == 'Todas':
        ordenes_de_compra = OrdenDeCompra.objects.all()
    else:
        ordenes_de_compra = OrdenDeCompra.objects.filter(clase=clase_seleccionada)
    
    pagos_cronograma = PagoCronograma.objects.all()

    # Calcular la suma de los montos pagados
    total_monto_pagado = round(ordenes_de_compra.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0)

    context = {
        'ordenes_de_compra': ordenes_de_compra,
        'pagos_cronograma': pagos_cronograma,
        'clase_seleccionada': clase_seleccionada,
        'total_monto_pagado': total_monto_pagado,
    }
    return render(request, 'egresos_detalle.html', context)

def venta_detalle(request):
    facturas = FacturaElectronica.objects.all()
    context = {
        'facturas': facturas,
    }
    return render(request, 'venta_detalle.html', context)

def cuentas_por_cobrar(request):
    facturas_no_pagadas = FacturaElectronica.objects.filter(factura_pagado=False)
    context = {
        'facturas_no_pagadas': facturas_no_pagadas,
    }
    return render(request, 'cuentas_por_cobrar.html', context)

def cuentas_por_pagar(request):
    ordenes_no_pagadas = OrdenDeCompra.objects.filter(fecha_pagada__isnull=True)
    context = {
        'ordenes_no_pagadas': ordenes_no_pagadas,
    }
    return render(request, 'cuentas_por_pagar.html', context)