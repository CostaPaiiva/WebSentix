# 1. Define rotas da API para análise de texto, URL ou arquivo usando FastAPI.
# 2. Integra serviços de extração de conteúdo, leitura de arquivos, análise de sentimentos e histórico.
# 3. Implementa função central de análise (_perform_analysis) que processa diferentes tipos de entrada.
# 4. Retorna resultados em formato HTML (template Jinja2) ou JSON, conforme a rota acessada.
# 5. Inclui tratamento robusto de erros e logging para monitoramento e depuração.

# Importa suporte para anotações futuras de tipo
from __future__ import annotations

# Importa tipagem genérica
from typing import Any

# Importa classes e funções do FastAPI para criação de rotas e dependências
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Importa dependências da aplicação (injeção de serviços)
from app.dependencies import (
    get_content_extractor,
    get_file_reader_service,
    get_history_service,
    get_sentiment_service,
)
# Importa modelos de dados
from app.models.schemas import AnalysisInput, InputType
# Importa serviços específicos da aplicação
from app.services.content_extractor import ContentExtractionError, ContentExtractor
from app.services.file_reader_service import FileReaderError, FileReaderService
from app.services.history_service import HistoryService
from app.services.sentiment_service import SentimentService, SentimentServiceError
# Importa utilitário de logging
from app.utils.logger import get_logger
# Importa validador de entradas
from app.utils.validators import validate_analysis_input

# Inicializa logger
logger = get_logger(__name__)
# Cria objeto de roteamento da API
router = APIRouter()
# Configura templates Jinja2 para renderização HTML
templates = Jinja2Templates(directory="app/templates")


# Função interna que realiza a análise de acordo com o tipo de entrada
def _perform_analysis(
    input_type: InputType,
    raw_value: str | None,
    uploaded_file: UploadFile | None,
    content_extractor: ContentExtractor,
    file_reader_service: FileReaderService,
    sentiment_service: SentimentService,
    history_service: HistoryService,
) -> dict[str, Any]:
    # Caso a entrada seja texto manual
    if input_type == InputType.TEXT:
        validated = validate_analysis_input(
            AnalysisInput(input_type=input_type, value=raw_value or "")
        )
        content = validated.value
        source_value = "texto_manual"
    # Caso a entrada seja uma URL
    elif input_type == InputType.URL:
        validated = validate_analysis_input(
            AnalysisInput(input_type=input_type, value=raw_value or "")
        )
        extraction = content_extractor.extract_from_url(validated.value)
        content = extraction["text"]
        source_value = validated.value
    # Caso a entrada seja um arquivo
    elif input_type == InputType.FILE:
        file_result = file_reader_service.read_uploaded_file(uploaded_file)
        content = file_result["text"]
        source_value = file_result["filename"]
    else:
        # Se o tipo não for válido, lança erro
        raise ValueError("Tipo de entrada inválido.")

    # Realiza análise de sentimentos
    result = sentiment_service.analyze_text(
        text=content,
        source_type=input_type.value,
        source_value=source_value,
    )
    # Salva resultado no histórico
    history_service.append_result(result)
    return result


# Rota POST para análise via formulário, retornando HTML
@router.post("/analyze", response_class=HTMLResponse)
async def analyze_form(
    request: Request,
    input_type: str = Form(...),
    text_value: str = Form(""),
    url_value: str = Form(""),
    file_value: UploadFile | None = File(default=None),
    content_extractor: ContentExtractor = Depends(get_content_extractor),
    file_reader_service: FileReaderService = Depends(get_file_reader_service),
    sentiment_service: SentimentService = Depends(get_sentiment_service),
    history_service: HistoryService = Depends(get_history_service),
) -> HTMLResponse:
    try:
        # Determina o modo de entrada
        mode = InputType(input_type)
        raw_value = text_value if mode == InputType.TEXT else url_value if mode == InputType.URL else None

        # Executa análise
        result = _perform_analysis(
            input_type=mode,
            raw_value=raw_value,
            uploaded_file=file_value,
            content_extractor=content_extractor,
            file_reader_service=file_reader_service,
            sentiment_service=sentiment_service,
            history_service=history_service,
        )

        # Carrega histórico e renderiza template
        history = history_service.load_history()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "history": history[:10],
                "result": result,
                "error": None,
                "active_mode": mode.value,
            },
        )

    # Tratamento de erros específicos
    except (ValueError, ContentExtractionError, FileReaderError, SentimentServiceError) as exc:
        logger.warning("Handled analysis error: %s", exc)
        history = history_service.load_history()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "history": history[:10],
                "result": None,
                "error": str(exc),
                "active_mode": input_type,
            },
            status_code=400,
        )
    # Tratamento de erros inesperados
    except Exception:
        logger.exception("Unexpected error during form analysis")
        history = history_service.load_history()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "history": history[:10],
                "result": None,
                "error": "Ocorreu um erro inesperado durante a análise.",
                "active_mode": input_type,
            },
            status_code=500,
        )


# Rota POST para análise retornando JSON
@router.post("/analyze/json", response_class=JSONResponse)
async def analyze_json(
    input_type: str = Form(...),
    text_value: str = Form(""),
    url_value: str = Form(""),
    file_value: UploadFile | None = File(default=None),
    content_extractor: ContentExtractor = Depends(get_content_extractor),
    file_reader_service: FileReaderService = Depends(get_file_reader_service),
    sentiment_service: SentimentService = Depends(get_sentiment_service),
    history_service: HistoryService = Depends(get_history_service),
) -> JSONResponse:
    try:
        # Determina o modo de entrada
        mode = InputType(input_type)
        raw_value = text_value if mode == InputType.TEXT else url_value if mode == InputType.URL else None

        # Executa análise
        result = _perform_analysis(
            input_type=mode,
            raw_value=raw_value,
            uploaded_file=file_value,
            content_extractor=content_extractor,
            file_reader_service=file_reader_service,
            sentiment_service=sentiment_service,
            history_service=history_service,
        )
        # Retorna resultado em JSON
        return JSONResponse(content=result)
    # Tratamento de erros específicos
    except (ValueError, ContentExtractionError, FileReaderError, SentimentServiceError) as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
