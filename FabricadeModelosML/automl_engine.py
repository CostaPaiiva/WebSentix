def treinar_automl(caminho_csv, pasta_projeto):
    """
    Função principal que:
    - Lê o CSV
    - Descobre se é classificação ou regressão
    - Treina vários modelos automaticamente
    - Escolhe o melhor
    - Salva modelo, gráfico, relatório e meta.json
    """

    # ===============================
    # IMPORTA BIBLIOTECAS NECESSÁRIAS
    # ===============================

    import pandas as pd               # Para ler e manipular dados
    import os                         # Para criar pastas e caminhos
    import joblib                     # Para salvar o modelo treinado
    import json                       # Para salvar o meta.json
    from datetime import datetime     # Para salvar data e hora
    import matplotlib.pyplot as plt   # Para gerar gráfico

    # ===============================
    # LÊ O CSV
    # ===============================

    df = pd.read_csv(caminho_csv)     # Lê o arquivo CSV para um DataFrame

    # Remove colunas 100% vazias
    df = df.dropna(axis=1, how="all")

    print("📊 Dataset shape:", df.shape)
    print("📋 Colunas:", df.columns.tolist())

    # ===============================
    # SEPARA X (entradas) e y (alvo)
    # ===============================

    X = df.iloc[:, :-1]   # Todas as colunas menos a última
    y = df.iloc[:, -1]    # Última coluna (alvo)

    # Remove linhas onde o alvo está vazio
    mask = y.notna()
    X = X[mask]
    y = y[mask]

    print("🎯 Alvo valores únicos:", y.nunique())
    print("🔎 Tipo do alvo:", y.dtype)

    # ===============================
    # DETECTA AUTOMATICAMENTE O TIPO
    # ===============================

    # Se o alvo é texto → com certeza é classificação
    if y.dtype == "object":
        tipo = "classificacao"
        y = y.astype("category").cat.codes  # Converte classes para números

    # Se for número:
    else:
        # Se tem poucos valores únicos → provavelmente classificação
        if y.nunique() <= 15:
            tipo = "classificacao"
        else:
            tipo = "regressao"

    print("🤖 Tipo de problema detectado:", tipo)

    # ===============================
    # DETECTA COLUNAS NUMÉRICAS E TEXTO
    # ===============================

    colunas_numericas = X.select_dtypes(include=["int64", "float64"]).columns
    colunas_categoricas = X.select_dtypes(include=["object", "bool"]).columns

    # ===============================
    # CRIA PIPELINES DE PRÉ-PROCESSAMENTO
    # ===============================

    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
    from sklearn.impute import SimpleImputer

    # Pipeline para números
    pipeline_numerico = Pipeline(steps=[
        ("preencher", SimpleImputer(strategy="median")),      # Preenche vazios com mediana
        ("escalar", StandardScaler()),                         # Normaliza os números
        ("polinomio", PolynomialFeatures(                      # Cria novas features
            degree=2, include_bias=False, interaction_only=True
        ))
    ])

    # Pipeline para texto
    pipeline_categorico = Pipeline(steps=[
        ("preencher", SimpleImputer(strategy="most_frequent")),  # Preenche vazios
        ("onehot", OneHotEncoder(handle_unknown="ignore"))       # Converte texto em números
    ])

    # Junta tudo em um só pré-processador
    pre_processador = ColumnTransformer(transformers=[
        ("num", pipeline_numerico, colunas_numericas),
        ("cat", pipeline_categorico, colunas_categoricas)
    ])

    # ===============================
    # IMPORTA MODELOS
    # ===============================

    from sklearn.model_selection import cross_val_score

    # Classificação
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.naive_bayes import GaussianNB
    from sklearn.tree import DecisionTreeClassifier

    # Regressão
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.tree import DecisionTreeRegressor

    # ===============================
    # ESCOLHE OS MODELOS PELO TIPO
    # ===============================

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
    # TREINA E TESTA TODOS
    # ===============================

    ranking = []                 # Guarda (nome, score)
    melhor_score = -999999       # Guarda o melhor score encontrado
    melhor_modelo = None         # Guarda o pipeline completo do melhor modelo
    melhor_nome = ""             # Nome do melhor modelo

    dataset_pequeno = len(X) < 30

    for nome, modelo in modelos.items():
        try:
            # Cria pipeline completo: preprocessamento + modelo
            pipeline_completo = Pipeline(steps=[
                ("preprocessamento", pre_processador),
                ("modelo", modelo)
            ])

            # Se dataset pequeno, treina e testa no próprio
            if dataset_pequeno:
                pipeline_completo.fit(X, y)
                score = pipeline_completo.score(X, y)
            else:
                scores = cross_val_score(pipeline_completo, X, y, cv=5)
                score = scores.mean()

            # Salva no ranking
            ranking.append((nome, float(score)))

            # Atualiza o melhor
            if score > melhor_score:
                melhor_score = score
                melhor_modelo = pipeline_completo
                melhor_nome = nome

        except Exception as e:
            print(f"❌ Erro no modelo {nome}: {e}")

    # ===============================
    # CRIA A PASTA DA VERSÃO
    # ===============================

    os.makedirs(pasta_projeto, exist_ok=True)

    # ===============================
    # SALVA O MELHOR MODELO
    # ===============================

    caminho_modelo = os.path.join(pasta_projeto, "modelo.pkl")
    joblib.dump(melhor_modelo, caminho_modelo)

    # ===============================
    # SALVA META.JSON (PARA COMPARAR VERSÕES)
    # ===============================

    meta = {
        "versao": os.path.basename(pasta_projeto),
        "tipo_problema": tipo,
        "melhor_modelo": melhor_nome,
        "score": float(melhor_score),
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_shape": df.shape,
        "colunas": list(df.columns),
        "ranking": ranking,
        "producao": False
    }

    caminho_meta = os.path.join(pasta_projeto, "meta.json")

    with open(caminho_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # ===============================
    # GERA GRÁFICO DO RANKING
    # ===============================

    nomes = [x[0] for x in ranking]
    scores = [x[1] for x in ranking]

    plt.figure(figsize=(10, 6))
    plt.barh(nomes, scores)
    plt.title("Ranking dos Modelos")
    plt.tight_layout()

    caminho_grafico = os.path.join(pasta_projeto, "ranking.png")
    plt.savefig(caminho_grafico)
    plt.close()

    # ===============================
    # GERA RELATÓRIO TXT
    # ===============================

    caminho_relatorio = os.path.join(pasta_projeto, "resultado.txt")

    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        f.write(f"Tipo de problema: {tipo}\n\n")

        for nome, score in ranking:
            f.write(f"{nome}: {score}\n")

        f.write(f"\nMelhor modelo: {melhor_nome}\n")
        f.write(f"Score: {melhor_score}\n")

    # ===============================
    # GERA PDF
    # ===============================

    from pdf_report import gerar_pdf

    caminho_pdf = os.path.join(pasta_projeto, "relatorio.pdf")

    gerar_pdf(
        caminho_pdf=caminho_pdf,
        texto=open(caminho_relatorio, encoding="utf-8").read(),
        imagem=caminho_grafico
    )

    # ===============================
    # RETORNA PARA O FLASK
    # ===============================

    return tipo, melhor_nome, melhor_score, caminho_relatorio, caminho_grafico
