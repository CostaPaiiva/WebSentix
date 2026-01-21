# Inicia o site
# Cria as páginas (rotas)
# Recebe arquivos do usuário
# Chama o AutoML
# Mostra resultados
# Gera PDF
# Faz previsões

# Importa a classe principal do Flask e algumas funções auxiliares
from flask import Flask, render_template, request, send_file, redirect, url_for
# Importa o módulo 'os' para manipulação de caminhos e arquivos no sistema operacional
import os
# Importa funções específicas de módulos internos do projeto:
# treinar_automl: provavelmente responsável por treinar um modelo de Machine Learning automático
from automl_engine import treinar_automl
# prever: função para realizar previsões usando o modelo treinado
from predictor import prever
# gerar_pdf: função para gerar relatórios em PDF com os resultados
from pdf_report import gerar_pdf

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Define a pasta para uploads de arquivos
UPLOAD_FOLDER = "uploads"
# Define a pasta para armazenar projetos de modelos
PROJECTS_FOLDER = "projects"

# Funções auxiliares

def salvar_upload(file):
    # Monta o caminho completo onde o arquivo será salvo
    caminho = os.path.join(UPLOAD_FOLDER, file.filename)

    # Salva fisicamente o arquivo enviado pelo usuário nesse caminho
    file.save(caminho)

    # Retorna o caminho completo do arquivo salvo
    # Isso permite que outras partes do sistema usem esse arquivo
    return caminho

# Rotas

# Cria a rota da página inicial do site
# Essa página aceita:
# - GET: quando o usuário apenas abre o site
# - POST: quando o usuário envia um arquivo CSV pelo formulário
@app.route("/", methods=["GET", "POST"])
def index():
    # Busca a lista de projetos já criados na pasta projects/
    projetos = listar_projetos()

    # Verifica se o usuário enviou o formulário (upload do CSV)
    if request.method == "POST":
        # Pega o arquivo enviado pelo formulário HTML
        file = request.files["file"]

        # Se nenhum arquivo foi enviado, retorna uma mensagem de erro
        if not file:
            return "Nenhum arquivo enviado"

        # ============================
        # SALVAR O ARQUIVO CSV
        # ============================

        # Salva o arquivo CSV na pasta uploads/
        # e guarda o caminho completo dele na variável caminho_csv
        caminho_csv = salvar_upload(file)

        # ============================
        # CRIAR NOME DO PROJETO
        # ============================

        # Usa o nome do arquivo (sem a extensão .csv) como nome do projeto
        nome_projeto = file.filename.replace(".csv", "")

        # Cria o caminho da pasta do projeto dentro de projects/
        # Exemplo: projects/vendas_2024
        pasta_projeto = os.path.join(PROJECTS_FOLDER, nome_projeto)

        # TREINAR AUTOML
        # Chama a função principal do AutoML que:
        # - Analisa os dados
        # - Detecta o tipo de problema
        # - Treina vários modelos
        # - Escolhe o melhor modelo
        # - Gera relatório e gráfico
        tipo, melhor, score, relatorio_txt, grafico = treinar_automl(
            caminho_csv,       # caminho do CSV enviado pelo usuário
            pasta_projeto      # pasta onde os resultados serão salvos
        )

        # LER RELATÓRIO EM TEXTO
        # Abre o arquivo de relatório .txt que foi gerado pelo AutoML
        with open(relatorio_txt, encoding="utf-8") as f:
            # Lê todo o conteúdo do arquivo e guarda na variável texto
            texto = f.read()

        # GERAR PDF
        # Define o caminho onde o PDF será salvo dentro da pasta do projeto
        caminho_pdf = os.path.join(pasta_projeto, "relatorio.pdf")

        # Gera o arquivo PDF usando o texto do relatório e o gráfico
        gerar_pdf(caminho_pdf, texto, grafico)

        # REDIRECIONAR PARA DASHBOARD
        # Depois que todo o processamento termina,
        # redireciona o usuário para a página de resultados do projeto
        return redirect(url_for("dashboard", projeto=nome_projeto))

    # Se o usuário apenas entrou no site (GET),
    # mostra a página inicial com a lista de projetos existentes
    return render_template("index.html", projetos=projetos)


# Cria a rota da página de resultados do projeto
# <projeto> é um parâmetro dinâmico da URL
# Exemplo: /dashboard/vendas_2024
@app.route("/dashboard/<projeto>")
def dashboard(projeto):
    # Monta o caminho da pasta do projeto dentro de projects/
    # Exemplo: projects/vendas_2024
    pasta = os.path.join(PROJECTS_FOLDER, projeto)

    # Abre o arquivo resultado.txt que foi gerado durante o treinamento
    # Esse arquivo contém o resumo dos resultados dos modelos
    with open(os.path.join(pasta, "resultado.txt"), encoding="utf-8") as f:
        # Lê todo o conteúdo do arquivo e guarda na variável texto
        texto = f.read()

    # Define o caminho da imagem do ranking dos modelos
    # Essa imagem mostra a comparação entre os modelos treinados
    grafico = f"/{pasta}/ranking.png"

    # Renderiza a página dashboard.html passando:
    # - o nome do projeto
    # - o texto do relatório
    # - o caminho da imagem do gráfico
    return render_template(
        "dashboard.html",
        projeto=projeto,
        texto=texto,
        grafico=grafico
    )


# Cria a rota para baixar o relatório em PDF de um projeto específico
# <projeto> é o nome do projeto passado pela URL
# Exemplo: /baixar_pdf/vendas_2024
@app.route("/baixar_pdf/<projeto>")
def baixar_pdf(projeto):
    # Monta o caminho completo do arquivo PDF dentro da pasta do projeto
    # Exemplo: projects/vendas_2024/relatorio.pdf
    caminho = os.path.join(PROJECTS_FOLDER, projeto, "relatorio.pdf")

    # Envia o arquivo PDF para o navegador como download
    # as_attachment=True força o navegador a baixar o arquivo
    # ao invés de apenas abrir no próprio navegador
    return send_file(caminho, as_attachment=True)


@app.route("/prever", methods=["GET", "POST"])
def pagina_prever():
    projetos = listar_projetos()

    if request.method == "POST":
        file = request.files["file"]
        projeto = request.form["projeto"]

        # Salva CSV de entrada
        caminho_csv = salvar_upload(file)

        # Caminho do modelo treinado
        modelo = os.path.join(PROJECTS_FOLDER, projeto, "modelo.pkl")

        # Gera previsões
        saida = prever(caminho_csv, modelo)

        return send_file(saida, as_attachment=True)

    return render_template("prever.html", projetos=projetos)


# =============================
# Inicialização
# =============================

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROJECTS_FOLDER, exist_ok=True)
    app.run(debug=True)
