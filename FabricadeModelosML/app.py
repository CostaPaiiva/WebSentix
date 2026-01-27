import os
from version_manager import listar_versoes, marcar_como_producao, versao_em_producao
import sys
from version_manager import marcar_como_producao
import json
from flask import send_from_directory
from flask import request, redirect, url_for
from version_manager import versao_em_producao
from flask import Flask, render_template, request, send_file, redirect, url_for

# =========================================================
# CONFIGURAÇÃO DE PATH PARA IMPORTS INTERNOS DO PROJETO
# =========================================================

# Adiciona a pasta atual ao path do Python para permitir imports locais
sys.path.append(os.path.dirname(__file__))

# =========================================================
# IMPORTS DOS MÓDULOS DO SEU PROJETO
# =========================================================

from versionador import criar_pasta_versao   # Cria versão do projeto
from automl_engine import treinar_automl     # Treina os modelos automaticamente
from predictor import prever                 # Faz previsões em novos dados
from pdf_report import gerar_pdf             # Gera o relatório em PDF

# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

UPLOAD_FOLDER = "uploads"    # Pasta onde os CSVs enviados são salvos
PROJECTS_FOLDER = "projects" # Pasta onde ficam todos os projetos

# Inicializa o Flask
app = Flask(__name__)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def listar_projetos():
    """
    Lista todas as pastas dentro de /projects
    Cada pasta é um projeto treinado
    """
    if not os.path.exists(PROJECTS_FOLDER):
        return []

    return [
        nome for nome in os.listdir(PROJECTS_FOLDER)
        if os.path.isdir(os.path.join(PROJECTS_FOLDER, nome))
    ]


def salvar_upload(file):
    """
    Salva o arquivo enviado pelo usuário na pasta uploads/
    Retorna o caminho completo do arquivo salvo
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    caminho = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(caminho)
    return caminho

# =========================================================
# ROTA PRINCIPAL - UPLOAD E TREINAMENTO
# =========================================================

@app.route("/", methods=["GET", "POST"])
def index():
    # Lista projetos já existentes
    projetos = listar_projetos()

    # Se o usuário enviou formulário
    if request.method == "POST":
        file = request.files.get("file")

        # Se não veio arquivo, retorna erro simples
        if not file:
            return "Nenhum arquivo enviado"

        # Salva o CSV enviado
        caminho_csv = salvar_upload(file)

        # Cria o nome do projeto baseado no nome do arquivo
        nome_projeto = file.filename.replace(".csv", "")

        # Cria a pasta do projeto
        pasta_projeto = os.path.join(PROJECTS_FOLDER, nome_projeto)

        # Cria uma nova versão dentro do projeto
        pasta_versao, versao = criar_pasta_versao(pasta_projeto)

        # Executa o AutoML
        tipo, melhor, score, relatorio_txt, grafico = treinar_automl(
            caminho_csv, pasta_versao
        )

        # Lê o relatório em texto
        with open(relatorio_txt, encoding="utf-8") as f:
            texto = f.read()

        # Gera o PDF
        caminho_pdf = os.path.join(pasta_versao, "relatorio.pdf")
        gerar_pdf(caminho_pdf, texto, grafico)

        # Redireciona para o dashboard do projeto
        return redirect(url_for("dashboard", projeto=nome_projeto))

    # Se for GET, apenas mostra a página inicial
    return render_template("index.html", projetos=projetos)
@app.route("/files/<projeto>/<versao>/<path:filename>")
def arquivos_projeto(projeto, versao, filename):
    import os

    pasta = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)

    if not os.path.exists(pasta):
        return "Pasta não encontrada", 404

    return send_from_directory(pasta, filename, as_attachment=False)

@app.route("/marcar_producao/<projeto>/<versao>")
def marcar_producao(projeto, versao):
    import os, json

    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)

    # Garante que a pasta existe
    os.makedirs(pasta_projeto, exist_ok=True)

    caminho = os.path.join(pasta_projeto, "producao.json")

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"versao": versao}, f, indent=4)

    print("✅ Produção marcada:", projeto, versao)

    # 🔁 VOLTA PARA A TELA DE DETALHES DA MESMA VERSÃO
    return redirect(url_for("ver_detalhes", projeto=projeto, versao=versao))

def obter_versao_producao(pasta_projeto):
    import os, json

    caminho = os.path.join(pasta_projeto, "producao.json")

    if not os.path.exists(caminho):
        return None

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return dados.get("versao")

@app.route("/historico/<projeto>")
def historico(projeto):
    pasta_projeto = os.path.join("projetos", projeto)

    versoes = listar_versoes(pasta_projeto)
    producao = versao_em_producao(pasta_projeto)

    return render_template(
        "historico.html",
        projeto=projeto,
        versoes=versoes,
        producao=producao
    )
@app.route("/timeline/<projeto>")
def timeline(projeto):
    import os, json

    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    if not os.path.exists(pasta_treinos):
        return f"Projeto {projeto} não encontrado", 404

    historico = []
    producao_atual = None

    print("📂 Lendo versões em:", pasta_treinos)
    print("📂 Conteúdo:", os.listdir(pasta_treinos))

    for versao in sorted(os.listdir(pasta_treinos)):
        pasta_versao = os.path.join(pasta_treinos, versao)
        meta_path = os.path.join(pasta_versao, "meta.json")

        if not os.path.exists(meta_path):
            print("⚠️ Sem meta.json em", pasta_versao)
            continue

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        item = {
            "versao": versao,
            "data": meta.get("data", ""),
            "comentario": meta.get("comentario", ""),
            "melhor_modelo": meta.get("melhor_modelo", ""),
            "melhor_score": meta.get("melhor_score"),
            "acc": meta.get("acc"),
            "f1": meta.get("f1"),
            "metricas": meta.get("metricas", {}),
            "em_producao": meta.get("producao", False)
        }

        if item["em_producao"]:
            producao_atual = versao

        historico.append(item)

    return render_template(
        "timeline.html",
        projeto=projeto,
        historico=historico,
        producao=producao_atual
    )


@app.route("/ver_detalhes/<projeto>/<versao>")
def ver_detalhes(projeto, versao):
    import os, json

    pasta_versao = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)

    if not os.path.exists(pasta_versao):
        return "Versão não encontrada", 404

    caminho_meta = os.path.join(pasta_versao, "meta.json")

    if not os.path.exists(caminho_meta):
        return "meta.json não encontrado", 404

    with open(caminho_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # =========================
    # Verifica se é produção
    # =========================
    caminho_producao = os.path.join(PROJECTS_FOLDER, projeto, "producao.json")

    em_producao = False
    if os.path.exists(caminho_producao):
        with open(caminho_producao, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if dados.get("versao") == versao:
                em_producao = True

    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    versao_producao = obter_versao_producao(pasta_projeto)

    return render_template(
        "detalhes_versao.html",
        projeto=projeto,
        versao=versao,
        meta=meta,
        versao_producao=versao_producao
    )

@app.route("/restaurar/<projeto>/<versao>")
def restaurar_versao(projeto, versao):
    import os
    from flask import redirect

    pasta_base = os.path.join(PROJECTS_FOLDER, projeto)

    if not os.path.exists(pasta_base):
        return "Projeto não encontrado", 404

    caminho_prod = os.path.join(pasta_base, "PRODUCAO.txt")

    # Se já for produção, não faz nada
    if os.path.exists(caminho_prod):
        with open(caminho_prod, "r", encoding="utf-8") as f:
            atual = f.read().strip()

        if atual == versao:
            print("⚠️ Esta versão já está em produção.")
            return redirect(f"/ver_detalhes/{projeto}/{versao}")

    # Grava nova produção
    with open(caminho_prod, "w", encoding="utf-8") as f:
        f.write(versao)

    print(f"🚀 Versão {versao} restaurada como produção em {projeto}")

    return redirect(f"/timeline/{projeto}")

@app.route("/editar_comentario/<projeto>/<versao>", methods=["GET", "POST"])
def editar_comentario(projeto, versao):
    import os, json

    pasta = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)
    meta_path = os.path.join(pasta, "meta.json")

    if not os.path.exists(meta_path):
        return f"meta.json não encontrado em {pasta}", 404

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    if request.method == "POST":
        comentario = request.form.get("comentario", "")
        meta["comentario"] = comentario

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)

        return redirect(url_for("timeline", projeto=projeto))

    comentario_atual = meta.get("comentario", "")

    return render_template(
        "editar_comentario.html",
        projeto=projeto,
        versao=versao,
        comentario=comentario_atual
    )


@app.route("/salvar_comentario/<projeto>/<versao>", methods=["POST"])
def salvar_comentario(projeto, versao):
    import os, json

    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    pasta_versao = os.path.join(pasta_projeto, versao)
    caminho_meta = os.path.join(pasta_versao, "meta.json")

    if not os.path.exists(caminho_meta):
        return "Meta.json não encontrado", 404

    # Lê meta.json atual
    with open(caminho_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Pega comentário do form
    comentario = request.form.get("comentario", "")

    # Salva no meta
    meta["comentario"] = comentario

    # Grava de volta
    with open(caminho_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # Volta pra timeline
    return redirect(url_for("timeline", projeto=projeto))

@app.route("/comparar/<projeto>/<v1>/<v2>")
def comparar_versoes(projeto, v1, v2):
    import os, json

    pasta_base = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    p1 = os.path.join(pasta_base, v1, "meta.json")
    p2 = os.path.join(pasta_base, v2, "meta.json")

    if not os.path.exists(p1) or not os.path.exists(p2):
        return "Uma das versões não existe", 404

    with open(p1, encoding="utf-8") as f:
        m1 = json.load(f)

    with open(p2, encoding="utf-8") as f:
        m2 = json.load(f)

    # Descobre produção
    producao = None
    caminho_prod = os.path.join(PROJECTS_FOLDER, projeto, "PRODUCAO.txt")
    if os.path.exists(caminho_prod):
        with open(caminho_prod, encoding="utf-8") as f:
            producao = f.read().strip()

    # Diferença de score
    try:
        diff = float(m2["melhor_score"]) - float(m1["melhor_score"])
    except:
        diff = None

    return render_template(
        "comparar_versoes.html",
        projeto=projeto,
        v1=v1,
        v2=v2,
        m1=m1,
        m2=m2,
        producao=producao,
        diff=diff
    )

@app.route("/comparar_duas/<projeto>")
@app.route("/comparar_duas/<projeto>/<v1>/<v2>")
def comparar_duas(projeto, v1=None, v2=None):
    import os, json

    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    pasta_treinos = os.path.join(pasta_projeto, "treinos")

    versoes = sorted(os.listdir(pasta_treinos)) if os.path.exists(pasta_treinos) else []

    def carregar_meta(v):
        caminho = os.path.join(pasta_treinos, v, "meta.json")
        if not os.path.exists(caminho):
            return None
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    # Se não veio pela URL, tenta pegar pelo form
    if v1 is None or v2 is None:
        selecionadas = request.args.getlist("versoes")
        if len(selecionadas) == 2:
            v1, v2 = selecionadas
        else:
            return render_template(
                "comparar_duas.html",
                projeto=projeto,
                versoes=versoes,
                v1=None,
                v2=None,
                meta1=None,
                meta2=None,
                vencedora=None,
                producao=obter_versao_producao(pasta_projeto)
            )

    meta1 = carregar_meta(v1)
    meta2 = carregar_meta(v2)

    if not meta1 or not meta2:
        return "Uma das versões não existe", 404

    # Decide vencedora
    if meta1["melhor_score"] > meta2["melhor_score"]:
        vencedora = v1
    else:
        vencedora = v2

    return render_template(
        "comparar_duas.html",
        projeto=projeto,
        versoes=versoes,
        v1=v1,
        v2=v2,
        meta1=meta1,
        meta2=meta2,
        vencedora=vencedora,
        producao=obter_versao_producao(pasta_projeto)
    )


    meta1_path = os.path.join(pasta_treinos, v1, "meta.json")
    meta2_path = os.path.join(pasta_treinos, v2, "meta.json")

    if not os.path.exists(meta1_path) or not os.path.exists(meta2_path):
        return "Uma das versões não possui meta.json", 404

    with open(meta1_path, "r", encoding="utf-8") as f:
        meta1 = json.load(f)

    with open(meta2_path, "r", encoding="utf-8") as f:
        meta2 = json.load(f)

    vencedora = None
    try:
        if meta1["melhor_score"] > meta2["melhor_score"]:
            vencedora = v1
        elif meta2["melhor_score"] > meta1["melhor_score"]:
            vencedora = v2
    except:
        pass

    return render_template(
        "comparar_duas.html",
        projeto=projeto,
        versoes=versoes,
        v1=v1,
        v2=v2,
        meta1=meta1,
        meta2=meta2,
        vencedora=vencedora,
        producao=obter_versao_producao(pasta_projeto)
    )


    # Agora carrega os meta.json
    meta1_path = os.path.join(pasta_treinos, v1, "meta.json")
    meta2_path = os.path.join(pasta_treinos, v2, "meta.json")

    if not os.path.exists(meta1_path) or not os.path.exists(meta2_path):
        return "Uma das versões não possui meta.json", 404

    with open(meta1_path, "r", encoding="utf-8") as f:
        meta1 = json.load(f)

    with open(meta2_path, "r", encoding="utf-8") as f:
        meta2 = json.load(f)

    # Decide vencedora
    vencedora = None
    try:
        if meta1["melhor_score"] > meta2["melhor_score"]:
            vencedora = v1
        elif meta2["melhor_score"] > meta1["melhor_score"]:
            vencedora = v2
    except:
        pass

    return render_template(
        "comparar_duas.html",
        projeto=projeto,
        versoes=versoes,
        v1=v1,
        v2=v2,
        meta1=meta1,
        meta2=meta2,
        vencedora=vencedora,
        producao=obter_versao_producao(pasta_projeto)
    )

    # Decide vencedora
    if meta1["melhor_score"] > meta2["melhor_score"]:
        vencedora = v1
    else:
        vencedora = v2

    # Lê produção atual
    producao = None
    caminho_prod = os.path.join(PROJECTS_FOLDER, projeto, "producao.json")
    if os.path.exists(caminho_prod):
        with open(caminho_prod, "r", encoding="utf-8") as f:
            producao = json.load(f).get("versao")

    # Lista versões para o select
    versoes = []
    for v in os.listdir(pasta_treinos):
        if os.path.exists(os.path.join(pasta_treinos, v, "meta.json")):
            versoes.append(v)

    versoes = sorted(versoes)

    return render_template(
        "comparar_duas.html",
        projeto=projeto,
        versoes=versoes,
        v1=v1,
        v2=v2,
        meta1=meta1,
        meta2=meta2,
        vencedora=vencedora,
        producao=producao
    )

@app.route("/promover_producao/<projeto>/<versao>")
def promover_producao(projeto, versao):
    import os

    pasta_base = os.path.join(PROJECTS_FOLDER, projeto)

    if not os.path.exists(pasta_base):
        return "Projeto não encontrado", 404

    caminho_prod = os.path.join(pasta_base, "PRODUCAO.txt")
    with open(caminho_prod, "w", encoding="utf-8") as f:
        f.write(versao)

    print(f"🏆 Versão {versao} promovida para produção em {projeto}")

    return redirect(f"/timeline/{projeto}")

@app.route("/comparar/<projeto>")
def comparar(projeto):
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    historico = []

    for v in sorted(os.listdir(pasta_treinos)):
        caminho_meta = os.path.join(pasta_treinos, v, "meta.json")

        if os.path.exists(caminho_meta):
            with open(caminho_meta, encoding="utf-8") as f:
                meta = json.load(f)
                historico.append(meta)

    return render_template("comparar_versoes.html", projeto=projeto, historico=historico)


# =========================================================
# DASHBOARD DO PROJETO
# =========================================================

@app.route("/dashboard/<projeto>")
def dashboard(projeto):
    # =====================================================
    # LOCALIZA A ÚLTIMA VERSÃO DO PROJETO
    # =====================================================

    # Pasta onde ficam os treinos do projeto
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    # Lista as versões existentes e pega a última
    versoes = sorted(os.listdir(pasta_treinos))
    ultima_versao = versoes[-1]

    # Caminho completo da última versão
    pasta = os.path.join(pasta_treinos, ultima_versao)

    # Caminhos dos arquivos principais gerados no treino
    caminho_relatorio = os.path.join(pasta, "resultado.txt")
    caminho_grafico = os.path.join(pasta, "ranking.png")
    caminho_meta = os.path.join(pasta, "meta.json")

    # =====================================================
    # LÊ O META.JSON (SE EXISTIR)
    # =====================================================

    meta = {}

    if os.path.exists(caminho_meta):
        with open(caminho_meta, encoding="utf-8") as f:
            meta = json.load(f)

    # =====================================================
    # LÊ O RESULTADO.TXT E EXTRAI OS SCORES DOS MODELOS
    # =====================================================

    resultados_dict = {}  # Formato final: { "Modelo": score }

    with open(caminho_relatorio, encoding="utf-8") as f:
        for linha in f:
            # Só processa linhas no formato: Modelo: score
            if ":" in linha:
                nome, score_txt = linha.split(":", 1)

                try:
                    score = float(score_txt.strip())
                    resultados_dict[nome.strip()] = score
                except:
                    # Ignora linhas que não são números
                    pass

    # =====================================================
    # DESCOBRE AUTOMATICAMENTE O MELHOR MODELO
    # =====================================================

    melhor_modelo_auto = "N/A"
    melhor_score_auto = "N/A"

    if len(resultados_dict) > 0:
        melhor_modelo_auto = max(resultados_dict, key=resultados_dict.get)
        melhor_score_auto = resultados_dict[melhor_modelo_auto]

    # =====================================================
    # DEFINE TIPO DE PROBLEMA (META OU FALLBACK)
    # =====================================================

    tipo_problema = meta.get("tipo_problema")

    if not tipo_problema:
        # Heurística simples (depois podemos melhorar)
        tipo_problema = "Regressão"

    # =====================================================
    # LÊ O TEXTO COMPLETO DO RELATÓRIO (SE QUISER MOSTRAR)
    # =====================================================

    with open(caminho_relatorio, encoding="utf-8") as f:
        texto = f.read()

    # =====================================================
    # DECIDE SE USA O META.JSON OU O CÁLCULO AUTOMÁTICO
    # =====================================================

    melhor_modelo = meta.get("melhor_modelo", melhor_modelo_auto)
    melhor_score = meta.get("melhor_score", melhor_score_auto)

    # =====================================================
    # ORDENA RESULTADOS DO MELHOR PARA O PIOR (PARA RANKING)
    # =====================================================

    resultados_ordenados = dict(
        sorted(resultados_dict.items(), key=lambda x: x[1], reverse=True)
    )
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    versao_producao = versao_em_producao(pasta_projeto)

    em_producao = (ultima_versao == versao_producao)

    # =====================================================
    # RENDERIZA O DASHBOARD
    # =====================================================

    return render_template(
        "dashboard.html",

        # Info do projeto
        projeto=projeto,
        versao=ultima_versao,

        versao_producao=versao_producao,
        em_producao=em_producao,

        # Texto completo do relatório
        texto=texto,

        # Caminho do gráfico (ajustado pra URL)
        grafico="/" + caminho_grafico.replace("\\", "/"),

        # Meta completo (se quiser usar no HTML depois)
        meta=meta,

        # Dados principais pro dashboard
        resultados=resultados_ordenados,
        tipo_problema=tipo_problema,
        melhor_modelo=melhor_modelo,
        melhor_score=melhor_score,
    )

# =========================================================
# DOWNLOAD DO PDF
# =========================================================

@app.route("/baixar_pdf/<projeto>")
def baixar_pdf(projeto):
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")
    versoes = sorted(os.listdir(pasta_treinos))
    ultima = versoes[-1]
    caminho = os.path.join(pasta_treinos, ultima, "relatorio.pdf")
    return send_file(caminho, as_attachment=True)

# =========================================================
# PÁGINA DE PREVISÃO
# =========================================================

@app.route("/prever", methods=["GET", "POST"])
def pagina_prever():
    projetos = listar_projetos()

    if request.method == "POST":
        file = request.files.get("file")
        projeto = request.form.get("projeto")

        if not file or not projeto:
            return "Arquivo ou projeto não selecionado"

        caminho_csv = salvar_upload(file)

        # Caminho do modelo treinado
        modelo = os.path.join(PROJECTS_FOLDER, projeto, "modelo.pkl")

        # Executa a previsão
        saida = prever(caminho_csv, modelo)

        # Retorna o arquivo gerado
        return send_file(saida, as_attachment=True)

    return render_template("prever.html", projetos=projetos)

# =========================================================
# GERENCIAR VERSÕES
# =========================================================

@app.route("/versoes/<projeto>")
def gerenciar_versoes(projeto):
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")
    versoes = []

    for v in sorted(os.listdir(pasta_treinos)):
        caminho_meta = os.path.join(pasta_treinos, v, "meta.json")
        if os.path.exists(caminho_meta):
            with open(caminho_meta, encoding="utf-8") as f:
                meta = json.load(f)
                versoes.append(meta)

    return render_template("versoes.html", projeto=projeto, versoes=versoes)

# =========================================================
# LISTAGEM DE PROJETOS
# =========================================================

@app.route("/projetos")
def historico_projetos():
    projetos = listar_projetos()
    return render_template("projetos.html", projetos=projetos)

# =========================================================
# INICIALIZAÇÃO DO SERVIDOR
# =========================================================

if __name__ == "__main__":
    # Garante que as pastas principais existam
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROJECTS_FOLDER, exist_ok=True)

    # Inicia o servidor Flask em modo debug
    app.run(debug=True)
