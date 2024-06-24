from decimal import Decimal
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from suppliers.models import Supplier
from django.conf import settings


class Wine(models.Model):
    MEIA = 'meia'
    INTEIRA = 'inteira'
    TAMANHO_CHOICES = [
        (MEIA, 'Meia Garrafa'),
        (INTEIRA, 'Garrafa Inteira'),
    ]

    imagem = models.ImageField(upload_to='wine_images/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wines')
    nome = models.CharField(max_length=255, db_index=True)
    vinicula = models.CharField(max_length=255, db_index=True)
    pais = models.CharField(max_length=100, db_index=True)
    uva = models.CharField(max_length=100, db_index=True)
    safra = models.CharField(max_length=4, validators=[RegexValidator(regex='^\d{4}$', message='Ano da safra deve conter 4 dígitos.')])
    tamanho = models.CharField(max_length=10, choices=TAMANHO_CHOICES)
    fornecedores = models.ManyToManyField(Supplier, related_name='vinhos')
    valor_custo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, editable=False)
    estoque = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.preco_venda = self.valor_custo * (1 + self.markup / 100)
        super(Wine, self).save(*args, **kwargs)

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
