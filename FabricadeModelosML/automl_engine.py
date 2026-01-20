# AutoML com:
# - Feature engineering
# - Validação cruzada
# - 20+ modelos
# - Ranking gráfico

# ===============================
# IMPORTA AS BIBLIOTECAS
# ===============================

import pandas as pd              # Para ler e manipular dados
import os                        # Para criar pastas
import joblib                    # Para salvar o modelo treinado
import matplotlib.pyplot as plt  # Para gerar gráfico

# Ferramentas do Scikit-Learn
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer

# ===============================
# MODELOS DE CLASSIFICAÇÃO
# ===============================
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

# ===============================
# MODELOS DE REGRESSÃO
# ===============================
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

# ===============================
# FUNÇÃO PRINCIPAL DO AUTOML
# ===============================
def treinar_automl(caminho_csv, pasta_projeto):

    # -------------------------------
    # 1. LÊ O CSV
    # -------------------------------
    df = pd.read_csv(caminho_csv)

    # Remove colunas completamente vazias
    df = df.dropna(axis=1, how="all")

    # -------------------------------
    # 2. SEPARA ENTRADAS (X) E ALVO (y)
    # -------------------------------
    X = df.iloc[:, :-1]  # Todas as colunas menos a última
    y = df.iloc[:, -1]   # Última coluna (o que queremos prever)

    # -------------------------------
    # 3. DESCOBRE SE É CLASSIFICAÇÃO OU REGRESSÃO
    # -------------------------------
    if y.nunique() <= 15 and y.dtype != "float":
        tipo = "classificacao"
    else:
        tipo = "regressao"

    # -------------------------------
    # 4. SEPARA COLUNAS NUMÉRICAS E CATEGÓRICAS
    # -------------------------------
    colunas_numericas = X.select_dtypes(include=["int64", "float64"]).columns
    colunas_categoricas = X.select_dtypes(include=["object", "bool"]).columns

    # -------------------------------
    # 5. PIPELINE PARA DADOS NUMÉRICOS
    # -------------------------------
    pipeline_numerico = Pipeline(steps=[
        ("preencher_vazios", SimpleImputer(strategy="median")), # Preenche NaN com a mediana
        ("escalar", StandardScaler()),                           # Normaliza os números
        ("polinomio", PolynomialFeatures(degree=2, include_bias=False)) # Cria novas features
    ])

    # -------------------------------
    # 6. PIPELINE PARA DADOS DE TEXTO
    # -------------------------------
    pipeline_categorico = Pipeline(steps=[
        ("preencher_vazios", SimpleImputer(strategy="most_frequent")), # Preenche com o mais comum
        ("onehot", OneHotEncoder(handle_unknown="ignore"))             # Converte texto em números
    ])

    # -------------------------------
    # 7. JUNTA TUDO
    # -------------------------------
    pre_processador = ColumnTransformer(transformers=[
        ("num", pipeline_numerico, colunas_numericas),
        ("cat", pipeline_categorico, colunas_categoricas)
    ])

    # -------------------------------
    # 8. ESCOLHE OS MODELOS
    # -------------------------------
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

    # -------------------------------
    # 9. TESTA TODOS OS MODELOS
    # -------------------------------
    ranking = []
    melhor_score = -999999
    melhor_modelo = None
    melhor_nome = ""

    for nome, modelo in modelos.items():
        try:
            # Cria o pipeline completo: tratamento + modelo
            pipeline_completo = Pipeline(steps=[
                ("preprocessamento", pre_processador),
                ("modelo", modelo)
            ])

            # Validação cruzada (5 testes)
            scores = cross_val_score(pipeline_completo, X, y, cv=5)

            media_score = scores.mean()

            ranking.append((nome, media_score))

            # Guarda o melhor
            if media_score > melhor_score:
                melhor_score = media_score
                melhor_modelo = pipeline_completo
                melhor_nome = nome

        except:
            # Se algum modelo der erro, ele apenas ignora
            pass

    # -------------------------------
    # 10. ORDENA DO MELHOR PARA O PIOR
    # -------------------------------
    ranking.sort(key=lambda x: x[1], reverse=True)

    # -------------------------------
    # 11. CRIA A PASTA DO PROJETO
    # -------------------------------
    os.makedirs(pasta_projeto, exist_ok=True)

    # -------------------------------
    # 12. TREINA O MELHOR MODELO FINAL
    # -------------------------------
    melhor_modelo.fit(X, y)

    # Salva o modelo em arquivo
    caminho_modelo = os.path.join(pasta_projeto, "modelo.pkl")
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
