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

    # Remove colunas completamente vazias
    df = df.dropna(axis=1, how="all")

    # SEPARA ENTRADAS (X) E ALVO (y)

    X = df.iloc[:, :-1]  # Todas as colunas menos a última
    y = df.iloc[:, -1]   # Última coluna (o que queremos prever)

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
        ("polinomio", PolynomialFeatures(degree=2, include_bias=False))
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
            "KNN": KNeighborsClassifier(),
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
            "KNN": KNeighborsRegressor(),
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

            # Validação cruzada (5 testes)
            scores = cross_val_score(pipeline_completo, X, y, cv=5)

            # Calcula a média dos scores obtidos
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

        except:
            # Se algum modelo der erro, ele apenas ignora
            pass

    # ORDENA DO MELHOR PARA O PIOR

    ranking.sort(key=lambda x: x[1], reverse=True)

    # CRIA A PASTA DO PROJETO

    os.makedirs(pasta_projeto, exist_ok=True)

    # TREINA O MELHOR MODELO FINAL

    melhor_modelo.fit(X, y)

    # Salva o modelo em arquivo
    caminho_modelo = os.path.join(pasta_projeto, "modelo.pkl")
    # Salva o melhor modelo treinado dentro desse arquivo usando o joblib
    # Isso permite que o modelo seja carregado depois sem precisar treinar novamente
    joblib.dump(melhor_modelo, caminho_modelo)

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

    # RETORNA OS RESULTADOS

    return tipo, melhor_nome, melhor_score, caminho_relatorio, caminho_grafico
