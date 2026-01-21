import os  # Biblioteca para lidar com pastas e arquivos do sistema

def proxima_versao(pasta_projeto):
    """
    Descobre qual é a próxima versão disponível: v1, v2, v3...
    """

    # Pasta onde ficarão todas as versões do projeto
    pasta_treinos = os.path.join(pasta_projeto, "treinos")

    # Se a pasta ainda não existir, então a primeira versão será v1
    if not os.path.exists(pasta_treinos):
        return "v1"

    # Lista todas as pastas dentro de /treinos que começam com "v"
    versoes = [
        nome for nome in os.listdir(pasta_treinos)
        if nome.startswith("v")
    ]

    # Se ainda não existe nenhuma versão, começa pela v1
    if not versoes:
        return "v1"

    # Pega apenas o número das versões:
    # Ex: "v3" vira 3
    numeros = [int(v.replace("v", "")) for v in versoes]

    # Descobre qual é o maior número e soma +1
    proximo = max(numeros) + 1

    # Retorna no formato: v4, v5, etc
    return f"v{proximo}"


def criar_pasta_versao(pasta_projeto):
    """
    Cria a pasta da nova versão e retorna:
    - o caminho da pasta
    - o nome da versão (ex: v1, v2)
    """

    # Descobre qual será a próxima versão
    versao = proxima_versao(pasta_projeto)

    # Monta o caminho completo:
    # projects/iris/treinos/v1
    pasta_versao = os.path.join(pasta_projeto, "treinos", versao)

    # Cria a pasta no disco (se não existir)
    os.makedirs(pasta_versao, exist_ok=True)

    # Retorna:
    # - o caminho da pasta criada
    # - o nome da versão
    return pasta_versao, versao
