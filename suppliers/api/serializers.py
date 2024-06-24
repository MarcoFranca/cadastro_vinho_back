from rest_framework import serializers
from suppliers.models import Supplier
from wines.api.serializers import WineSerializer


class SupplierSerializer(serializers.ModelSerializer):
    vinhos = WineSerializer(many=True, read_only=True)  # Lista de vinhos

    class Meta:
        model = Supplier
        fields = ['id', 'user', 'nome', 'contato', 'telefone', 'email', 'endereco', 'vinhos']
        read_only_fields = ['user']
