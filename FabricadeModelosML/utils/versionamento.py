import os
import json

def listar_versoes(pasta_treinos):
    versoes = []

    if not os.path.exists(pasta_treinos):
        return versoes

    for nome_pasta in os.listdir(pasta_treinos):
        caminho = os.path.join(pasta_treinos, nome_pasta)

        if os.path.isdir(caminho):
            meta_path = os.path.join(caminho, "meta.json")

            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    versoes.append(meta)

    # Ordena por score (maior primeiro)
    versoes.sort(key=lambda x: x["score"], reverse=True)

    return versoes
