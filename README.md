# SalesInsight PY

## Sobre o projeto
O projeto tem como o objetivo análise e visualização de dados de vendas desenvolvida em Python. O projeto gera (ou carrega) um dataset de vendas, inspeciona, limpa, transforma, agrega e visualiza os dados, produzindo métricas por mês, trimestre, produto, categoria e região, além de uma segmentação de clientes por faixa de gasto.

## O que o projeto analisa
- Receita total e volume de vendas por mês e por trimestre
- Top 5 produtos e receita por categoria
- Receita e ticket médio por região
- Segmentação de clientes (Bronze, Prata, Ouro)
- Relação entre quantidade vendida e receita por transação
- Exportação de relatórios em CSV e JSON e de gráficos em PNG

## Conceitos aplicados (Módulo 01)
- Lógica de programação: variáveis, tipos, operadores, if/elif/else, for
- Estruturas de dados: listas, tuplas, dicionários (relatório de limpeza e dicionário de métricas)
- Funções com parâmetros, retorno e docstring; funções lambda; função de ordem superior (`processar_coluna`)
- Classe `AnalisadorDeVendas` organizando o fluxo
- Leitura e escrita de CSV e JSON (`to_csv`, `json.dump`, `json.load`)
- Módulo datetime: conversão de datas e extração de mês, trimestre e ano
- Pandas: DataFrames, filtros booleanos, groupby, colunas derivadas
- Matplotlib e Seaborn: linha, barra, dispersão, subplots 2x2, exportação PNG
- Git e GitHub: branches e commits

## Como executar
### Google Colab
1. Abra o `salesinsight.ipynb` no Colab (Arquivo > Fazer upload de notebook).
2. Clique em Ambiente de execução > Executar tudo.

### Localmente
```
pip install pandas numpy matplotlib seaborn
python salesinsight.py
```
O arquivo `vendas.csv` é gerado automaticamente na primeira execução.

## Estrutura
```
salesinsight-py/
|-- salesinsight.py      # fluxo principal
|-- salesinsight.ipynb   # mesma versão em notebook
|-- README.md
|-- outputs/             # criada ao executar
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/ (4 arquivos .png)
```

## Decisões técnicas
As linhas com data inválida foram **removidas** em vez de mantidas, porque toda a análise temporal (mês, trimestre, gráfico de linha) depende da data. Inventar uma data colocaria a receita no mês errado e distorceria os resultados. Como são poucas linhas, a perda não compromete a análise.

## Melhorias futuras
- Projeção de receita com média móvel
- Tabela cruzada mês x categoria
- Ajustar as faixas Bronze/Prata/Ouro, pois a maioria dos clientes ficou como Ouro

## Ferramentas
Python 3.10+, Google Colab, pandas, numpy, matplotlib, seaborn, json, datetime, os, random, GitHub.
