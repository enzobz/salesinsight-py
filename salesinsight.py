import os
import json
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

MESES = {1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril", 5: "Maio",
         6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro",
         11: "Novembro", 12: "Dezembro"}

CORES_CATEGORIA = {"Computadores": "#1f4e79",
                   "Celulares": "#e07a1f",
                   "Perifericos": "#2e8b57"}


def gerar_dataset_vendas(n_registros=200, seed=42):
    """Gera um dataset sintetico de vendas com dados sujos."""
    random.seed(seed)
    np.random.seed(seed)
    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor",
                "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120,
              "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    data_inicio = datetime(2025, 1, 1)
    dados = []
    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 50):03d}"
        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"
        dados.append({
            "id_venda": i + 1, "data_venda": data_txt,
            "cliente": cliente, "produto": produto,
            "categoria": categoria, "regiao": random.choice(regioes),
            "quantidade": quantidade, "preco_unitario": preco,
        })
    return pd.DataFrame(dados)


def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df


def tratar_dados(df):
    """Limpa o DataFrame. Retorna (df_limpo, relatorio)."""
    df = df.copy()
    n_inicial = len(df)

    colunas_texto = ["cliente", "produto", "categoria", "regiao"]
    antes = df[colunas_texto].copy()
    for col in colunas_texto:
        df[col] = df[col].astype(str).str.strip()
    linhas_texto_alterado = int((antes != df[colunas_texto]).any(axis=1).sum())

    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    n_datas_invalidas = int(df["data_venda"].isna().sum())
    df = df.dropna(subset=["data_venda"])

    tipo_qtd_antes = str(df["quantidade"].dtype)
    tipo_preco_antes = str(df["preco_unitario"].dtype)
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    relatorio = {
        "registros_iniciais": n_inicial,
        "removidos_data_invalida": n_datas_invalidas,
        "datas_convertidas_para_datetime": len(df),
        "linhas_com_espacos_corrigidos": linhas_texto_alterado,
        "quantidade_tipo": f"{tipo_qtd_antes} -> {df['quantidade'].dtype}",
        "preco_tipo": f"{tipo_preco_antes} -> {df['preco_unitario'].dtype}",
        "sem_alteracao_de_conteudo": len(df) - linhas_texto_alterado,
        "registros_finais": len(df),
    }
    print("\n=== RELATORIO DE LIMPEZA ===")
    for chave, valor in relatorio.items():
        print(f"{chave:35} {valor}")
    return df.reset_index(drop=True), relatorio


def criar_colunas_derivadas(df):
    """Cria receita_total, mes, mes_nome, trimestre, ano e faixa_receita_item."""
    df = df.copy()
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]
    df["mes"] = df["data_venda"].dt.month
    df["mes_nome"] = df["mes"].map(MESES)
    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)
    df["ano"] = df["data_venda"].dt.year

    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
    df["faixa_receita_item"] = "Nao Classificado"
    for condicao, faixa in zip(condicoes, faixas):
        df.loc[condicao, "faixa_receita_item"] = faixa
    return df


def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """Aplica uma funcao recebida como argumento a uma coluna."""
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df


def calcular_metricas(df):
    """Retorna um dicionario {nome_da_metrica: DataFrame}."""
    metricas = {}
    metricas["por_mes"] = (
        df.groupby(["mes", "mes_nome"])
        .agg(receita_total=("receita_total", "sum"),
             quantidade=("quantidade", "sum"),
             n_vendas=("id_venda", "count"))
        .reset_index().sort_values("mes")
    )
    metricas["por_trimestre"] = (
        df.groupby("trimestre")["receita_total"].sum().reset_index()
    )
    metricas["top_produtos"] = (
        df.groupby("produto")["receita_total"].sum()
        .sort_values(ascending=False).head(5).reset_index()
    )
    metricas["por_categoria"] = (
        df.groupby("categoria")["receita_total"].sum()
        .sort_values(ascending=False).reset_index()
    )
    metricas["por_regiao"] = (
        df.groupby("regiao")
        .agg(receita_total=("receita_total", "sum"),
             ticket_medio=("receita_total", "mean"))
        .sort_values("receita_total", ascending=False).reset_index()
    )
    for nome, tabela in metricas.items():
        print(f"\n=== {nome.upper().replace('_', ' ')} ===")
        print(tabela.round(2).to_string(index=False))
    return metricas


def segmentar_clientes(df):
    """Soma o gasto por cliente e classifica em Bronze/Prata/Ouro."""
    clientes = (
        df.groupby("cliente")["receita_total"].sum()
        .reset_index().rename(columns={"receita_total": "total_gasto"})
    )
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda g: "Bronze" if g < 5000 else ("Prata" if g <= 15000 else "Ouro")
    )
    clientes = clientes.sort_values("total_gasto", ascending=False)
    print("\n=== TOP 10 CLIENTES ===")
    print(clientes.head(10).round(2).to_string(index=False))
    print("\n=== CLIENTES POR SEGMENTO ===")
    print(clientes["segmento"].value_counts())
    return clientes.reset_index(drop=True)


def gerar_graficos(df, metricas, pasta="outputs/graficos"):
    """Gera e exporta as 4 figuras em PNG."""
    os.makedirs(pasta, exist_ok=True)
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14
    por_mes = metricas["por_mes"]
    top = metricas["top_produtos"]
    por_regiao = metricas["por_regiao"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(por_mes["mes"], por_mes["receita_total"], marker="o",
            linewidth=2, color="#1f4e79", label="Receita mensal")
    ax.set_xticks(por_mes["mes"])
    ax.set_xticklabels(por_mes["mes_nome"].str[:3])
    ax.set_title("Receita Total por Mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Receita Total (R$)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{pasta}/receita_por_mes.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top, y="produto", x="receita_total", hue="produto",
                legend=False, palette="Blues_d", ax=ax)
    ax.set_title("Top 5 Produtos por Receita")
    ax.set_xlabel("Receita Total (R$)")
    ax.set_ylabel("Produto")
    plt.tight_layout()
    plt.savefig(f"{pasta}/top_produtos.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 6))
    for categoria, cor in CORES_CATEGORIA.items():
        sub = df[df["categoria"] == categoria]
        ax.scatter(sub["quantidade"], sub["receita_total"],
                   color=cor, alpha=0.7, label=categoria)
    ax.set_title("Quantidade x Receita por Transacao")
    ax.set_xlabel("Quantidade vendida")
    ax.set_ylabel("Receita da transacao (R$)")
    ax.legend(title="Categoria")
    plt.tight_layout()
    plt.savefig(f"{pasta}/quantidade_vs_receita.png", dpi=150)
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes[0, 0].plot(por_mes["mes"], por_mes["receita_total"], marker="o",
                    color="#1f4e79", label="Receita mensal")
    axes[0, 0].set_title("Receita por Mes")
    axes[0, 0].set_xlabel("Mes")
    axes[0, 0].set_ylabel("R$")
    axes[0, 0].legend()

    axes[0, 1].barh(top["produto"], top["receita_total"], color="#4a7fb5")
    axes[0, 1].invert_yaxis()
    axes[0, 1].set_title("Top 5 Produtos")
    axes[0, 1].set_xlabel("R$")
    axes[0, 1].set_ylabel("Produto")

    for categoria, cor in CORES_CATEGORIA.items():
        sub = df[df["categoria"] == categoria]
        axes[1, 0].scatter(sub["quantidade"], sub["receita_total"],
                           color=cor, alpha=0.7, label=categoria)
    axes[1, 0].set_title("Quantidade x Receita")
    axes[1, 0].set_xlabel("Quantidade")
    axes[1, 0].set_ylabel("R$")
    axes[1, 0].legend(title="Categoria", fontsize=8)

    axes[1, 1].bar(por_regiao["regiao"], por_regiao["receita_total"],
                   color=["#1f4e79", "#2e8b57", "#e07a1f", "#8e44ad", "#c0392b"])
    axes[1, 1].set_title("Receita por Regiao")
    axes[1, 1].set_xlabel("Regiao")
    axes[1, 1].set_ylabel("R$")

    fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{pasta}/painel_resumo.png", dpi=150)
    plt.close()
    print(f"\nGraficos salvos em {pasta}/")


def exportar_resultados(metricas, clientes, estatisticas):
    """Exporta os resultados em CSV e JSON."""
    os.makedirs("outputs", exist_ok=True)
    metricas["por_mes"].to_csv("outputs/metricas_por_mes.csv",
                               index=False, encoding="utf-8-sig")
    clientes.to_csv("outputs/segmentacao_clientes.csv",
                    index=False, encoding="utf-8-sig")
    serializavel = {k: round(float(v), 2) for k, v in estatisticas.items()}
    caminho = "outputs/estatisticas_gerais.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(serializavel, f, indent=4, ensure_ascii=False)
    with open(caminho, "r", encoding="utf-8") as f:
        conferencia = json.load(f)
    print(f"\nJSON gravado e lido: {conferencia}")


class AnalisadorDeVendas:
    """Organiza o fluxo de analise de ponta a ponta."""

    def __init__(self):
        self.df_bruto = None
        self.df = None
        self.relatorio_limpeza = {}
        self.metricas = {}
        self.clientes = None
        self.estatisticas = {}

    def carregar(self, caminho):
        self.df_bruto = pd.read_csv(caminho)
        return self

    def transformar(self):
        self.df, self.relatorio_limpeza = tratar_dados(self.df_bruto)
        self.df = criar_colunas_derivadas(self.df)
        self.df = processar_coluna(self.df, "receita_total",
                                   lambda x: round(x / 1000, 2),
                                   nome_saida="receita_em_milhares")
        self.df = processar_coluna(self.df, "quantidade",
                                   lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
                                   nome_saida="perfil_volume")
        return self

    def analisar(self):
        self.metricas = calcular_metricas(self.df)
        self.clientes = segmentar_clientes(self.df)
        alto_valor = self.df[self.df["faixa_receita_item"] == "Alto Valor"]
        self.estatisticas = {
            "receita_total_geral": self.df["receita_total"].sum(),
            "ticket_medio": self.df["receita_total"].mean(),
            "total_itens_vendidos": self.df["quantidade"].sum(),
            "numero_de_vendas": len(self.df),
            "numero_de_clientes": self.df["cliente"].nunique(),
            "vendas_alto_valor": len(alto_valor),
        }
        return self

    def visualizar(self):
        gerar_graficos(self.df, self.metricas)
        return self

    def resumo(self):
        exportar_resultados(self.metricas, self.clientes, self.estatisticas)
        print("\n=== RESUMO ===")
        print(f"Receita total: R$ {self.estatisticas['receita_total_geral']:,.2f}")
        print(f"Ticket medio:  R$ {self.estatisticas['ticket_medio']:,.2f}")
        print(f"Produto lider: {self.metricas['top_produtos'].iloc[0]['produto']}")
        print(f"Regiao lider:  {self.metricas['por_regiao'].iloc[0]['regiao']}")
        return self


def main():
    """Executa o fluxo completo do SalesInsight PY."""
    print("=" * 60)
    print(" SALESINSIGHT PY - Analise de Dados de Vendas")
    print("=" * 60)
    if not os.path.exists("vendas.csv"):
        gerar_dataset_vendas().to_csv("vendas.csv", index=False)
        print("Dataset vendas.csv gerado.")
    analisador = AnalisadorDeVendas()
    analisador.carregar("vendas.csv")
    inspecionar_dados(analisador.df_bruto)
    analisador.transformar()
    analisador.analisar()
    analisador.visualizar()
    analisador.resumo()
    print("\nFluxo finalizado.")


if __name__ == "__main__":
    main()
