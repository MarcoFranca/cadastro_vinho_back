import io

import pandas as pd
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from suppliers.models import Supplier
from wines.models import Wine, MovimentoEstoque
from wines.api.serializers import WineSerializer, MovimentoEstoqueSerializer
from rest_framework.permissions import IsAuthenticated


class WineViewSet(viewsets.ModelViewSet):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Wine.objects.filter(user=self.request.user)


class ExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obter o usuário autenticado
        user = request.user

        # Obter os vinhos do usuário
        vinhos = Wine.objects.filter(user=user)

        # Criar DataFrame para vinhos
        vinhos_data = [
            {
                'Nome': vinho.nome,
                'Vinícola': vinho.vinicula,
                'País': vinho.pais,
                'Uva': vinho.uva,
                'Safra': vinho.safra,
                'Tamanho': vinho.get_tamanho_display(),
                'Fornecedores': ', '.join([fornecedor.nome for fornecedor in vinho.fornecedores.all()]),
                'Valor de Custo': vinho.valor_custo,
                'Markup': vinho.markup,
                'Preço de Venda': vinho.preco_venda,
                'Estoque': vinho.estoque
            }
            for vinho in vinhos
        ]
        vinhos_df = pd.DataFrame(vinhos_data)

        # Criar um arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            vinhos_df.to_excel(writer, sheet_name='Vinhos', index=False)

        output.seek(0)

        # Criar resposta HTTP com o arquivo Excel
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=vinhos_fornecedores.xlsx'

        return response


class ImportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Obter o usuário autenticado
        user = request.user

        # Obter o arquivo do request
        excel_file = request.FILES.get('file')

        # Ler o arquivo Excel
        df = pd.read_excel(excel_file)

        # Substituir valores nulos por valores padrão
        df.fillna({
            'Nome': '',
            'Vinícola': '',
            'País': '',
            'Uva': '',
            'Safra': '',
            'Tamanho': 'inteira',
            'Fornecedores': '',
            'Valor de Custo': 0.0,
            'Markup': 0.0,
            'Preço de Venda': 0.0,
            'Estoque': 0
        }, inplace=True)

        # Iterar sobre as linhas do DataFrame e criar vinhos
        for index, row in df.iterrows():
            # Criar ou obter fornecedores
            fornecedores_nomes = str(row['Fornecedores']).split(', ')
            fornecedores = []
            for nome in fornecedores_nomes:
                fornecedor, created = Supplier.objects.get_or_create(nome=nome.strip(), user=user)
                fornecedores.append(fornecedor)

            # Tratar valores nulos e garantir que os valores estejam no formato correto
            tamanho = str(row['Tamanho']).lower() if not pd.isna(row['Tamanho']) else 'inteira'
            valor_custo = row['Valor de Custo'] if not pd.isna(row['Valor de Custo']) else 0.0
            markup = row['Markup'] if not pd.isna(row['Markup']) else 0.0
            preco_venda = row['Preço de Venda'] if not pd.isna(row['Preço de Venda']) else 0.0
            estoque = int(row['Estoque']) if not pd.isna(row['Estoque']) else 0

            # Criar o vinho
            vinho = Wine.objects.create(
                user=user,
                nome=row['Nome'],
                vinicula=row['Vinícola'],
                pais=row['País'],
                uva=row['Uva'],
                safra=row['Safra'],
                tamanho=tamanho,
                valor_custo=valor_custo,
                markup=markup,
                preco_venda=preco_venda,
                estoque=estoque
            )
            vinho.fornecedores.set(fornecedores)
            vinho.save()

        return Response({"message": "Vinhos importados com sucesso!"}, status=201)


class MovimentoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentoEstoque.objects.all()
    serializer_class = MovimentoEstoqueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MovimentoEstoque.objects.filter(vinho__user=self.request.user)
