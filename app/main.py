# Habilita anotações de tipo de importação futura para compatibilidade
from __future__ import annotations

# Importa a classe FastAPI do módulo fastapi
from fastapi import FastAPI
# Importa a classe StaticFiles para servir arquivos estáticos
from fastapi.staticfiles import StaticFiles

# Importa os roteadores de API, exportações e páginas do diretório app.routers
from app.routers import api, exports, pages
# Importa a função get_logger do módulo app.utils.logger para configuração de log
from app.utils.logger import get_logger

# Obtém uma instância do logger com o nome do módulo atual
logger = get_logger(__name__)


# Define uma função para criar e configurar a aplicação FastAPI
def create_app() -> FastAPI:
    # Inicializa a aplicação FastAPI com metadados (título, descrição, versão)
    app = FastAPI(
        title="WebSentix",  # Título da aplicação
        description="Aplicação web de análise de sentimentos com FastAPI",  # Descrição da aplicação
        version="1.0.0",  # Versão da aplicação
    )

    # Monta um diretório de arquivos estáticos para ser servido em "/static"
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Inclui o roteador para páginas web
    app.include_router(pages.router)
    # Inclui o roteador para a API, com prefixo "/api" e tag "analysis"
    app.include_router(api.router, prefix="/api", tags=["analysis"])
    # Inclui o roteador para exportações, com prefixo "/exports" e tag "exports"
    app.include_router(exports.router, prefix="/exports", tags=["exports"])

    # Define um endpoint de verificação de saúde (healthcheck)
    @app.get("/health", tags=["health"])
    # Função que retorna o status da aplicação
    def healthcheck() -> dict[str, str]:
        # Retorna um dicionário indicando que o status é "ok"
        return {"status": "ok"}

    # Retorna a instância da aplicação FastAPI configurada
    return app


# Cria a instância principal da aplicação chamando a função create_app
app = create_app()
