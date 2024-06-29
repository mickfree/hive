from rest_framework import serializers
from .models import OrdenVenta, ItemOrdenVenta


class ItemOrdenVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemOrdenVenta
        fields = "__all__"


class OrdenVentaSerializer(serializers.ModelSerializer):
    items = ItemOrdenVentaSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenVenta
        fields = "__all__"
