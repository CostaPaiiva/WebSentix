import os
import sys
import json
from flask import Flask, render_template, request, send_file, redirect, url_for

# Adiciona pasta atual ao path para imports internos
sys.path.append(os.path.dirname(__file__))

# Funções do seu projeto
from versionador import criar_pasta_versao
from automl_engine import treinar_automl
from predictor import prever
from pdf_report import gerar_pdf

# Configurações
UPLOAD_FOLDER = "uploads"
PROJECTS_FOLDER = "projects"

# Inicializa Flask
app = Flask(__name__)

# ---------- Funções auxiliares ----------

def listar_projetos():
    """Lista as pastas de projetos existentes."""
    if not os.path.exists(PROJECTS_FOLDER):
        return []
    return [nome for nome in os.listdir(PROJECTS_FOLDER)
            if os.path.isdir(os.path.join(PROJECTS_FOLDER, nome))]

def salvar_upload(file):
    """Salva arquivo enviado pelo usuário na pasta uploads/."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    caminho = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(caminho)
    return caminho

# ---------- Rotas ----------

@app.route("/", methods=["GET", "POST"])
def index():
    projetos = listar_projetos()

    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "Nenhum arquivo enviado"

        # Salvar CSV
        caminho_csv = salvar_upload(file)

        # Criar pasta do projeto
        nome_projeto = file.filename.replace(".csv", "")
        pasta_projeto = os.path.join(PROJECTS_FOLDER, nome_projeto)
        pasta_versao, versao = criar_pasta_versao(pasta_projeto)

        # Treinar AutoML
        tipo, melhor, score, relatorio_txt, grafico = treinar_automl(
            caminho_csv, pasta_versao
        )

        # Ler relatório em texto
        with open(relatorio_txt, encoding="utf-8") as f:
            texto = f.read()

        # Gerar PDF
        caminho_pdf = os.path.join(pasta_versao, "relatorio.pdf")
        gerar_pdf(caminho_pdf, texto, grafico)

        # Redirecionar para dashboard
        return redirect(url_for("dashboard", projeto=nome_projeto))

    return render_template("index.html", projetos=projetos)

@app.route("/dashboard/<projeto>")
def dashboard(projeto):
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")
    versoes = sorted(os.listdir(pasta_treinos))
    ultima_versao = versoes[-1]
    pasta = os.path.join(pasta_treinos, ultima_versao)

    caminho_relatorio = os.path.join(pasta, "resultado.txt")
    caminho_grafico = os.path.join(pasta, "ranking.png")
    caminho_meta = os.path.join(pasta, "meta.json")

    # Ler relatório e extrair resultados
    resultados = []
    with open(caminho_relatorio, encoding="utf-8") as f:
        for linha in f:
            if ":" in linha:
                nome, score = linha.split(":")
                try:
                    valor = float(score.strip())
                    resultados.append((nome.strip(), valor))
                except ValueError:
                    continue

    with open(caminho_relatorio, encoding="utf-8") as f:
        texto = f.read()

    with open(caminho_meta, encoding="utf-8") as f:
        meta = json.load(f)

    return render_template(
        "dashboard.html",
        projeto=projeto,
        versao=ultima_versao,
        texto=texto,
        grafico="/" + caminho_grafico.replace("\\", "/"),
        meta=meta,
        resultados=resultados
    )

@app.route("/baixar_pdf/<projeto>")
def baixar_pdf(projeto):
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")
    versoes = sorted(os.listdir(pasta_treinos))
    ultima = versoes[-1]
    caminho = os.path.join(pasta_treinos, ultima, "relatorio.pdf")
    return send_file(caminho, as_attachment=True)

@app.route("/prever", methods=["GET", "POST"])
def pagina_prever():
    projetos = listar_projetos()
    if request.method == "POST":
        file = request.files.get("file")
        projeto = request.form.get("projeto")

        if not file or not projeto:
            return "Arquivo ou projeto não selecionado"

        caminho_csv = salvar_upload(file)
        modelo = os.path.join(PROJECTS_FOLDER, projeto, "modelo.pkl")
        saida = prever(caminho_csv, modelo)

        return send_file(saida, as_attachment=True)

    return render_template("prever.html", projetos=projetos)

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

@app.route("/projetos")
def historico_projetos():
    projetos = listar_projetos()
    return render_template("projetos.html", projetos=projetos)

@app.route("/comparar/<projeto>")
def comparar(projeto):
    pasta = os.path.join(PROJECTS_FOLDER, projeto)
    caminho = os.path.join(pasta, "resultado.txt")
    resultados = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if ":" in linha:
                nome, score = linha.split(":")
                resultados.append((nome.strip(), float(score.strip())))

    nomes = [r[0] for r in resultados]
    scores = [r[1] for r in resultados]

    return render_template(
        "comparar.html",
        projeto=projeto,
        resultados=resultados,
        nomes=nomes,
        scores=scores
    )

# ---------- Inicialização ----------
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROJECTS_FOLDER, exist_ok=True)
    app.run(debug=True)
