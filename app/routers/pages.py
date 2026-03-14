# 1. Cria um roteador FastAPI para gerenciar rotas da aplicação.
# 2. Configura o uso de templates Jinja2 para renderizar páginas HTML.
# 3. Define a rota principal ("/") que serve como página inicial da aplicação.
# 4. Injeta o serviço de histórico (HistoryService) para acessar resultados anteriores.
# 5. Carrega o histórico de análises e limita a exibição aos 10 resultados mais recentes.
# 6. Renderiza o template "index.html" passando contexto com histórico, resultado e estado inicial.
# 7. Define valores padrão no contexto (sem resultado, sem erro, modo ativo = texto) para inicializar a interface.


# Permite usar recursos futuros da linguagem Python.
# Aqui especificamente ativa o comportamento de "annotations" adiado,
# permitindo usar tipos antes de serem definidos e melhor compatibilidade com typing.
from __future__ import annotations

# Importa o roteador do FastAPI, o sistema de dependências (Depends)
# e o objeto Request que representa a requisição HTTP recebida.
from fastapi import APIRouter, Depends, Request

# Importa a classe de resposta HTML, usada quando queremos retornar páginas HTML.
from fastapi.responses import HTMLResponse

# Importa o sistema de templates Jinja2 integrado ao FastAPI
# para renderizar arquivos HTML com dados dinâmicos.
from fastapi.templating import Jinja2Templates

# Importa a função que fornece a dependência do serviço de histórico.
# Essa função será usada pelo FastAPI para injetar o serviço automaticamente.
from app.dependencies import get_history_service

# Importa a classe HistoryService responsável por manipular o histórico.
from app.services.history_service import HistoryService

# Cria um roteador (router) do FastAPI.
# Ele permite organizar rotas em módulos separados.
router = APIRouter()

# Configura o sistema de templates Jinja2 apontando para a pasta
# onde estão os arquivos HTML do projeto.
templates = Jinja2Templates(directory="app/templates")


# Define uma rota GET para o caminho raiz "/".
# O parâmetro response_class=HTMLResponse indica que a resposta será HTML.
@router.get("/", response_class=HTMLResponse)

# Define a função que será executada quando alguém acessar "/".
def home(
    # Objeto da requisição HTTP atual.
    request: Request,

    # Injeta automaticamente uma instância de HistoryService
    # usando o sistema de dependências do FastAPI.
    history_service: HistoryService = Depends(get_history_service),
) -> HTMLResponse:  # Indica que a função retorna uma resposta HTML

    # Carrega o histórico utilizando o serviço de histórico.
    history = history_service.load_history()

    # Renderiza o template "index.html" usando Jinja2
    # e envia dados para o HTML através do contexto.
    return templates.TemplateResponse(

        # Passa o objeto da requisição para o template
        # (necessário para o funcionamento do Jinja2 no FastAPI).
        request=request,

        # Nome do arquivo HTML que será renderizado.
        name="index.html",

        # Contexto: dicionário com variáveis que o HTML poderá usar.
        context={
            # A requisição também precisa estar no contexto para o template.
            "request": request,

            # Envia apenas os 10 primeiros itens do histórico.
            "history": history[:10],

            # Resultado inicial da aplicação (nenhum ainda).
            "result": None,

            # Campo para mensagens de erro (inicialmente vazio).
            "error": None,

            # Define o modo ativo da interface (modo texto).
            "active_mode": "text",
        },
    )