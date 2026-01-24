def treinar_automl(caminho_csv, pasta_projeto):
    """
    Função principal que:
    - Lê o CSV
    - Descobre se é classificação ou regressão
    - Treina vários modelos automaticamente
    - Escolhe o melhor
    - Salva modelo, gráfico, relatórios, dataset e arquivos JSON
    """

    # ===============================
    # IMPORTA BIBLIOTECAS
    # ===============================
    import pandas as pd
    import os
    import joblib
    import json
    from datetime import datetime
    import matplotlib.pyplot as plt
    import shutil
    import matplotlib
    matplotlib.use("Agg")  # backend sem interface gráfica (corrige crash no Flask)

    # ===============================
    # LÊ CSV
    # ===============================
    df = pd.read_csv(caminho_csv)
    df = df.dropna(axis=1, how="all")

    print("📊 Dataset shape:", df.shape)
    print("📋 Colunas:", df.columns.tolist())

    # ===============================
    # SEPARA X e y
    # ===============================
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    mask = y.notna()
    X = X[mask]
    y = y[mask]

    # ===============================
    # DETECTA TIPO DE PROBLEMA
    # ===============================
    if y.dtype == "object":
        tipo = "classificacao"
        y = y.astype("category").cat.codes
    else:
        if y.nunique() <= 15:
            tipo = "classificacao"
            y = y.astype("category").cat.codes
        else:
            tipo = "regressao"

    print("🧠 Tipo de problema detectado:", tipo)

    # ===============================
    # PIPELINES DE PRÉ-PROCESSAMENTO
    # ===============================
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
    from sklearn.impute import SimpleImputer

    colunas_numericas = X.select_dtypes(include=["int64", "float64"]).columns
    colunas_categoricas = X.select_dtypes(include=["object", "bool"]).columns

    pipeline_numerico = Pipeline(steps=[
        ("preencher", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
        ("polinomio", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True))
    ])

    pipeline_categorico = Pipeline(steps=[
        ("preencher", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    pre_processador = ColumnTransformer(transformers=[
        ("num", pipeline_numerico, colunas_numericas),
        ("cat", pipeline_categorico, colunas_categoricas)
    ])

    # ===============================
    # MODELOS
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
    ranking = []
    resultados_dict = {}

    melhor_score = -999999
    melhor_modelo = None
    melhor_nome = ""

    dataset_pequeno = len(X) < 30

    for nome, modelo in modelos.items():
        try:
            pipeline_completo = Pipeline(steps=[
                ("preprocessamento", pre_processador),
                ("modelo", modelo)
            ])

            if dataset_pequeno:
                pipeline_completo.fit(X, y)
                score = pipeline_completo.score(X, y)
            else:
                scores = cross_val_score(pipeline_completo, X, y, cv=5)
                score = scores.mean()

            score = float(score)

            ranking.append((nome, score))
            resultados_dict[nome] = score

            if score > melhor_score:
                melhor_score = score
                melhor_modelo = pipeline_completo
                melhor_nome = nome

        except Exception as e:
            print(f"❌ Erro no modelo {nome}: {e}")

    # ===============================
    # GARANTE PASTA
    # ===============================
    os.makedirs(pasta_projeto, exist_ok=True)

    # ===============================
    # SALVA MODELO
    # ===============================
    joblib.dump(melhor_modelo, os.path.join(pasta_projeto, "melhor_modelo.pkl"))

    # ===============================
    # SALVA DATASET
    # ===============================
    shutil.copy(caminho_csv, os.path.join(pasta_projeto, "dataset.csv"))

    # ===============================
    # META.JSON
    # ===============================
    meta = {
        "versao": os.path.basename(pasta_projeto),
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_problema": tipo,
        "melhor_modelo": melhor_nome,
        "melhor_score": float(melhor_score),
        "metricas": resultados_dict,
        "dataset_shape": list(df.shape),
        "colunas": list(df.columns),
        "arquivo_dataset": "dataset.csv",
        "comentario": ""
    }

    with open(os.path.join(pasta_projeto, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # ===============================
    # RESULTADOS.JSON
    # ===============================
    resultados = {
        "melhor_modelo": melhor_nome,
        "melhor_score": float(melhor_score),
        "tipo_problema": tipo,
        "metricas_por_modelo": resultados_dict
    }

    with open(os.path.join(pasta_projeto, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    # ===============================
    # RANKING
    # ===============================
    ranking_ordenado = sorted(ranking, key=lambda x: x[1], reverse=True)

    ranking_serializavel = [
        {"modelo": nome, "score": float(score)}
        for nome, score in ranking_ordenado
    ]

    with open(os.path.join(pasta_projeto, "ranking.json"), "w", encoding="utf-8") as f:
        json.dump(ranking_serializavel, f, indent=4, ensure_ascii=False)

    # ===============================
    # GRÁFICO
    # ===============================
    nomes = [x[0] for x in ranking_ordenado]
    scores = [x[1] for x in ranking_ordenado]

    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.barh(nomes, scores)
    plt.gca().invert_yaxis()
    plt.title("Ranking dos Modelos")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_projeto, "ranking.png"))
    plt.close()

    # ===============================
    # RELATÓRIO TXT
    # ===============================
    caminho_relatorio = os.path.join(pasta_projeto, "resultado.txt")

    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        f.write(f"Tipo de problema: {tipo}\n\n")
        for nome, score in ranking_ordenado:
            f.write(f"{nome}: {score}\n")
        f.write(f"\nMelhor modelo: {melhor_nome}\n")
        f.write(f"Score: {melhor_score}\n")

    # ===============================
    # PDF
    # ===============================
    from pdf_report import gerar_pdf

    gerar_pdf(
        caminho_pdf=os.path.join(pasta_projeto, "relatorio.pdf"),
        texto=open(caminho_relatorio, encoding="utf-8").read(),
        imagem=os.path.join(pasta_projeto, "ranking.png")
    )

    # ===============================
    # RETORNO
    # ===============================
    return tipo, melhor_nome, melhor_score, caminho_relatorio, os.path.join(pasta_projeto, "ranking.png")
