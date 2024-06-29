# Generated by Django 5.0.6 on 2024-06-25 01:51

import django.core.validators
import django.db.models.deletion
import uuid
import wines.models
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('suppliers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wine',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('imagem', models.ImageField(blank=True, null=True, upload_to=wines.models.wine_image_upload_to, validators=[wines.models.validate_image_extension])),
                ('nome', models.CharField(db_index=True, max_length=255)),
                ('vinicula', models.CharField(db_index=True, max_length=255)),
                ('pais', models.CharField(db_index=True, max_length=100)),
                ('uva', models.CharField(db_index=True, max_length=100)),
                ('safra', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator(message='Ano da safra deve conter 4 dígitos.', regex='^\\d{4}$')])),
                ('tamanho', models.CharField(choices=[('meia', 'Meia Garrafa'), ('inteira', 'Garrafa Inteira')], max_length=10)),
                ('valor_custo', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('markup', models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=5)),
                ('preco_venda', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10)),
                ('estoque', models.PositiveIntegerField(default=0)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fornecedores', models.ManyToManyField(related_name='vinhos', to='suppliers.supplier')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wines', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MovimentoEstoque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saida')], max_length=10)),
                ('quantidade', models.PositiveIntegerField()),
                ('data_movimento', models.DateTimeField(auto_now_add=True)),
                ('vinho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wines.wine')),
            ],
        ),
        migrations.CreateModel(
            name='MarkupRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('percentage', models.DecimalField(decimal_places=2, help_text='Markup percentage to apply in range', max_digits=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markup_rules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'min_price', 'max_price')},
            },
        ),
    ]
