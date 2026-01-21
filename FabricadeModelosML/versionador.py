import os
import json
import shutil
from datetime import datetime


# CONTROLE DE VERSÕES DE MODELOS


def proxima_versao(pasta_projeto):
    """
    Descobre qual é a próxima versão disponível: v1, v2, v3...
    """
    pasta_treinos = os.path.join(pasta_projeto, "treinos")

    if not os.path.exists(pasta_treinos):
        return "v1"

    versoes = [
        nome for nome in os.listdir(pasta_treinos)
        if nome.startswith("v") and os.path.isdir(os.path.join(pasta_treinos, nome))
    ]

    if not versoes:
        return "v1"

    numeros = []
    for v in versoes:
        try:
            numeros.append(int(v.replace("v", "")))
        except:
            pass

    if not numeros:
        return "v1"

    proximo = max(numeros) + 1
    return f"v{proximo}"


def criar_pasta_versao(pasta_projeto):
    """
    Cria a pasta da nova versão e retorna:
    - caminho da pasta
    - nome da versão (ex: v1, v2)
    """
    versao = proxima_versao(pasta_projeto)
    pasta_versao = os.path.join(pasta_projeto, "treinos", versao)
    os.makedirs(pasta_versao, exist_ok=True)
    return pasta_versao, versao



# HISTÓRICO DE VERSÕES


def listar_versoes(pasta_projeto):
    """
    Retorna uma lista com todas as versões e seus metadados.
    """
    pasta_treinos = os.path.join(pasta_projeto, "treinos")

    if not os.path.exists(pasta_treinos):
        return []

    versoes = []

    for v in sorted(os.listdir(pasta_treinos)):
        pasta_v = os.path.join(pasta_treinos, v)
        if not os.path.isdir(pasta_v):
            continue

        meta_path = os.path.join(pasta_v, "meta.json")

        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        else:
            meta = {
                "versao": v,
                "modelo": "desconhecido",
                "score": None,
                "data": None,
                "producao": False
            }

        versoes.append(meta)

    # Ordena por score (maior primeiro)
    versoes.sort(key=lambda x: (x["score"] is not None, x["score"]), reverse=True)

    return versoes



# MODELO EM PRODUÇÃO


def definir_como_producao(pasta_projeto, versao):
    """
    Marca uma versão como produção e copia o modelo para /producao
    """

    pasta_treinos = os.path.join(pasta_projeto, "treinos")
    pasta_producao = os.path.join(pasta_projeto, "producao")

    os.makedirs(pasta_producao, exist_ok=True)

    # Remove flag de produção de todos
    for v in os.listdir(pasta_treinos):
        meta_path = os.path.join(pasta_treinos, v, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)

            meta["producao"] = False

            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=4, ensure_ascii=False)

    # Marca a versão escolhida
    pasta_versao = os.path.join(pasta_treinos, versao)
    meta_path = os.path.join(pasta_versao, "meta.json")

    if not os.path.exists(meta_path):
        raise Exception("Versão não possui meta.json")

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    meta["producao"] = True

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # Copia o modelo para produção
    origem = os.path.join(pasta_versao, "modelo.pkl")
    destino = os.path.join(pasta_producao, "modelo.pkl")

    if not os.path.exists(origem):
        raise Exception("modelo.pkl não encontrado na versão")

    shutil.copy2(origem, destino)



# DADOS PARA GRÁFICOS


def dados_para_comparacao(pasta_projeto):
    """
    Retorna dados prontos para gráfico:
    [
      {"versao": "v1", "score": 0.87},
      {"versao": "v2", "score": 0.91}
    ]
    """
    versoes = listar_versoes(pasta_projeto)

    dados = []
    for v in versoes:
        if v["score"] is not None:
            dados.append({
                "versao": v["versao"],
                "score": v["score"]
            })

    return dados
