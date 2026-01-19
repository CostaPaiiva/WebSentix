import pandas as pd  # Importa a biblioteca pandas para manipulação de dados
import os  # Importa a biblioteca os para interações com o sistema operacional
import joblib  # Importa a biblioteca joblib para salvar e carregar modelos
import matplotlib.pyplot as plt  # Importa a biblioteca matplotlib para criação de gráficos
from sklearn.model_selection import cross_val_score  # Importa função para validação cruzada
from sklearn.pipeline import Pipeline  # Importa a classe Pipeline para criação de pipelines
from sklearn.compose import ColumnTransformer  # Importa ColumnTransformer para transformar colunas específicas
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures  # Importa pré-processadores
from sklearn.impute import SimpleImputer  # Importa SimpleImputer para lidar com valores ausentes

# Classificação
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier  # Modelos de ensemble
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier  # Modelos lineares
from sklearn.svm import SVC  # Máquina de vetores de suporte
from sklearn.neighbors import KNeighborsClassifier  # Classificador K-Nearest Neighbors
from sklearn.naive_bayes import GaussianNB  # Classificador Naive Bayes
from sklearn.tree import DecisionTreeClassifier  # Árvore de decisão
from sklearn.neural_network import MLPClassifier  # Perceptron multicamada

# Regressão
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor  # Modelos de ensemble
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet  # Modelos lineares
from sklearn.svm import SVR  # Máquina de vetores de suporte para regressão
from sklearn.neighbors import KNeighborsRegressor  # Regressor K-Nearest Neighbors
from sklearn.tree import DecisionTreeRegressor  # Árvore de decisão para regressão
from sklearn.neural_network import MLPRegressor  # Perceptron multicamada para regressão


def treinar_automl(caminho_csv, pasta_projeto):  # Função principal para treinar o AutoML
    df = pd.read_csv(caminho_csv)  # Lê o arquivo CSV em um DataFrame
    df = df.dropna(axis=1, how="all")  # Remove colunas com todos os valores ausentes

    X = df.iloc[:, :-1]  # Separa as features (todas as colunas menos a última)
    y = df.iloc[:, -1]  # Separa o alvo (última coluna)

    if y.nunique() <= 15 and y.dtype != "float":  # Verifica se é um problema de classificação
        tipo = "classificacao"
    else:  # Caso contrário, é um problema de regressão
        tipo = "regressao"

    col_num = X.select_dtypes(include=["int64", "float64"]).columns  # Seleciona colunas numéricas
    col_cat = X.select_dtypes(include=["object", "bool"]).columns  # Seleciona colunas categóricas

    num_pipe = Pipeline(steps=[  # Pipeline para pré-processamento de colunas numéricas
        ("imputer", SimpleImputer(strategy="median")),  # Imputa valores ausentes com a mediana
        ("scaler", StandardScaler()),  # Escala os dados numéricos
        ("poly", PolynomialFeatures(degree=2, include_bias=False))  # Adiciona características polinomiais
    ])

    cat_pipe = Pipeline(steps=[  # Pipeline para pré-processamento de colunas categóricas
        ("imputer", SimpleImputer(strategy="most_frequent")),  # Imputa valores ausentes com o mais frequente
        ("onehot", OneHotEncoder(handle_unknown="ignore"))  # Codifica variáveis categóricas como one-hot
    ])

    pre = ColumnTransformer(transformers=[  # Combina os pipelines de pré-processamento
        ("num", num_pipe, col_num),  # Aplica num_pipe às colunas numéricas
        ("cat", cat_pipe, col_cat)  # Aplica cat_pipe às colunas categóricas
    ])

    if tipo == "classificacao":  # Define os modelos para classificação
        modelos = {
            "RandomForest": RandomForestClassifier(),
            "ExtraTrees": ExtraTreesClassifier(),
            "GradientBoosting": GradientBoostingClassifier(),
            "LogisticRegression": LogisticRegression(max_iter=3000),
            "RidgeClassifier": RidgeClassifier(),
            "SGDClassifier": SGDClassifier(),
            "SVC": SVC(),
            "KNN": KNeighborsClassifier(),
            "NaiveBayes": GaussianNB(),
            "DecisionTree": DecisionTreeClassifier(),
            "MLP": MLPClassifier(max_iter=3000)
        }
    else:  # Define os modelos para regressão
        modelos = {
            "RandomForest": RandomForestRegressor(),
            "ExtraTrees": ExtraTreesRegressor(),
            "GradientBoosting": GradientBoostingRegressor(),
            "LinearRegression": LinearRegression(),
            "Ridge": Ridge(),
            "Lasso": Lasso(),
            "ElasticNet": ElasticNet(),
            "SVR": SVR(),
            "KNN": KNeighborsRegressor(),
            "DecisionTree": DecisionTreeRegressor(),
            "MLP": MLPRegressor(max_iter=3000)
        }

    ranking = []  # Lista para armazenar o ranking dos modelos
    melhor_score = -999999  # Inicializa o melhor score com um valor muito baixo
    melhor_modelo = None  # Inicializa o melhor modelo como None
    melhor_nome = ""  # Inicializa o nome do melhor modelo como vazio

    for nome, modelo in modelos.items():  # Itera sobre os modelos
        try:
            pipe = Pipeline(steps=[  # Cria um pipeline com o pré-processamento e o modelo
                ("prep", pre),
                ("model", modelo)
            ])

            scores = cross_val_score(pipe, X, y, cv=5)  # Realiza validação cruzada
            score = scores.mean()  # Calcula a média dos scores

            ranking.append((nome, score))  # Adiciona o modelo e seu score ao ranking

            if score > melhor_score:  # Atualiza o melhor modelo se o score for maior
                melhor_score = score
                melhor_modelo = pipe
                melhor_nome = nome
        except:
            pass  # Ignora erros durante o treinamento

    ranking.sort(key=lambda x: x[1], reverse=True)  # Ordena o ranking em ordem decrescente de score

    os.makedirs(pasta_projeto, exist_ok=True)  # Cria a pasta do projeto, se não existir

    melhor_modelo.fit(X, y)  # Treina o melhor modelo com todos os dados
    joblib.dump(melhor_modelo, os.path.join(pasta_projeto, "modelo.pkl"))  # Salva o melhor modelo

    # Gráfico
    nomes = [x[0] for x in ranking]  # Extrai os nomes dos modelos do ranking
    scores = [x[1] for x in ranking]  # Extrai os scores dos modelos do ranking

    plt.figure(figsize=(10, 6))  # Define o tamanho da figura
    plt.barh(nomes, scores)  # Cria um gráfico de barras horizontal
    plt.title("Ranking dos Modelos")  # Adiciona um título ao gráfico
    plt.tight_layout()  # Ajusta o layout do gráfico
    caminho_grafico = os.path.join(pasta_projeto, "ranking.png")  # Define o caminho para salvar o gráfico
    plt.savefig(caminho_grafico)  # Salva o gráfico
    plt.close()  # Fecha a figura

    # Relatório
    relatorio = os.path.join(pasta_projeto, "resultado.txt")  # Define o caminho para salvar o relatório
    with open(relatorio, "w", encoding="utf-8") as f:  # Abre o arquivo de relatório para escrita
        f.write(f"Tipo: {tipo}\n\n")  # Escreve o tipo de problema
        for nome, score in ranking:  # Itera sobre o ranking
            f.write(f"{nome}: {score}\n")  # Escreve o nome e o score de cada modelo
        f.write(f"\nMelhor modelo: {melhor_nome}\n")  # Escreve o melhor modelo
        f.write(f"Score: {melhor_score}\n")  # Escreve o score do melhor modelo

    return tipo, melhor_nome, melhor_score, relatorio, caminho_grafico  # Retorna os resultados principais
