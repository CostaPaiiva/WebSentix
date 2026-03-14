from __future__ import annotations

from app.services.content_extractor import ContentExtractor
from app.services.export_service import ExportService
from app.services.file_reader_service import FileReaderService
from app.services.history_service import HistoryService
from app.services.sentiment_service import SentimentService

content_extractor = ContentExtractor()
file_reader_service = FileReaderService()
history_service = HistoryService()
export_service = ExportService()
sentiment_service = SentimentService()


def get_content_extractor() -> ContentExtractor:
    return content_extractor


def get_file_reader_service() -> FileReaderService:
    return file_reader_service


def get_history_service() -> HistoryService:
    return history_service


def get_export_service() -> ExportService:
    return export_service


def get_sentiment_service() -> SentimentService:
    return sentiment_service
