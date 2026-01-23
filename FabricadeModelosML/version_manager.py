import os
import json

def listar_versoes(pasta_projeto):
    """
    Lê todas as pastas v1, v2, v3...
    e retorna os meta.json de cada versão
    """

    versoes = []

    # Percorre todas as subpastas
    for nome in os.listdir(pasta_projeto):
        caminho = os.path.join(pasta_projeto, nome)

        # Só entra se for pasta de versão
        if os.path.isdir(caminho) and nome.lower().startswith("v"):
            caminho_meta = os.path.join(caminho, "meta.json")

            # Só entra se existir meta.json
            if os.path.exists(caminho_meta):
                with open(caminho_meta, encoding="utf-8") as f:
                    meta = json.load(f)

                    # Guarda também o nome da pasta
                    meta["pasta"] = nome

                    versoes.append(meta)

    # Ordena por data
    versoes.sort(key=lambda x: x["data"])

    return versoes

def marcar_como_producao(pasta_projeto, versao):
    """
    Marca uma versão como sendo a versão em produção
    """

    caminho = os.path.join(pasta_projeto, "producao.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(versao)

def versao_em_producao(pasta_projeto):
    """
    Retorna qual versão está em produção
    """

    caminho = os.path.join(pasta_projeto, "producao.txt")

    if not os.path.exists(caminho):
        return None

    return open(caminho, encoding="utf-8").read().strip()

import os

# Retorna a lista de versões do projeto
def listar_versoes(pasta_projeto):
    pasta_treinos = os.path.join(pasta_projeto, "treinos")
    if not os.path.exists(pasta_treinos):
        return []

    versoes = sorted(os.listdir(pasta_treinos))
    return versoes

# Marca uma versão como produção
def marcar_como_producao(pasta_projeto, versao):
    caminho = os.path.join(pasta_projeto, "producao.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(versao)

# Retorna qual versão está em produção
def versao_em_producao(pasta_projeto):
    caminho = os.path.join(pasta_projeto, "producao.txt")

    if not os.path.exists(caminho):
        return None

    with open(caminho, "r", encoding="utf-8") as f:
        return f.read().strip()
