from rest_framework import serializers
from wines.models import Wine, MovimentoEstoque
from suppliers.models import Supplier


class WineSerializer(serializers.ModelSerializer):
    fornecedores = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), many=True)

    class Meta:
        model = Wine
        fields = ['id', 'user', 'imagem', 'nome', 'vinicula', 'pais', 'uva', 'safra', 'tamanho', 'fornecedores', 'valor_custo', 'markup', 'preco_venda', 'estoque']
        read_only_fields = ['user', 'preco_venda']

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem:
            return request.build_absolute_uri(obj.imagem.url)
        return None

    def validate_fornecedores(self, value):
        # Ensure that all fornecedores belong to the authenticated user
        user = self.context['request'].user
        for fornecedor in value:
            if fornecedor.user != user:
                raise serializers.ValidationError("You can only associate wines with your own suppliers.")
        return value


class MovimentoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentoEstoque
        fields = '__all__'
