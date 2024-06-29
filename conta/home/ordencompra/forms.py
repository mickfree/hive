# en forms.py

from django import forms
from .models import OrdenCompra, OrdenPago


class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = "__all__"


class OrdenPagoForm(forms.ModelForm):
    class Meta:
        model = OrdenPago
        fields = [
            "numero_operacion",
            "orden_compra",
            "proyecto",
            "observaciones",
            "ruc_dni",
            "proveedor",
            "numero_cuenta",
            "banco",
            "monto_pagar",
            "comprobante_pdf",
        ]
