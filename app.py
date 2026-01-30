from pdf_report import gerar_pdf             # Gera o relatório em PDF
from predictor import prever                 # Faz previsões em novos dados
from automl_engine import treinar_automl     # Treina os modelos automaticamente
from versionador import criar_pasta_versao   # Cria versão do projeto
import os  # Importa o módulo os para interagir com o sistema operacional
# Importa funções de gerenciamento de versão
from version_manager import listar_versoes, marcar_como_producao, versao_em_producao
import sys  # Importa o módulo sys para interagir com o interpretador Python
# Importa a função marcar_como_producao do version_manager
from version_manager import marcar_como_producao
import json  # Importa o módulo json para trabalhar com dados JSON
# Importa send_from_directory do Flask para servir arquivos
from flask import send_from_directory
# Importa request, redirect e url_for do Flask para manipulação de requisições e redirecionamentos
from flask import request, redirect, url_for
# Importa a função versao_em_producao do version_manager
from version_manager import versao_em_producao
# Importa classes e funções essenciais do Flask
from flask import Flask, render_template, request, send_file, redirect, url_for

# =========================================================
# CONFIGURAÇÃO DE PATH PARA IMPORTS INTERNOS DO PROJETO
# =========================================================

# Adiciona a pasta atual ao path do Python para permitir imports locais
sys.path.append(os.path.dirname(__file__))

# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

UPLOAD_FOLDER = "uploads"    # Pasta onde os CSVs enviados são salvos
PROJECTS_FOLDER = "projects"  # Pasta onde ficam todos os projetos

# Inicializa o Flask
app = Flask(__name__)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================


def listar_projetos():  # Define a função listar_projetos

    # Verifica se a pasta de projetos não existe
    if not os.path.exists(PROJECTS_FOLDER):
        return []  # Se não existir, retorna uma lista vazia

    return [  # Retorna uma lista de nomes de diretórios
        # Para cada nome na lista de itens dentro da pasta de projetos
        nome for nome in os.listdir(PROJECTS_FOLDER)
        # Verifica se o item é um diretório
        if os.path.isdir(os.path.join(PROJECTS_FOLDER, nome))
    ]


def salvar_upload(file):  # Define a função salvar_upload que recebe um arquivo como argumento
    # Cria a pasta de upload se ela não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Constrói o caminho completo para salvar o arquivo
    caminho = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(caminho)  # Salva o arquivo no caminho especificado
    return caminho  # Retorna o caminho onde o arquivo foi salvo

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


# Define a rota para servir arquivos de uma versão específica de um projeto
@app.route("/files/<projeto>/<versao>/<path:filename>")
# Define a função que lida com a requisição
def arquivos_projeto(projeto, versao, filename):
    import os  # Importa o módulo os para interagir com o sistema operacional

    # Constrói o caminho completo para a pasta de treinos da versão
    pasta = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)

    if not os.path.exists(pasta):  # Verifica se a pasta da versão não existe
        return "Pasta não encontrada", 404  # Retorna uma mensagem de erro e o status 404

    # Serve o arquivo da pasta especificada, sem forçar download
    return send_from_directory(pasta, filename, as_attachment=False)


# Define a rota para marcar uma versão como produção
@app.route("/marcar_producao/<projeto>/<versao>")
def marcar_producao(projeto, versao):  # Define a função que lida com a requisição
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho completo para a pasta do projeto
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)

    # Cria a pasta do projeto se ela não existir
    os.makedirs(pasta_projeto, exist_ok=True)

    # Constrói o caminho completo para o arquivo producao.json
    caminho = os.path.join(pasta_projeto, "producao.json")

    # Abre o arquivo producao.json em modo de escrita
    with open(caminho, "w", encoding="utf-8") as f:
        # Escreve a versão atual no arquivo JSON, formatado com 4 espaços de indentação
        json.dump({"versao": versao}, f, indent=4)

    # Imprime uma mensagem de confirmação no console
    print("✅ Produção marcada:", projeto, versao)

    # 🔁 VOLTA PARA A TELA DE DETALHES DA MESMA VERSÃO
    return redirect(url_for("ver_detalhes", projeto=projeto, versao=versao))


# Define a função obter_versao_producao que recebe o caminho da pasta do projeto como argumento
def obter_versao_producao(pasta_projeto):
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho completo para o arquivo producao.json
    caminho = os.path.join(pasta_projeto, "producao.json")

    if not os.path.exists(caminho):  # Verifica se o arquivo producao.json não existe
        return None  # Se não existir, retorna None

    # Abre o arquivo producao.json em modo de leitura
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)  # Carrega os dados JSON do arquivo

    # Retorna o valor associado à chave "versao" no dicionário de dados, ou None se a chave não existir
    return dados.get("versao")


# Define a rota para a página de histórico de um projeto
@app.route("/historico/<projeto>")
def historico(projeto):  # Define a função que lida com a requisição
    # Constrói o caminho completo para a pasta do projeto
    pasta_projeto = os.path.join("projetos", projeto)

    # Lista as versões do projeto usando a função listar_versoes
    versoes = listar_versoes(pasta_projeto)
    # Obtém a versão em produção do projeto usando a função versao_em_producao
    producao = versao_em_producao(pasta_projeto)

    return render_template(  # Renderiza o template historico.html
        "historico.html",  # Nome do template
        projeto=projeto,  # Passa o nome do projeto para o template
        versoes=versoes,  # Passa a lista de versões para o template
        producao=producao  # Passa a versão em produção para o template
    )


# Define a rota para a página de timeline de um projeto
@app.route("/timeline/<projeto>")
def timeline(projeto):  # Define a função que lida com a requisição da timeline
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho para a pasta de treinos do projeto
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    # Verifica se a pasta de treinos não existe
    if not os.path.exists(pasta_treinos):
        # Retorna uma mensagem de erro se o projeto não for encontrado
        return f"Projeto {projeto} não encontrado", 404

    historico = []  # Inicializa uma lista vazia para armazenar o histórico de versões
    producao_atual = None  # Inicializa a variável para a versão em produção como None

    # Imprime uma mensagem indicando qual pasta está sendo lida
    print("📂 Lendo versões em:", pasta_treinos)
    # Imprime o conteúdo da pasta de treinos
    print("📂 Conteúdo:", os.listdir(pasta_treinos))

    # Itera sobre as versões ordenadas na pasta de treinos
    for versao in sorted(os.listdir(pasta_treinos)):
        # Constrói o caminho para a pasta da versão
        pasta_versao = os.path.join(pasta_treinos, versao)
        # Constrói o caminho para o arquivo meta.json da versão
        meta_path = os.path.join(pasta_versao, "meta.json")

        # Verifica se o arquivo meta.json não existe
        if not os.path.exists(meta_path):
            # Imprime um aviso se o meta.json não for encontrado
            print("⚠️ Sem meta.json em", pasta_versao)
            continue  # Pula para a próxima versão

        # Abre o arquivo meta.json em modo de leitura
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)  # Carrega os dados JSON do arquivo

        item = {  # Cria um dicionário com os detalhes da versão
            "versao": versao,  # Adiciona o nome da versão
            # Adiciona a data da versão (ou string vazia se não existir)
            "data": meta.get("data", ""),
            # Adiciona o comentário da versão (ou string vazia se não existir)
            "comentario": meta.get("comentario", ""),
            # Adiciona o melhor modelo da versão (ou string vazia se não existir)
            "melhor_modelo": meta.get("melhor_modelo", ""),
            # Adiciona o melhor score da versão
            "melhor_score": meta.get("melhor_score"),
            "acc": meta.get("acc"),  # Adiciona a acurácia da versão
            "f1": meta.get("f1"),  # Adiciona o F1-score da versão
            # Adiciona as métricas da versão (ou dicionário vazio se não existir)
            "metricas": meta.get("metricas", {}),
            # Adiciona se a versão está em produção (ou False se não existir)
            "em_producao": meta.get("producao", False)
        }

        if item["em_producao"]:  # Verifica se a versão está em produção
            producao_atual = versao  # Define a versão atual em produção

        # Adiciona o item (detalhes da versão) ao histórico
        historico.append(item)

    return render_template(  # Renderiza o template timeline.html
        "timeline.html",  # Nome do template
        projeto=projeto,  # Passa o nome do projeto para o template
        historico=historico,  # Passa o histórico de versões para o template
        producao=producao_atual  # Passa a versão em produção para o template
    )


# Define a rota para a página de detalhes de uma versão
@app.route("/ver_detalhes/<projeto>/<versao>")
def ver_detalhes(projeto, versao):  # Define a função que lida com a requisição
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho para a pasta da versão
    pasta_versao = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)

    # Verifica se a pasta da versão não existe
    if not os.path.exists(pasta_versao):
        # Retorna uma mensagem de erro se a versão não for encontrada
        return "Versão não encontrada", 404

    # Constrói o caminho para o arquivo meta.json da versão
    caminho_meta = os.path.join(pasta_versao, "meta.json")

    # Verifica se o arquivo meta.json não existe
    if not os.path.exists(caminho_meta):
        # Retorna uma mensagem de erro se o meta.json não for encontrado
        return "meta.json não encontrado", 404

    # Abre o arquivo meta.json em modo de leitura
    with open(caminho_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)  # Carrega os dados JSON do arquivo

    # =========================
    # Verifica se é produção
    # =========================
    caminho_producao = os.path.join(PROJECTS_FOLDER, projeto, "producao.json")

    em_producao = False  # Inicializa a variável em_producao como False
    if os.path.exists(caminho_producao):  # Verifica se o arquivo producao.json existe
        # Abre o arquivo producao.json em modo de leitura
        with open(caminho_producao, "r", encoding="utf-8") as f:
            dados = json.load(f)  # Carrega os dados JSON do arquivo
            # Verifica se a versão atual é a versão em produção
            if dados.get("versao") == versao:
                em_producao = True  # Define em_producao como True

    # Constrói o caminho completo para a pasta do projeto
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    # Obtém a versão em produção do projeto
    versao_producao = obter_versao_producao(pasta_projeto)

    return render_template(  # Renderiza o template detalhes_versao.html
        "detalhes_versao.html",  # Nome do template
        projeto=projeto,  # Passa o nome do projeto para o template
        versao=versao,  # Passa a versão atual para o template
        meta=meta,  # Passa os metadados da versão para o template
        versao_producao=versao_producao  # Passa a versão em produção para o template
    )


# Define a rota para restaurar uma versão
@app.route("/restaurar/<projeto>/<versao>")
def restaurar_versao(projeto, versao):  # Define a função que lida com a requisição
    import os  # Importa o módulo os para interagir com o sistema operacional
    from flask import redirect  # Importa a função redirect do Flask para redirecionar

    # Constrói o caminho base para a pasta do projeto
    pasta_base = os.path.join(PROJECTS_FOLDER, projeto)

    if not os.path.exists(pasta_base):  # Verifica se a pasta do projeto não existe
        # Retorna uma mensagem de erro se o projeto não for encontrado
        return "Projeto não encontrado", 404

    # Constrói o caminho para o arquivo PRODUCAO.txt
    caminho_prod = os.path.join(pasta_base, "PRODUCAO.txt")

    # Se já for produção, não faz nada
    if os.path.exists(caminho_prod):  # Verifica se o arquivo PRODUCAO.txt existe
        # Abre o arquivo PRODUCAO.txt em modo de leitura
        with open(caminho_prod, "r", encoding="utf-8") as f:
            atual = f.read().strip()  # Lê o conteúdo do arquivo e remove espaços em branco

        if atual == versao:  # Verifica se a versão atual já está em produção
            print("⚠️ Esta versão já está em produção.")  # Imprime um aviso
            # Redireciona para os detalhes da versão
            return redirect(f"/ver_detalhes/{projeto}/{versao}")

    # Grava nova produção
    # Abre o arquivo PRODUCAO.txt em modo de escrita
    with open(caminho_prod, "w", encoding="utf-8") as f:
        f.write(versao)  # Escreve o nome da versão no arquivo

    # Imprime uma mensagem de confirmação
    print(f"🚀 Versão {versao} restaurada como produção em {projeto}")

    # Redireciona para a timeline do projeto
    return redirect(f"/timeline/{projeto}")


# Define a rota para editar o comentário de uma versão específica do projeto, aceitando métodos GET e POST
@app.route("/editar_comentario/<projeto>/<versao>", methods=["GET", "POST"])
# Define a função que lida com a requisição de edição de comentário
def editar_comentario(projeto, versao):
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho completo para a pasta da versão
    pasta = os.path.join(PROJECTS_FOLDER, projeto, "treinos", versao)
    # Constrói o caminho completo para o arquivo meta.json da versão
    meta_path = os.path.join(pasta, "meta.json")

    if not os.path.exists(meta_path):  # Verifica se o arquivo meta.json não existe
        # Retorna uma mensagem de erro se o meta.json não for encontrado
        return f"meta.json não encontrado em {pasta}", 404

    # Abre o arquivo meta.json em modo de leitura
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)  # Carrega os dados JSON do arquivo

    if request.method == "POST":  # Verifica se o método da requisição é POST
        # Obtém o valor do campo "comentario" do formulário, ou uma string vazia se não existir
        comentario = request.form.get("comentario", "")
        # Atualiza o valor do comentário no dicionário meta
        meta["comentario"] = comentario

        # Abre o arquivo meta.json em modo de escrita
        with open(meta_path, "w", encoding="utf-8") as f:
            # Escreve o dicionário meta atualizado no arquivo JSON, formatado com 4 espaços de indentação e garantindo caracteres não ASCII
            json.dump(meta, f, indent=4, ensure_ascii=False)

        # Redireciona para a página da timeline do projeto
        return redirect(url_for("timeline", projeto=projeto))

    # Obtém o comentário atual do dicionário meta, ou uma string vazia se não existir
    comentario_atual = meta.get("comentario", "")

    return render_template(  # Renderiza o template editar_comentario.html
        "editar_comentario.html",  # Nome do template
        projeto=projeto,  # Passa o nome do projeto para o template
        versao=versao,  # Passa a versão atual para o template
        comentario=comentario_atual  # Passa o comentário atual para o template
    )


# Define a rota para salvar o comentário de uma versão específica do projeto, aceitando apenas o método POST
@app.route("/salvar_comentario/<projeto>/<versao>", methods=["POST"])
# Define a função que lida com a requisição de salvamento de comentário
def salvar_comentario(projeto, versao):
    import os  # Importa o módulo os para interagir com o sistema operacional
    import json  # Importa o módulo json para trabalhar com dados JSON

    # Constrói o caminho completo para a pasta do projeto
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)
    # Constrói o caminho completo para a pasta da versão
    pasta_versao = os.path.join(pasta_projeto, versao)
    # Constrói o caminho completo para o arquivo meta.json da versão
    caminho_meta = os.path.join(pasta_versao, "meta.json")

    # Verifica se o arquivo meta.json não existe
    if not os.path.exists(caminho_meta):
        # Retorna uma mensagem de erro se o meta.json não for encontrado
        return "Meta.json não encontrado", 404

    # Lê meta.json atual
    # Abre o arquivo meta.json em modo de leitura
    with open(caminho_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)  # Carrega os dados JSON do arquivo

    # Obtém o valor do campo "comentario" do formulário, ou uma string vazia se não existir
    comentario = request.form.get("comentario", "")

    # Salva no meta
    # Atualiza o valor do comentário no dicionário meta
    meta["comentario"] = comentario

    # Abre o arquivo meta.json em modo de escrita
    with open(caminho_meta, "w", encoding="utf-8") as f:
        # Escreve o dicionário meta atualizado no arquivo JSON, formatado com 4 espaços de indentação e garantindo caracteres não ASCII
        json.dump(meta, f, indent=4, ensure_ascii=False)

    # Redireciona para a página da timeline do projeto
    return redirect(url_for("timeline", projeto=projeto))


# Define a rota para comparar duas versões específicas de um projeto
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

    # Dados para gráfico e tabela
    nomes = [
        f"{v1} - {m1.get('melhor_modelo','')}",
        f"{v2} - {m2.get('melhor_modelo','')}"
    ]

    try:
        s1 = float(m1.get("melhor_score", 0))
        s2 = float(m2.get("melhor_score", 0))
    except:
        s1 = 0
        s2 = 0

    scores = [s1, s2]

    resultados = [
        (nomes[0], s1),
        (nomes[1], s2),
    ]

    # Descobre produção
    producao = None
    caminho_prod = os.path.join(PROJECTS_FOLDER, projeto, "PRODUCAO.txt")
    if os.path.exists(caminho_prod):
        with open(caminho_prod, encoding="utf-8") as f:
            producao = f.read().strip()

    # Diferença
    diff = s2 - s1

    return render_template(
        "comparar_versoes.html",
        projeto=projeto,
        v1=v1,
        v2=v2,
        m1=m1,
        m2=m2,
        producao=producao,
        diff=diff,
        nomes=nomes,
        scores=scores,
        resultados=resultados
    )

# Define uma rota alternativa com versões pré-selecionadas
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

    # Se ainda não escolheu duas versões → só mostra a tela
    if not v1 or not v2:
        return render_template(
            "comparar_grafico.html",
            projeto=projeto,
            versoes=versoes,
            v1=None,
            v2=None,
            meta1=None,
            meta2=None,
            vencedora=None,
            producao=obter_versao_producao(pasta_projeto)
        )

    # Se vieram duas versões, carrega os dados
    meta1 = carregar_meta(v1)
    meta2 = carregar_meta(v2)

    vencedora = None
    if meta1 and meta2:
        vencedora = v1 if meta1["melhor_score"] > meta2["melhor_score"] else v2

    return render_template(
        "comparar_grafico.html",
        projeto=projeto,
        versoes=versoes,
        v1=v1,
        v2=v2,
        meta1=meta1,
        meta2=meta2,
        vencedora=vencedora,
        producao=obter_versao_producao(pasta_projeto)
    )

    # Carrega os metadados da primeira versão
    meta1 = carregar_meta(v1)
    # Carrega os metadados da segunda versão
    meta2 = carregar_meta(v2)

    # Se meta1 ou meta2 não existirem, retorna um erro
    if not meta1 or not meta2:
        return "Uma das versões não existe", 404

    # Decide a versão vencedora com base no "melhor_score"
    if meta1["melhor_score"] > meta2["melhor_score"]:
        vencedora = v1  # Se o score de meta1 for maior, v1 é a vencedora
    else:
        vencedora = v2  # Caso contrário, v2 é a vencedora

    # Renderiza o template de comparação de duas versões com os dados processados
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

    # Constrói o caminho para o arquivo meta.json da primeira versão
    meta1_path = os.path.join(pasta_treinos, v1, "meta.json")
    # Constrói o caminho para o arquivo meta.json da segunda versão
    meta2_path = os.path.join(pasta_treinos, v2, "meta.json")

    # Verifica se os arquivos meta.json de ambas as versões existem
    if not os.path.exists(meta1_path) or not os.path.exists(meta2_path):
        # Retorna um erro se um dos arquivos não for encontrado
        return "Uma das versões não possui meta.json", 404

    # Abre e carrega o arquivo meta.json da primeira versão
    with open(meta1_path, "r", encoding="utf-8") as f:
        meta1 = json.load(f)

    # Abre e carrega o arquivo meta.json da segunda versão
    with open(meta2_path, "r", encoding="utf-8") as f:
        meta2 = json.load(f)

    vencedora = None  # Inicializa a variável vencedora como None
    try:  # Inicia um bloco try para tratamento de erros
        # Compara os "melhor_score" para decidir a versão vencedora
        if meta1["melhor_score"] > meta2["melhor_score"]:
            vencedora = v1  # Se meta1 tiver score maior, v1 é a vencedora
        elif meta2["melhor_score"] > meta1["melhor_score"]:
            vencedora = v2  # Se meta2 tiver score maior, v2 é a vencedora
    except:  # Captura qualquer exceção que ocorra
        pass  # Ignora o erro e continua

    # Renderiza o template de comparação de duas versões com os dados processados
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
    if meta1["melhor_score"] > meta2["melhor_score"]:  # Compara os scores das duas versões
        vencedora = v1  # Se o score da meta1 for maior, define v1 como vencedora
    else:  # Caso contrário
        vencedora = v2  # Define v2 como vencedora

    # Lê produção atual
        producao = None  # Inicializa a variável 'producao' como None
    # Constrói o caminho completo para o arquivo 'producao.json'
    caminho_prod = os.path.join(PROJECTS_FOLDER, projeto, "producao.json")
    if os.path.exists(caminho_prod):  # Verifica se o arquivo 'producao.json' existe
        # Abre o arquivo 'producao.json' em modo de leitura
        with open(caminho_prod, "r", encoding="utf-8") as f:
            # Carrega os dados JSON do arquivo e obtém o valor da chave "versao"
            producao = json.load(f).get("versao")

    # Lista versões para o select
    versoes = []  # Inicializa uma lista vazia para armazenar as versões
    # Itera sobre os diretórios na pasta de treinos
    for v in os.listdir(pasta_treinos):
        # Verifica se o arquivo meta.json existe dentro do diretório da versão
        if os.path.exists(os.path.join(pasta_treinos, v, "meta.json")):
            versoes.append(v)  # Adiciona o nome da versão à lista

    versoes = sorted(versoes)  # Ordena as versões em ordem alfabética

    return render_template(  # Renderiza o template 'comparar_duas.html'
        "comparar_duas.html",  # Nome do template
        projeto=projeto,  # Passa o nome do projeto para o template
        versoes=versoes,  # Passa a lista de versões para o template
        v1=v1,  # Passa a primeira versão selecionada para o template
        v2=v2,  # Passa a segunda versão selecionada para o template
        meta1=meta1,  # Passa os metadados da primeira versão para o template
        meta2=meta2,  # Passa os metadados da segunda versão para o template
        vencedora=vencedora,  # Passa a versão vencedora para o template
        producao=producao  # Passa a versão em produção para o template
    )


# Define a rota para promover uma versão à produção
@app.route("/promover_producao/<projeto>/<versao>")
# Define a função que lida com a requisição de promoção
def promover_producao(projeto, versao):
    import os  # Importa o módulo os para interagir com o sistema operacional

    # Constrói o caminho base para a pasta do projeto
    pasta_base = os.path.join(PROJECTS_FOLDER, projeto)

    if not os.path.exists(pasta_base):  # Verifica se a pasta do projeto não existe
        # Retorna uma mensagem de erro se o projeto não for encontrado
        return "Projeto não encontrado", 404

    # Constrói o caminho para o arquivo PRODUCAO.txt
    caminho_prod = os.path.join(pasta_base, "PRODUCAO.txt")
    # Abre o arquivo PRODUCAO.txt em modo de escrita
    with open(caminho_prod, "w", encoding="utf-8") as f:
        f.write(versao)  # Escreve o nome da versão no arquivo

    # Imprime uma mensagem de confirmação
    print(f"🏆 Versão {versao} promovida para produção em {projeto}")

    # Redireciona para a timeline do projeto
    return redirect(f"/timeline/{projeto}")


# Define a rota para a página de comparação de versões de um projeto
@app.route("/comparar_lista/<projeto>")
def comparar(projeto):  # Define a função que lida com a requisição de comparação
    # Constrói o caminho para a pasta de treinos do projeto
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    historico = []  # Inicializa uma lista vazia para armazenar o histórico de versões

    # Itera sobre as versões ordenadas na pasta de treinos
    for v in sorted(os.listdir(pasta_treinos)):
        # Constrói o caminho para o arquivo meta.json da versão
        caminho_meta = os.path.join(pasta_treinos, v, "meta.json")

        if os.path.exists(caminho_meta):  # Verifica se o arquivo meta.json existe
            # Abre o arquivo meta.json em modo de leitura
            with open(caminho_meta, encoding="utf-8") as f:
                meta = json.load(f)  # Carrega os dados JSON do arquivo
                # Adiciona os metadados da versão ao histórico
                historico.append(meta)

    # Renderiza o template 'comparar_versoes.html' com o projeto e o histórico
    return render_template("comparar_grafico.html", projeto=projeto, historico=historico)


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
    # Constrói o caminho para o arquivo de relatório
    caminho_relatorio = os.path.join(pasta, "resultado.txt")
    # Constrói o caminho para o arquivo de gráfico
    caminho_grafico = os.path.join(pasta, "ranking.png")
    # Constrói o caminho para o arquivo meta.json
    caminho_meta = os.path.join(pasta, "meta.json")

    # =====================================================
    # LÊ O META.JSON (SE EXISTIR)
    # =====================================================

    # Inicializa um dicionário vazio para armazenar metadados
    meta = {}

    # Verifica se o arquivo meta.json existe no caminho especificado
    if os.path.exists(caminho_meta):
        # Abre o arquivo meta.json em modo de leitura com codificação UTF-8
        with open(caminho_meta, encoding="utf-8") as f:
            # Carrega o conteúdo JSON do arquivo para o dicionário 'meta'
            meta = json.load(f)

    # =====================================================
    # LÊ O RESULTADO.TXT E EXTRAI OS SCORES DOS MODELOS
    # =====================================================

    resultados_dict = {}  # Formato final: { "Modelo": score }

    with open(caminho_relatorio, encoding="utf-8") as f:  # Abre o arquivo de relatório para leitura
        for linha in f:  # Itera sobre cada linha do arquivo
            # Só processa linhas no formato: Modelo: score
            if ":" in linha:  # Verifica se a linha contém um ":" para indicar um modelo e score
                nome, score_txt = linha.split(":", 1)  # Divide a linha no primeiro ":" para obter o nome do modelo e o texto do score

                try:  # Inicia um bloco try para tratamento de erros ao converter o score
                    score = float(score_txt.strip())  # Converte o texto do score para um número float e remove espaços
                    resultados_dict[nome.strip()] = score  # Adiciona o nome do modelo (sem espaços) e o score ao dicionário de resultados
                except:
                    # Ignora linhas que não são números
                    pass

    # =====================================================
    # DESCOBRE AUTOMATICAMENTE O MELHOR MODELO
    # =====================================================

    melhor_modelo_auto = "N/A"  # Inicializa a variável melhor_modelo_auto com "N/A"
    melhor_score_auto = "N/A"  # Inicializa a variável melhor_score_auto com "N/A"

    if len(resultados_dict) > 0:  # Verifica se o dicionário de resultados não está vazio
        # Encontra o modelo com o melhor score
        melhor_modelo_auto = max(resultados_dict, key=resultados_dict.get)
        # Obtém o melhor score correspondente ao melhor modelo
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

    melhor_modelo = meta.get("melhor_modelo", melhor_modelo_auto) # Define o melhor modelo, priorizando meta.json ou o cálculo automático
    melhor_score = meta.get("melhor_score", melhor_score_auto) # Define o melhor score, priorizando meta.json ou o cálculo automático

    # =====================================================
    # ORDENA RESULTADOS DO MELHOR PARA O PIOR (PARA RANKING)
    # =====================================================

    # Cria um novo dicionário com os itens de 'resultados_dict' ordenados
    # pelo valor (x[1]) em ordem decrescente (reverse=True)
    resultados_ordenados = dict(
        sorted(resultados_dict.items(), key=lambda x: x[1], reverse=True)
    )

    # Monta o caminho completo da pasta do projeto,
    # juntando o diretório base PROJECTS_FOLDER com o nome do projeto
    pasta_projeto = os.path.join(PROJECTS_FOLDER, projeto)

    # Obtém a versão que está atualmente em produção,
    # a partir da pasta do projeto
    versao_producao = versao_em_producao(pasta_projeto)

    # Verifica se a última versão é a mesma que está em produção
    # O resultado será True ou False
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


# Define uma rota Flask que recebe o nome do projeto pela URL
# Exemplo de acesso: /baixar_pdf/meu_projeto
@app.route("/baixar_pdf/<projeto>")
def baixar_pdf(projeto):

    # Monta o caminho da pasta "treinos" dentro do projeto informado
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    # Lista todas as pastas/arquivos dentro de "treinos" e ordena em ordem crescente
    versoes = sorted(os.listdir(pasta_treinos))

    # Seleciona a última versão da lista (normalmente a mais recente)
    ultima = versoes[-1]

    # Monta o caminho completo até o arquivo "relatorio.pdf"
    # que está dentro da última versão
    caminho = os.path.join(pasta_treinos, ultima, "relatorio.pdf")

    # Envia o arquivo PDF para download no navegador
    # as_attachment=True força o download em vez de abrir no navegador
    return send_file(caminho, as_attachment=True)

# =========================================================
# PÁGINA DE PREVISÃO
# =========================================================

# Define a rota "/prever" que aceita requisições GET e POST
@app.route("/prever", methods=["GET", "POST"])
def pagina_prever():

    # Obtém a lista de projetos disponíveis
    projetos = listar_projetos()

    # Verifica se a requisição foi feita via método POST (envio de formulário)
    if request.method == "POST":

        # Obtém o arquivo enviado pelo formulário (input type="file")
        file = request.files.get("file")

        # Obtém o nome do projeto selecionado no formulário
        projeto = request.form.get("projeto")

        # Verifica se o arquivo ou o projeto não foram informados
        if not file or not projeto:
            return "Arquivo ou projeto não selecionado"

        # Salva o arquivo CSV enviado e retorna o caminho onde foi salvo
        caminho_csv = salvar_upload(file)

        # Monta o caminho do arquivo do modelo treinado (modelo.pkl)
        modelo = os.path.join(PROJECTS_FOLDER, projeto, "modelo.pkl")

        # Executa a previsão usando o CSV enviado e o modelo selecionado
        # e retorna o caminho do arquivo de saída gerado
        saida = prever(caminho_csv, modelo)

        # Envia o arquivo de saída para download
        return send_file(saida, as_attachment=True)

    # Se a requisição for GET, renderiza a página HTML "prever.html"
    # passando a lista de projetos para o template
    return render_template("prever.html", projetos=projetos)

# =========================================================
# GERENCIAR VERSÕES
# =========================================================

# Define uma rota Flask que recebe o nome do projeto pela URL
# Exemplo: /versoes/meu_projeto
@app.route("/versoes/<projeto>")
def gerenciar_versoes(projeto):

    # Monta o caminho da pasta "treinos" dentro do projeto informado
    pasta_treinos = os.path.join(PROJECTS_FOLDER, projeto, "treinos")

    # Inicializa uma lista vazia para armazenar os metadados das versões
    versoes = []

    # Percorre as pastas de versões dentro de "treinos", em ordem crescente
    for v in sorted(os.listdir(pasta_treinos)):

        # Monta o caminho completo do arquivo "meta.json" da versão atual
        caminho_meta = os.path.join(pasta_treinos, v, "meta.json")

        # Verifica se o arquivo "meta.json" existe nessa versão
        if os.path.exists(caminho_meta):

            # Abre o arquivo "meta.json" usando codificação UTF-8
            with open(caminho_meta, encoding="utf-8") as f:

                # Lê o conteúdo do JSON e converte para um dicionário Python
                meta = json.load(f)

                # Adiciona os metadados da versão à lista "versoes"
                versoes.append(meta)

    # Renderiza o template "versoes.html",
    # passando o nome do projeto e a lista de versões para a página
    return render_template("versoes.html", projeto=projeto, versoes=versoes)


# =========================================================
# LISTAGEM DE PROJETOS
# =========================================================


# Define uma rota Flask para a URL "/projetos"
@app.route("/projetos")
def historico_projetos():

    # Obtém a lista de projetos disponíveis no sistema
    projetos = listar_projetos()

    # Renderiza o template "projetos.html"
    # passando a lista de projetos para ser exibida na página
    return render_template("projetos.html", projetos=projetos)


# =========================================================
# INICIALIZAÇÃO DO SERVIDOR
# =========================================================


# Verifica se este arquivo está sendo executado diretamente
# (e não importado como módulo em outro arquivo)
if __name__ == "__main__":

    # Cria a pasta de uploads, caso ela não exista
    # exist_ok=True evita erro se a pasta já estiver criada
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Cria a pasta principal de projetos, caso ela não exista
    # exist_ok=True evita erro se a pasta já estiver criada
    os.makedirs(PROJECTS_FOLDER, exist_ok=True)


    # Inicia o servidor Flask em modo debug
    app.run(debug=True)
