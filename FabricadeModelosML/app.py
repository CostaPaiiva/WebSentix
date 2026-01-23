import os
from version_manager import listar_versoes, marcar_como_producao, versao_em_producao
import sys
from version_manager import marcar_como_producao
import json
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

@app.route("/marcar_producao/<projeto>/<versao>")
def marcar_producao(projeto, versao):
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)

    marcar_como_producao(pasta_projeto, versao)

    # Volta para o dashboard da mesma versão
    return redirect(url_for("dashboard", projeto=projeto))

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
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    historico = []

    for v in sorted(os.listdir(pasta_treinos)):
        caminho_pasta = os.path.join(pasta_treinos, v)
        caminho_meta = os.path.join(caminho_pasta, "meta.json")
        caminho_coment = os.path.join(caminho_pasta, "comentario.txt")

        if os.path.exists(caminho_meta):
            with open(caminho_meta, encoding="utf-8") as f:
                meta = json.load(f)

            if os.path.exists(caminho_coment):
                with open(caminho_coment, encoding="utf-8") as f:
                    meta["comentario"] = f.read()
            else:
                meta["comentario"] = ""

            historico.append(meta)


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
