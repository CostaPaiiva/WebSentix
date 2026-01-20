# Carrega um modelo já treinado
# Recebe dados novos
# Aplica o mesmo pré-processamento automaticamente
# Faz previsões

# Importa a biblioteca pandas para manipulação de dados em DataFrames
import pandas as pd
# Importa a biblioteca joblib para carregar modelos treinados
import joblib


def prever(caminho_csv, caminho_modelo):
    # Carrega o arquivo CSV em um DataFrame do pandas
    df = pd.read_csv(caminho_csv)
    # Carrega o modelo treinado a partir do arquivo
    modelo = joblib.load(caminho_modelo)

    # Faz previsões usando o modelo carregado e o DataFrame de entrada
    preds = modelo.predict(df)
    # Adiciona as previsões como uma nova coluna ao DataFrame
    df["previsao"] = preds

    # Cria o nome do arquivo de saída, substituindo a extensão original
    saida = caminho_csv.replace(".csv", "_previsto.csv")
    # Salva o DataFrame com as previsões em um novo arquivo CSV, sem o índice
    df.to_csv(saida, index=False)

    # Retorna o caminho do arquivo de saída
    return saida
