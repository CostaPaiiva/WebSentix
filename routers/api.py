from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import (
    get_content_extractor,
    get_file_reader_service,
    get_history_service,
    get_sentiment_service,
)
from app.models.schemas import AnalysisInput, InputType
from app.services.content_extractor import ContentExtractionError, ContentExtractor
from app.services.file_reader_service import FileReaderError, FileReaderService
from app.services.history_service import HistoryService
from app.services.sentiment_service import SentimentService, SentimentServiceError
from app.utils.logger import get_logger
from app.utils.validators import validate_analysis_input

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _perform_analysis(
    input_type: InputType,
    raw_value: str | None,
    uploaded_file: UploadFile | None,
    content_extractor: ContentExtractor,
    file_reader_service: FileReaderService,
    sentiment_service: SentimentService,
    history_service: HistoryService,
) -> dict[str, Any]:
    if input_type == InputType.TEXT:
        validated = validate_analysis_input(
            AnalysisInput(input_type=input_type, value=raw_value or "")
        )
        content = validated.value
        source_value = "texto_manual"
    elif input_type == InputType.URL:
        validated = validate_analysis_input(
            AnalysisInput(input_type=input_type, value=raw_value or "")
        )
        extraction = content_extractor.extract_from_url(validated.value)
        content = extraction["text"]
        source_value = validated.value
    elif input_type == InputType.FILE:
        file_result = file_reader_service.read_uploaded_file(uploaded_file)
        content = file_result["text"]
        source_value = file_result["filename"]
    else:
        raise ValueError("Tipo de entrada inválido.")

    result = sentiment_service.analyze_text(
        text=content,
        source_type=input_type.value,
        source_value=source_value,
    )
    history_service.append_result(result)
    return result


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
        mode = InputType(input_type)
        raw_value = text_value if mode == InputType.TEXT else url_value if mode == InputType.URL else None

        result = _perform_analysis(
            input_type=mode,
            raw_value=raw_value,
            uploaded_file=file_value,
            content_extractor=content_extractor,
            file_reader_service=file_reader_service,
            sentiment_service=sentiment_service,
            history_service=history_service,
        )

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
        mode = InputType(input_type)
        raw_value = text_value if mode == InputType.TEXT else url_value if mode == InputType.URL else None

        result = _perform_analysis(
            input_type=mode,
            raw_value=raw_value,
            uploaded_file=file_value,
            content_extractor=content_extractor,
            file_reader_service=file_reader_service,
            sentiment_service=sentiment_service,
            history_service=history_service,
        )
        return JSONResponse(content=result)
    except (ValueError, ContentExtractionError, FileReaderError, SentimentServiceError) as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
