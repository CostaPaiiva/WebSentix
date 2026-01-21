# Inicia o site
# Cria as páginas (rotas)
# Recebe arquivos do usuário
# Chama o AutoML
# Mostra resultados
# Gera PDF
# Faz previsões

import sys
import os
sys.path.append(os.path.dirname(__file__))
# Importa a função que cria versões automaticamente (v1, v2, v3...)
from versionador import criar_pasta_versao
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
def listar_projetos():
    # Se a pasta projects existir, lista os projetos dentro dela
    if os.path.exists(PROJECTS_FOLDER):
        return os.listdir(PROJECTS_FOLDER)
    # Se não existir, retorna lista vazia
    return []

def listar_projetos():
    # Se a pasta de projetos não existir, retorna lista vazia
    if not os.path.exists(PROJECTS_FOLDER):
        return []

    # Retorna apenas as pastas dentro de /projects
    return [
        nome for nome in os.listdir(PROJECTS_FOLDER)
        if os.path.isdir(os.path.join(PROJECTS_FOLDER, nome))
    ]
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
@app.route("/projetos")
def historico_projetos():
    projetos = listar_projetos()
    return render_template("projetos.html", projetos=projetos)
    
@app.route("/comparar/<projeto>")
def comparar(projeto):
    pasta = os.path.join(PROJECTS_FOLDER, projeto)
    caminho = os.path.join(pasta, "resultado.txt")

    resultados = []

    # Lê o arquivo e extrai nome e score
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if ":" in linha:
                nome, score = linha.split(":")
                resultados.append((nome.strip(), float(score.strip())))

    # Separa em listas para o gráfico
    nomes = [r[0] for r in resultados]
    scores = [r[1] for r in resultados]

    return render_template(
        "comparar.html",
        projeto=projeto,
        resultados=resultados,
        nomes=nomes,
        scores=scores
    )


    # Lê o arquivo e extrai nome e score
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if ":" in linha:
                nome, score = linha.split(":")
                resultados.append((nome.strip(), float(score.strip())))

    return render_template(
        "comparar.html",
        projeto=projeto,
        resultados=resultados
    )
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

        # SALVAR O ARQUIVO CSV
        # Salva o arquivo CSV na pasta uploads/
        # e guarda o caminho completo dele na variável caminho_csv
        caminho_csv = salvar_upload(file)

        # CRIAR NOME DO PROJETO
        # Usa o nome do arquivo (sem a extensão .csv) como nome do projeto
        nome_projeto = file.filename.replace(".csv", "")

        # Cria o caminho da pasta do projeto dentro de projects/
        # Ex: projects/iris
        pasta_projeto = os.path.join(PROJECTS_FOLDER, nome_projeto)

        pasta_versao, versao = criar_pasta_versao(pasta_projeto)

        # Treina o AutoML normalmente, mas salvando tudo dentro da pasta da versãoL
        tipo, melhor, score, relatorio_txt, grafico = treinar_automl(
        caminho_csv, 
        pasta_versao
)

        # LER RELATÓRIO EM TEXTO
        # Abre o arquivo de relatório .txt que foi gerado pelo AutoML
        with open(relatorio_txt, encoding="utf-8") as f:
            # Lê todo o conteúdo do arquivo e guarda na variável texto
            texto = f.read()

        # GERAR PDF
        # Ex: projects/iris/treinos/v1/relatorio.pdfo
        caminho_pdf = os.path.join(pasta_versao, "relatorio.pdf")

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
    # Pasta base do projeto
    pasta_base = os.path.join("projects", projeto)

    # Pasta onde ficam as versões treinadas
    pasta_treinos = os.path.join(pasta_base, "treinos")

    # Lista as versões existentes (v1, v2, v3, ...)
    versoes = sorted(os.listdir(pasta_treinos))

    # Pega sempre a última versão
    ultima_versao = versoes[-1]

    # Pasta completa da última versão
    pasta = os.path.join(pasta_treinos, ultima_versao)

    # Caminhos dos arquivos gerados pelo treino
    caminho_relatorio = os.path.join(pasta, "resultado.txt")
    caminho_grafico = os.path.join(pasta, "ranking.png")
    caminho_meta = os.path.join(pasta, "meta.json")

    # Lê o texto do relatório
    with open(caminho_relatorio, encoding="utf-8") as f:
        texto = f.read()

    # Carrega os metadados
    import json
    with open(caminho_meta, encoding="utf-8") as f:
        meta = json.load(f)

    # Renderiza o dashboard passando tudo pra tela
    return render_template(
        "dashboard.html",
        projeto=projeto,
        versao=ultima_versao,
        texto=texto,
        grafico="/" + caminho_grafico.replace("\\", "/"),
        meta=meta
    )


# Cria a rota para baixar o relatório em PDF de um projeto específico
# <projeto> é o nome do projeto passado pela URL
# Exemplo: /baixar_pdf/vendas_2024
@app.route("/baixar_pdf/<projeto>")
def baixar_pdf(projeto):
    pasta_treinos = os.path.join("projects", projeto, "treinos")
    versoes = sorted(os.listdir(pasta_treinos))
    ultima = versoes[-1]

    caminho = os.path.join(pasta_treinos, ultima, "relatorio.pdf")

    return send_file(caminho, as_attachment=True)


# Cria a rota da página de previsões
# Essa página aceita:
# - GET: quando o usuário apenas abre a página
# - POST: quando o usuário envia um CSV para ser previsto
import json

@app.route("/versoes/<projeto>")
def gerenciar_versoes(projeto):
    pasta_treinos = os.path.join("projects", projeto, "treinos")

    versoes = []

    for v in sorted(os.listdir(pasta_treinos)):
        caminho_meta = os.path.join(pasta_treinos, v, "meta.json")
        if os.path.exists(caminho_meta):
            with open(caminho_meta, encoding="utf-8") as f:
                meta = json.load(f)
                versoes.append(meta)

    return render_template("versoes.html", projeto=projeto, versoes=versoes)

@app.route("/prever", methods=["GET", "POST"])
def pagina_prever():
    # Busca a lista de projetos (modelos treinados) existentes
    projetos = listar_projetos()

    # Verifica se o usuário enviou o formulário
    if request.method == "POST":
        # Pega o arquivo CSV enviado pelo usuário
        file = request.files["file"]

        # Pega o nome do projeto escolhido no formulário HTML
        # Esse projeto indica qual modelo treinado será usado
        projeto = request.form["projeto"]

        # SALVAR CSV DE ENTRADA
        # Salva o CSV enviado pelo usuário na pasta uploads/
        # e guarda o caminho completo na variável caminho_csv
        caminho_csv = salvar_upload(file)


        # DEFINIR CAMINHO DO MODELO
        # Monta o caminho do arquivo do modelo treinado (.pkl)
        # Exemplo: projects/vendas_2024/modelo.pkl
        modelo = os.path.join(PROJECTS_FOLDER, projeto, "modelo.pkl")

        # GERAR PREVISÕES
        # Chama a função que:
        # - Carrega o modelo treinado
        # - Aplica o modelo aos novos dados
        # - Gera um novo CSV com as previsões
        saida = prever(caminho_csv, modelo)

        # Envia o arquivo com as previsões para download
        return send_file(saida, as_attachment=True)

    # Se o usuário apenas entrou na página (GET),
    # mostra a tela prever.html com a lista de projetos disponíveis
    return render_template("prever.html", projetos=projetos)



# Inicialização

# Esse bloco só será executado se este arquivo for o programa principal
# Ou seja: quando você roda no terminal:
# python app.py
# Mas NÃO será executado se esse arquivo for importado por outro módulo
if __name__ == "__main__":

    # Cria a pasta uploads/ se ela ainda não existir
    # Essa pasta é usada para salvar os arquivos enviados pelos usuários
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Cria a pasta projects/ se ela ainda não existir
    # Essa pasta guarda todos os projetos, modelos e relatórios gerados
    os.makedirs(PROJECTS_FOLDER, exist_ok=True)

    # Inicia o servidor web do Flask
    # debug=True faz:
    # - Mostrar erros detalhados no navegador
    # - Reiniciar o servidor automaticamente quando você altera o código
    app.run(debug=True)


from utils.versionamento import listar_versoes
print(listar_versoes("projects/dados_teste_modelo/treinos"))