def treinar_automl(caminho_csv, pasta_projeto):
    """
    Função principal responsável por:
    - Ler um arquivo CSV
    - Identificar automaticamente se o problema é de classificação ou regressão
    - Preparar os dados para treino
    """

    # ===============================
    # IMPORTA BIBLIOTECAS
    # ===============================

    import pandas as pd              # Biblioteca para manipulação de dados (DataFrame)
    import os                         # Funções para lidar com arquivos e diretórios
    import joblib                     # Usada para salvar e carregar modelos treinados
    import json                       # Manipulação de arquivos JSON
    from datetime import datetime     # Trabalhar com data e hora
    import matplotlib.pyplot as plt   # Criação de gráficos
    import shutil                     # Copiar, mover e apagar arquivos/pastas
    import matplotlib                 # Biblioteca base do matplotlib

    # Define o backend "Agg" para evitar erros em ambientes sem interface gráfica (ex: Flask, servidor)
    matplotlib.use("Agg")

    # ===============================
    # LÊ CSV
    # ===============================

    # Lê o arquivo CSV a partir do caminho informado
    df = pd.read_csv(caminho_csv)

    # Remove colunas que possuem apenas valores nulos
    df = df.dropna(axis=1, how="all")

    # Exibe no terminal o número de linhas e colunas do dataset
    print("📊 Dataset shape:", df.shape)

    # Exibe o nome de todas as colunas do dataset
    print("📋 Colunas:", df.columns.tolist())

    # ===============================
    # SEPARA X e y
    # ===============================

    # X recebe todas as colunas exceto a última (variáveis independentes)
    X = df.iloc[:, :-1]

    # y recebe apenas a última coluna (variável alvo)
    y = df.iloc[:, -1]

    # Cria uma máscara booleana indicando onde y NÃO é nulo
    mask = y.notna()

    # Remove das features as linhas onde o target é nulo
    X = X[mask]

    # Remove do target os valores nulos
    y = y[mask]

    # ===============================
    # DETECTA TIPO DE PROBLEMA
    # ===============================

    # Se o tipo da variável alvo for texto (object)
    if y.dtype == "object":
        # Considera como problema de classificação
        tipo = "classificacao"

        # Converte categorias em números inteiros
        y = y.astype("category").cat.codes

    else:
        # Se o número de valores únicos for pequeno (<= 15)
        if y.nunique() <= 15:
            # Trata como classificação
            tipo = "classificacao"

            # Converte os rótulos em códigos numéricos
            y = y.astype("category").cat.codes
        else:
            # Caso contrário, trata como regressão
            tipo = "regressao"

    # Mostra no terminal o tipo de problema detectado
    print("🧠 Tipo de problema detectado:", tipo)


    # ===============================
    # PIPELINES DE PRÉ-PROCESSAMENTO
    # ===============================

    # Importa a classe Pipeline, usada para encadear etapas de pré-processamento
    from sklearn.pipeline import Pipeline

    # Importa o ColumnTransformer, que permite aplicar pipelines diferentes para tipos de colunas distintos
    from sklearn.compose import ColumnTransformer

    # Importa ferramentas de pré-processamento
    from sklearn.preprocessing import (
        StandardScaler,        # Padroniza dados numéricos (média 0, desvio padrão 1)
        OneHotEncoder,         # Converte categorias em colunas binárias
        PolynomialFeatures     # Cria interações/polinômios entre variáveis numéricas
    )

    # Importa o imputador para preenchimento de valores ausentes
    from sklearn.impute import SimpleImputer

    # Seleciona os nomes das colunas numéricas (inteiros e floats)
    colunas_numericas = X.select_dtypes(include=["int64", "float64"]).columns

    # Seleciona os nomes das colunas categóricas (texto e booleanos)
    colunas_categoricas = X.select_dtypes(include=["object", "bool"]).columns

    # ===============================
    # PIPELINE PARA COLUNAS NUMÉRICAS
    # ===============================

    pipeline_numerico = Pipeline(steps=[
        # Preenche valores ausentes usando a mediana da coluna
        ("preencher", SimpleImputer(strategy="median")),

        # Padroniza os valores numéricos
        ("escalar", StandardScaler()),

        # Cria variáveis de interação entre features (ex: x1*x2)
        # degree=2 → apenas interações de grau 2
        # include_bias=False → não adiciona coluna de bias (1s)
        # interaction_only=True → não cria x², apenas x1*x2
        ("polinomio", PolynomialFeatures(
            degree=2,
            include_bias=False,
            interaction_only=True
        ))
    ])

    # ===============================
    # PIPELINE PARA COLUNAS CATEGÓRICAS
    # ===============================

    pipeline_categorico = Pipeline(steps=[
        # Preenche valores ausentes com o valor mais frequente da coluna
        ("preencher", SimpleImputer(strategy="most_frequent")),

        # Converte categorias em variáveis binárias (one-hot encoding)
        # handle_unknown="ignore" evita erro com categorias novas no teste
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    # ===============================
    # COMBINA PIPELINES
    # ===============================

    pre_processador = ColumnTransformer(transformers=[
        # Aplica o pipeline numérico apenas nas colunas numéricas
        ("num", pipeline_numerico, colunas_numericas),

        # Aplica o pipeline categórico apenas nas colunas categóricas
        ("cat", pipeline_categorico, colunas_categoricas)
    ])

    # ===============================
    # MODELOS
    # ===============================

    # Importa função para validação cruzada
    from sklearn.model_selection import cross_val_score

    # ===============================
    # MODELOS DE CLASSIFICAÇÃO
    # ===============================

    # Florestas aleatórias para classificação
    from sklearn.ensemble import (
        RandomForestClassifier,      # Ensemble robusto baseado em árvores
        GradientBoostingClassifier,  # Boosting sequencial focado em erros
        ExtraTreesClassifier         # Árvores extremamente aleatórias
    )

    # Regressão logística (classificação linear)
    from sklearn.linear_model import LogisticRegression

    # Máquina de vetores de suporte para classificação
    from sklearn.svm import SVC

    # Classificador baseado em vizinhos mais próximos
    from sklearn.neighbors import KNeighborsClassifier

    # Classificador probabilístico baseado no teorema de Bayes
    from sklearn.naive_bayes import GaussianNB

    # Árvore de decisão simples para classificação
    from sklearn.tree import DecisionTreeClassifier

    # ===============================
    # MODELOS DE REGRESSÃO
    # ===============================

    # Florestas e boosting para regressão
    from sklearn.ensemble import (
        RandomForestRegressor,       # Random Forest para regressão
        GradientBoostingRegressor,   # Gradient Boosting para regressão
        ExtraTreesRegressor          # Extra Trees para regressão
    )

    # Modelos lineares para regressão
    from sklearn.linear_model import (
        LinearRegression,  # Regressão linear simples
        Ridge,             # Regressão com regularização L2
        Lasso              # Regressão com regularização L1
    )

    # SVM para regressão
    from sklearn.svm import SVR

    # KNN para regressão
    from sklearn.neighbors import KNeighborsRegressor

    # Árvore de decisão para regressão
    from sklearn.tree import DecisionTreeRegressor


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

    # ===============================
    # TREINAMENTO
    # ===============================

    # Lista que armazenará o ranking dos modelos (nome + score)
    ranking = []

    # Dicionário para salvar os resultados de cada modelo (nome → score)
    resultados_dict = {}

    # Inicializa o melhor score com um valor bem baixo
    # Assim, qualquer modelo treinado tende a ser melhor
    melhor_score = -999999

    # Variável que armazenará o melhor pipeline (pré-processamento + modelo)
    melhor_modelo = None

    # Variável que armazenará o nome do melhor modelo
    melhor_nome = ""

    # Verifica se o dataset é pequeno (menos de 30 amostras)
    dataset_pequeno = len(X) < 30

    # Loop que percorre todos os modelos definidos anteriormente
    for nome, modelo in modelos.items():

        try:
            # Cria um pipeline completo unindo:
            # 1) pré-processamento dos dados
            # 2) modelo de machine learning
            pipeline_completo = Pipeline(steps=[
                ("preprocessamento", pre_processador),  # Limpeza e transformação dos dados
                ("modelo", modelo)                      # Algoritmo de ML
            ])

            # Se o dataset for pequeno
            if dataset_pequeno:
                # Treina o modelo usando todos os dados
                pipeline_completo.fit(X, y)

                # Calcula o score usando os próprios dados de treino
                # (evita erro de cross-validation com poucos dados)
                score = pipeline_completo.score(X, y)

            # Se o dataset não for pequeno
            else:
                # Executa validação cruzada com 5 folds
                scores = cross_val_score(
                    pipeline_completo,  # pipeline completo
                    X,                   # features
                    y,                   # target
                    cv=5                 # número de divisões
                )

                # Calcula a média dos scores dos folds
                score = scores.mean()

            # Garante que o score seja um número float padrão do Python
            score = float(score)

            # Adiciona o resultado ao ranking
            ranking.append((nome, score))

            # Salva o score do modelo no dicionário de resultados
            resultados_dict[nome] = score

            # Verifica se o modelo atual é melhor que o anterior
            if score > melhor_score:
                # Atualiza o melhor score
                melhor_score = score

                # Salva o pipeline completo como o melhor modelo
                melhor_modelo = pipeline_completo

                # Salva o nome do melhor modelo
                melhor_nome = nome

        # Caso algum modelo gere erro durante o treino ou avaliação
        except Exception as e:
            # Exibe o erro no terminal sem interromper o AutoML
            print(f"❌ Erro no modelo {nome}: {e}")


    # ===============================
    # GARANTE PASTA
    # ===============================

    # Cria a pasta do projeto, caso ela não exista
    # exist_ok=True evita erro se a pasta já existir
    os.makedirs(pasta_projeto, exist_ok=True)

    # ===============================
    # SALVA MODELO
    # ===============================

    # Salva o melhor pipeline (pré-processamento + modelo)
    # no formato .pkl dentro da pasta do projeto
    joblib.dump(
        melhor_modelo,
        os.path.join(pasta_projeto, "melhor_modelo.pkl")
    )

    # ===============================
    # SALVA DATASET
    # ===============================

    # Copia o arquivo CSV original para a pasta do projeto
    # garantindo rastreabilidade dos dados usados no treino
    shutil.copy(
        caminho_csv,
        os.path.join(pasta_projeto, "dataset.csv")
    )

    # ===============================
    # META.JSON
    # ===============================

    # Cria um dicionário com metadados do treinamento
    meta = {
        # Nome da versão do modelo (usa o nome da pasta do projeto)
        "versao": os.path.basename(pasta_projeto),

        # Data e hora do treinamento
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # Tipo de problema identificado (classificação ou regressão)
        "tipo_problema": tipo,

        # Nome do melhor modelo encontrado
        "melhor_modelo": melhor_nome,

        # Score do melhor modelo
        "melhor_score": float(melhor_score),

        # Scores de todos os modelos testados
        "metricas": resultados_dict,

        # Dimensão do dataset (linhas, colunas)
        "dataset_shape": list(df.shape),

        # Lista com os nomes das colunas do dataset
        "colunas": list(df.columns),

        # Nome do arquivo do dataset salvo
        "arquivo_dataset": "dataset.csv",

        # Campo livre para observações futuras
        "comentario": ""
    }

    # Abre (ou cria) o arquivo meta.json em modo escrita
    with open(
        os.path.join(pasta_projeto, "meta.json"),
        "w",
        encoding="utf-8"
    ) as f:

        # Salva o dicionário meta no arquivo JSON
        # indent=4 deixa o arquivo legível
        # ensure_ascii=False preserva acentos e caracteres especiais
        json.dump(meta, f, indent=4, ensure_ascii=False)


    # ===============================
    # RESULTADOS.JSON
    # ===============================

    # Cria um dicionário com o resumo final do treinamento
    resultados = {
        # Nome do melhor modelo encontrado
        "melhor_modelo": melhor_nome,

        # Score do melhor modelo
        "melhor_score": float(melhor_score),

        # Tipo de problema (classificação ou regressão)
        "tipo_problema": tipo,

        # Scores de todos os modelos testados
        "metricas_por_modelo": resultados_dict
    }

    # Abre (ou cria) o arquivo resultados.json para escrita
    with open(
        os.path.join(pasta_projeto, "resultados.json"),
        "w",
        encoding="utf-8"
    ) as f:
        # Salva o dicionário de resultados em formato JSON
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    # ===============================
    # RANKING
    # ===============================

    # Ordena o ranking pelo score (posição 1 da tupla), do maior para o menor
    ranking_ordenado = sorted(
        ranking,
        key=lambda x: x[1],  # x[1] representa o score
        reverse=True        # ordem decrescente
    )

    # Converte o ranking em um formato serializável (JSON-friendly)
    ranking_serializavel = [
        {
            "modelo": nome,          # Nome do modelo
            "score": float(score)    # Score convertido para float padrão
        }
        for nome, score in ranking_ordenado
    ]

    # Salva o ranking ordenado em ranking.json
    with open(
        os.path.join(pasta_projeto, "ranking.json"),
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(ranking_serializavel, f, indent=4, ensure_ascii=False)

    # ===============================
    # GRÁFICO
    # ===============================

    # Extrai apenas os nomes dos modelos, na ordem do ranking
    nomes = [x[0] for x in ranking_ordenado]

    # Extrai apenas os scores dos modelos, na mesma ordem
    scores = [x[1] for x in ranking_ordenado]

    # Importa matplotlib para geração do gráfico
    import matplotlib.pyplot as plt

    # Cria uma nova figura com tamanho definido
    plt.figure(figsize=(10, 6))

    # Cria um gráfico de barras horizontais (melhor visualização do ranking)
    plt.barh(nomes, scores)

    # Inverte o eixo Y para que o melhor modelo fique no topo
    plt.gca().invert_yaxis()

    # Define o título do gráfico
    plt.title("Ranking dos Modelos")

    # Ajusta automaticamente os espaçamentos do gráfico
    plt.tight_layout()

    # Salva o gráfico como imagem PNG na pasta do projeto
    plt.savefig(os.path.join(pasta_projeto, "ranking.png"))

    # Fecha a figura para liberar memória
    plt.close()

    # ===============================
    # RELATÓRIO TXT
    # ===============================

    # Define o caminho do arquivo de relatório em texto
    caminho_relatorio = os.path.join(pasta_projeto, "resultado.txt")

    # Abre (ou cria) o arquivo resultado.txt para escrita
    with open(caminho_relatorio, "w", encoding="utf-8") as f:

        # Escreve o tipo de problema identificado
        f.write(f"Tipo de problema: {tipo}\n\n")

        # Escreve o ranking completo (modelo + score)
        for nome, score in ranking_ordenado:
            f.write(f"{nome}: {score}\n")

        # Destaca o melhor modelo ao final do relatório
        f.write(f"\nMelhor modelo: {melhor_nome}\n")

        # Escreve o score do melhor modelo
        f.write(f"Score: {melhor_score}\n")


    # ===============================
    # PDF
    # ===============================

    # Importa a função gerar_pdf do módulo pdf_report
    # Essa função é responsável por criar um relatório em PDF
    from pdf_report import gerar_pdf

    # Chama a função que gera o PDF final do projeto
    gerar_pdf(
        # Caminho completo onde o arquivo PDF será salvo
        caminho_pdf=os.path.join(pasta_projeto, "relatorio.pdf"),

        # Texto do relatório:
        # lê o conteúdo do arquivo resultado.txt já gerado anteriormente
        texto=open(caminho_relatorio, encoding="utf-8").read(),

        # Caminho da imagem do ranking (gráfico PNG)
        imagem=os.path.join(pasta_projeto, "ranking.png")
    )

    # ===============================
    # RETORNO
    # ===============================

    # Retorna informações principais da execução da função:
    # - tipo: classificação ou regressão
    # - melhor_nome: nome do melhor modelo encontrado
    # - melhor_score: score do melhor modelo
    # - caminho_relatorio: caminho do relatório em texto (.txt)
    # - caminho do gráfico de ranking (.png)
    return (
        tipo,
        melhor_nome,
        melhor_score,
        caminho_relatorio,
        os.path.join(pasta_projeto, "ranking.png")
)

