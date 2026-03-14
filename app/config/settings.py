
# 1. Centraliza todas as configurações da aplicação em uma única classe (Settings).
# 2. Permite carregar valores de variáveis de ambiente via arquivo .env.
# 3. Define parâmetros para uso de um modelo de NLP de análise de sentimentos.
# 4. Controla limites de execução e nível de logs para estabilidade e monitoramento.
# 5. Organiza caminhos e arquivos importantes, como o histórico de análises.

# Importa suporte para anotações futuras de tipo (permite usar tipos como "list[str]" em versões antigas do Python)
from __future__ import annotations

# Importa a classe Path para manipulação de caminhos de arquivos e diretórios
from pathlib import Path

# Importa BaseSettings e SettingsConfigDict da biblioteca pydantic_settings para configuração baseada em variáveis de ambiente
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define o diretório base do projeto, subindo três níveis a partir do arquivo atual
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Cria uma classe de configuração chamada Settings que herda de BaseSettings
class Settings(BaseSettings):
    # Nome da aplicação
    app_name: str = "websentix"
    # Ambiente de execução (ex.: desenvolvimento, produção)
    environment: str = "development"
    # Flag para ativar/desativar modo debug
    debug: bool = False

    # Nome do modelo de NLP usado para análise de sentimentos
    model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    # Tempo máximo de espera para requisições
    request_timeout: int = 12
    # Número máximo de caracteres permitidos no conteúdo analisado
    max_content_chars: int = 12000
    # Caminho do arquivo de histórico de análises
    history_file: str = str(BASE_DIR / "data" / "analysis_history.json")
    # User-Agent usado em requisições HTTP
    user_agent: str = "Mozilla/5.0 (compatible; WebSentix/1.0; +https://localhost)"
    # Nível de log da aplicação
    log_level: str = "INFO"
    # Host onde a aplicação será executada
    host: str = "127.0.0.1"
    # Porta do servidor
    port: int = 8000

    # Configuração adicional para leitura de variáveis de ambiente
    model_config = SettingsConfigDict(
        env_file=".env",              # Arquivo de variáveis de ambiente
        env_file_encoding="utf-8",    # Codificação do arquivo .env
        case_sensitive=False,         # Variáveis de ambiente não diferenciam maiúsculas/minúsculas
    )


# Instancia a classe Settings, carregando as configurações
settings = Settings()
