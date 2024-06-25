from rest_framework import serializers
from wines.models import Wine, MovimentoEstoque, MarkupRule
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


class MarkupRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkupRule
        fields = ['id', 'user', 'min_price', 'max_price', 'percentage']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        min_price = data.get('min_price')
        max_price = data.get('max_price')

        overlapping_rules = MarkupRule.objects.filter(
            user=user,
            min_price__lt=max_price,
            max_price__gt=min_price
        ).exclude(pk=self.instance.pk if self.instance else None)

        if overlapping_rules.exists():
            raise serializers.ValidationError("This markup rule overlaps with an existing rule.")

        return data


class MovimentoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentoEstoque
        fields = '__all__'


class MarkupRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkupRule
        fields = ['id', 'user', 'min_price', 'max_price', 'percentage']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        min_price = data.get('min_price')
        max_price = data.get('max_price')

        overlapping_rules = MarkupRule.objects.filter(
            user=user,
            min_price__lt=max_price,
            max_price__gt=min_price
        ).exclude(pk=self.instance.pk if self.instance else None)

        if overlapping_rules.exists():
            raise serializers.ValidationError("This markup rule overlaps with an existing rule.")

        return data