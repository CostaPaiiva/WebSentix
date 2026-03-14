# Permite o uso de anotações de tipo como strings para evitar problemas de referência circular
from __future__ import annotations

# Importa a classe responsável por extrair conteúdo
from app.services.content_extractor import ContentExtractor
# Importa a classe responsável por serviços de exportação de dados
from app.services.export_service import ExportService
# Importa a classe responsável por ler arquivos
from app.services.file_reader_service import FileReaderService
# Importa a classe que gerencia o histórico de operações
from app.services.history_service import HistoryService
# Importa a classe que realiza análise de sentimento
from app.services.sentiment_service import SentimentService

# Instancia o serviço de extração de conteúdo
content_extractor = ContentExtractor()
# Instancia o serviço de leitura de arquivos
file_reader_service = FileReaderService()
# Instancia o serviço de histórico
history_service = HistoryService()
# Instancia o serviço de exportação
export_service = ExportService()
# Instancia o serviço de análise de sentimento
sentiment_service = SentimentService()


# Função que retorna a instância única do extrator de conteúdo
def get_content_extractor() -> ContentExtractor:
    return content_extractor


# Função que retorna a instância única do leitor de arquivos
def get_file_reader_service() -> FileReaderService:
    return file_reader_service


# Função que retorna a instância única do serviço de histórico
def get_history_service() -> HistoryService:
    return history_service


# Função que retorna a instância única do serviço de exportação
def get_export_service() -> ExportService:
    return export_service


# Função que retorna a instância única do serviço de análise de sentimento
def get_sentiment_service() -> SentimentService:
    return sentiment_service
