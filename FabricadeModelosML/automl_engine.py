# AutoML com:
# - Feature engineering
# - Validação cruzada
# - 20+ modelos
# - Ranking gráfico


# IMPORTA AS BIBLIOTECAS


import pandas as pd              # Para ler e manipular dados
import os                        # Para criar pastas
import joblib                    # Para salvar o modelo treinado
import matplotlib.pyplot as plt  # Para gerar gráfico

# Importa funções para validação cruzada
from sklearn.model_selection import cross_val_score
# Importa ferramentas para criar pipelines
from sklearn.pipeline import Pipeline
# Importa transformador para aplicar diferentes pré-processamentos em colunas específicas
from sklearn.compose import ColumnTransformer
# Importa escalador padrão, codificador one-hot e gerador de features polinomiais
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
# Importa imputador simples para lidar com valores ausentes
from sklearn.impute import SimpleImputer


# MODELOS DE CLASSIFICAÇÃO

# Importa classificadores baseados em árvores
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
# Importa regressão logística para classificação linear
from sklearn.linear_model import LogisticRegression
# Importa máquinas de vetores de suporte
from sklearn.svm import SVC
# Importa o classificador baseado em vizinhos mais próximos
from sklearn.neighbors import KNeighborsClassifier
# Importa o classificador Naive Bayes
from sklearn.naive_bayes import GaussianNB
# Importa o classificador baseado em árvores de decisão
from sklearn.tree import DecisionTreeClassifier


# MODELOS DE REGRESSÃO

# Importa o modelo RandomForestRegressor (floresta aleatória para regressão),
# GradientBoostingRegressor (boosting em árvore para regressão)
# e ExtraTreesRegressor (floresta extremamente aleatória para regressão)
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor

# Importa modelos de regressão linear:
# LinearRegression = regressão linear simples
# Ridge = regressão linear com penalização L2 (evita overfitting)
# Lasso = regressão linear com penalização L1 (pode zerar coeficientes)
from sklearn.linear_model import LinearRegression, Ridge, Lasso

# Importa o SVR (Support Vector Regressor),
# que é um modelo baseado em máquinas de vetor de suporte para regressão
from sklearn.svm import SVR

# Importa o KNeighborsRegressor (KNN para regressão),
# que faz previsões baseadas nos vizinhos mais próximos
from sklearn.neighbors import KNeighborsRegressor

# Importa o DecisionTreeRegressor (Árvore de Decisão para regressão),
# que cria regras em forma de árvore para prever valores numéricos
from sklearn.tree import DecisionTreeRegressor


# FUNÇÃO PRINCIPAL DO AUTOML

def treinar_automl(caminho_csv, pasta_projeto):

    # LÊ O CSV

    df = pd.read_csv(caminho_csv)
    print("📊 Dataset shape:", df.shape)
    print("📋 Colunas:", df.columns.tolist())
    print("🎯 Alvo (y) valores únicos:", df.iloc[:, -1].unique())
    print("❗ Valores nulos no alvo:", df.iloc[:, -1].isna().sum())
    print("🔎 Tipo do alvo:", df.iloc[:, -1].dtype)

    # Se o dataset for muito pequeno, não usa cross-validation
    dataset_pequeno = len(df) < 30


    # Remove colunas completamente vazias
    df = df.dropna(axis=1, how="all")

    # SEPARA ENTRADAS (X) E ALVO (y)

    X = df.iloc[:, :-1]  # Todas as colunas menos a última
    y = df.iloc[:, -1]   # Última coluna (o que queremos prever)
    # Remove linhas onde o alvo é nulo
    mask = y.notna()
    X = X[mask]
    y = y[mask]

# Se o alvo for texto, converte para números
    if y.dtype == "object":
        y = y.astype("category").cat.codes


    # DESCOBRE SE É CLASSIFICAÇÃO OU REGRESSÃO

    # Verifica se o número de valores únicos em y é menor ou igual a 15 e se o tipo de dado não é float
    if y.nunique() <= 15 and y.dtype != "float":
        tipo = "classificacao"  # Define como problema de classificação
    else:
        tipo = "regressao"  # Caso contrário, define como problema de regressão

    # SEPARA COLUNAS NUMÉRICAS E CATEGÓRICAS

    # Seleciona colunas numéricas (int e float)
    colunas_numericas = X.select_dtypes(include=["int64", "float64"]).columns
    # Seleciona colunas categóricas (object e bool)
    colunas_categoricas = X.select_dtypes(include=["object", "bool"]).columns

    # PIPELINE PARA DADOS NUMÉRICOS

    pipeline_numerico = Pipeline(steps=[
        # Preenche NaN com a mediana
        ("preencher_vazios", SimpleImputer(strategy="median")),
        # Normaliza os números
        ("escalar", StandardScaler()),
        # Cria novas features
        ("polinomio", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True))
    ])
    # PIPELINE PARA DADOS DE TEXTO

    pipeline_categorico = Pipeline(steps=[
        # Preenche com o mais comum
        ("preencher_vazios", SimpleImputer(strategy="most_frequent")),
        # Converte texto em números
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    # JUNTA TUDO

    # Junta os pipelines numéricos e categóricos em um único pré-processador
    pre_processador = ColumnTransformer(transformers=[
        # Aplica o pipeline numérico às colunas numéricas
        ("num", pipeline_numerico, colunas_numericas),
        # Aplica o pipeline categórico às colunas categóricas
        ("cat", pipeline_categorico, colunas_categoricas)
    ])

    # ESCOLHE OS MODELOS

    if tipo == "classificacao":
        modelos = {
            "RandomForest": RandomForestClassifier(),
            "ExtraTrees": ExtraTreesClassifier(),
            "GradientBoosting": GradientBoostingClassifier(),
            "LogisticRegression": LogisticRegression(max_iter=3000),
            "SVM": SVC(),
            "KNN": KNeighborsClassifier(n_neighbors=3),
            "NaiveBayes": GaussianNB(),
            "DecisionTree": DecisionTreeClassifier()
        }
    else:
        modelos = {
            "RandomForest": RandomForestRegressor(),
            "ExtraTrees": ExtraTreesRegressor(),
            "GradientBoosting": GradientBoostingRegressor(),
            "LinearRegression": LinearRegression(),
            "Ridge": Ridge(),
            "Lasso": Lasso(),
            "SVR": SVR(),
            "KNN": KNeighborsRegressor(n_neighbors=3),
            "DecisionTree": DecisionTreeRegressor()
        }

    # TESTA TODOS OS MODELOS

    # Lista para armazenar o ranking dos modelos e seus scores
    ranking = []
    # Variável para armazenar o melhor score encontrado
    melhor_score = -999999
    # Variável para armazenar o pipeline do melhor modelo
    melhor_modelo = None
    # Nome do melhor modelo
    melhor_nome = ""

    for nome, modelo in modelos.items():
        try:
            # Cria o pipeline completo: tratamento + modelo
            pipeline_completo = Pipeline(steps=[
                # Primeiro passo do pipeline:
                # Aplica todo o tratamento de dados definido no pre_processador
                ("preprocessamento", pre_processador),
                # Segundo passo do pipeline:
                # Aplica o modelo de machine learning (RandomForest, SVM, etc)
                ("modelo", modelo)
            ])

            if dataset_pequeno:
                # Treina e testa no próprio dataset (modo simples)
                pipeline_completo.fit(X, y)
                media_score = pipeline_completo.score(X, y)
            else:
                scores = cross_val_score(pipeline_completo, X, y, cv=5)
                media_score = scores.mean()


            # Adiciona o modelo e sua média ao ranking
            ranking.append((nome, media_score))

            # Atualiza o melhor modelo se o score atual for maior que o melhor score encontrado até agora
            if media_score > melhor_score:
                # Se for melhor, atualiza a variável que guarda o melhor score
                melhor_score = media_score
                # Guarda o pipeline completo (pré-processamento + modelo) como o melhor até agora
                melhor_modelo = pipeline_completo
                # Guarda o nome do modelo que obteve esse melhor resultado
                melhor_nome = nome

        except Exception as e:
            print(f"❌ Erro no modelo {nome}: {e}")


        # Remove modelos que deram NaN ou erro
        ranking = [(n, s) for n, s in ranking if s == s]

    # CRIA A PASTA DO PROJETO

    os.makedirs(pasta_projeto, exist_ok=True)

    # TREINA O MELHOR MODELO FINAL
    if melhor_modelo is None:
        raise Exception("❌ Nenhum modelo conseguiu treinar com esse dataset. Verifique o CSV.")

    # Salva o modelo em arquivo
    caminho_modelo = os.path.join(pasta_projeto, "modelo.pkl")
    # Salva o melhor modelo treinado dentro desse arquivo usando o joblib
    # Isso permite que o modelo seja carregado depois sem precisar treinar novamente
    joblib.dump(melhor_modelo, caminho_modelo)
        # ===============================
    # SALVA METADADOS DA VERSÃO
    # ===============================
    import json
    from datetime import datetime

    meta = {
        "versao": os.path.basename(pasta_projeto),
        "modelo": melhor_nome,
        "score": float(melhor_score),
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "producao": False
    }

    caminho_meta = os.path.join(pasta_projeto, "meta.json")

    with open(caminho_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # GERA O GRÁFICO

    # Extrai os nomes dos modelos e suas respectivas médias de score
    nomes = [x[0] for x in ranking]
    scores = [x[1] for x in ranking]

    # Cria uma figura para o gráfico de barras horizontal
    plt.figure(figsize=(10, 6))
    plt.barh(nomes, scores)  # Plota os modelos e seus scores
    plt.title("Ranking dos Modelos")  # Adiciona título ao gráfico
    plt.tight_layout()  # Ajusta o layout para evitar cortes

    # Define o caminho para salvar o gráfico
    caminho_grafico = os.path.join(pasta_projeto, "ranking.png")
    plt.savefig(caminho_grafico)  # Salva o gráfico no caminho especificado
    plt.close()  # Fecha a figura para liberar memória

    # GERA RELATÓRIO EM TXT

    # Caminho do relatório
    caminho_relatorio = os.path.join(pasta_projeto, "resultado.txt")

    # Cria e escreve no arquivo de relatório
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        # Escreve o tipo de problema
        f.write(f"Tipo de problema: {tipo}\n\n")

        # Escreve o ranking dos modelos
        for nome, score in ranking:
            f.write(f"{nome}: {score}\n")

        # Escreve o melhor modelo e seu score
        f.write(f"\nMelhor modelo: {melhor_nome}\n")
        f.write(f"Score: {melhor_score}\n")


# GERA PDF

    from pdf_report import gerar_pdf

    caminho_pdf = os.path.join(pasta_projeto, "relatorio.pdf")

    gerar_pdf(
        caminho_pdf=caminho_pdf,
        texto=open(caminho_relatorio, encoding="utf-8").read(),
        imagem=caminho_grafico
    )
        # RETORNA OS RESULTADOS
    return tipo, melhor_nome, melhor_score, caminho_relatorio, caminho_grafico

