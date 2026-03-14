from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class InputType(str, Enum):
    TEXT = "text"
    URL = "url"
    FILE = "file"


class AnalysisInput(BaseModel):
    input_type: InputType
    value: str = Field(min_length=1)


class KeywordItem(BaseModel):
    keyword: str
    score: float


class SentimentResult(BaseModel):
    sentiment: Literal["positivo", "negativo", "neutro"]
    confidence: float
    polarity: float
    summary: str
    keywords: list[KeywordItem]
    text_length_chars: int
    text_length_words: int
    sentence_count: int
    processing_time_ms: int
    distribution: dict[str, float]
    cleaned_text: str
    source_type: str
    source_value: str
    model_name: str
    analyzed_at: str
