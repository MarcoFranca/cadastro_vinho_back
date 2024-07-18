import os
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from suppliers.models import Supplier
from django.conf import settings
from PIL import Image


def wine_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.nome}_{instance.user.id}.{ext}"
    return os.path.join('wine_images/', filename)


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png.')


class Wine(models.Model):
    MEIA = 'meia'
    INTEIRA = 'inteira'
    TAMANHO_CHOICES = [
        (MEIA, 'Meia Garrafa'),
        (INTEIRA, 'Garrafa Inteira'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imagem = models.ImageField(upload_to=wine_image_upload_to, blank=True, null=True,
                               validators=[validate_image_extension])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wines')
    nome = models.CharField(max_length=255, db_index=True)
    vinicula = models.CharField(max_length=255, db_index=True)
    pais = models.CharField(max_length=100, db_index=True)
    uva = models.CharField(max_length=100, db_index=True)
    safra = models.CharField(max_length=4, validators=[
        RegexValidator(regex='^\d{4}$', message='Ano da safra deve conter 4 dígitos.')])
    tamanho = models.CharField(max_length=10, choices=TAMANHO_CHOICES)
    fornecedores = models.ManyToManyField(Supplier, related_name='vinhos')
    valor_custo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'), editable=False)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, editable=False)
    estoque = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Find the applicable markup rule
        applicable_rule = self.user.markup_rules.filter(min_price__lte=self.valor_custo,
                                                        max_price__gte=self.valor_custo).first()
        if applicable_rule:
            self.markup = applicable_rule.percentage

        # Garantir que ambos os valores sejam Decimal
        valor_custo_decimal = Decimal(self.valor_custo)
        markup_decimal = Decimal(self.markup)
        self.preco_venda = valor_custo_decimal * (Decimal('1.0') + markup_decimal / Decimal('100'))

        # Handle image compression
        if not self._state.adding:
            try:
                old_instance = Wine.objects.get(pk=self.pk)
                if old_instance.imagem and old_instance.imagem != self.imagem:
                    old_instance.imagem.delete(save=False)
            except Wine.DoesNotExist:
                pass
        super(Wine, self).save(*args, **kwargs)
        if self.imagem:
            self.compress_image()

    def compress_image(self):
        image = Image.open(self.imagem.path)
        image = image.convert('RGB')  # Convert to RGB if the image is in a different mode
        compressed_image_path = self.imagem.path
        image.save(compressed_image_path, format='JPEG', quality=85)

    def __str__(self):
        return self.nome


class MovimentoEstoque(models.Model):
    ENTRADA = 'entrada'
    SAIDA = 'saida'
    MOVIMENTO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saida'),
    ]

    vinho = models.ForeignKey(Wine, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=MOVIMENTO_CHOICES)
    quantidade = models.PositiveIntegerField()
    data_movimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.quantidade} - {self.vinho.nome}"


class MarkupRule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='markup_rules')
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Markup percentage to apply in range")

    class Meta:
        unique_together = ('user', 'min_price', 'max_price')

    def clean(self):
        # Ensure no overlapping ranges
        overlapping_rules = MarkupRule.objects.filter(
            user=self.user,
            min_price__lt=self.max_price,
            max_price__gt=self.min_price
        ).exclude(pk=self.pk)

        if overlapping_rules.exists():
            raise ValidationError("This markup rule overlaps with an existing rule.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.min_price} - {self.max_price}: {self.percentage}%"
