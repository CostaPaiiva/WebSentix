from __future__ import annotations

from urllib.parse import urlparse

from app.models.schemas import AnalysisInput, InputType


def validate_url(url: str) -> str:
    url = (url or "").strip()

    if not url:
        raise ValueError("A URL não pode estar vazia.")

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("A URL deve iniciar com http:// ou https://")

    if not parsed.netloc:
        raise ValueError("A URL informada é inválida.")

    return url


def validate_analysis_input(data: AnalysisInput) -> AnalysisInput:
    value = (data.value or "").strip()

    if data.input_type == InputType.TEXT:
        if len(value) < 3:
            raise ValueError("Informe um texto com conteúdo suficiente para análise.")
        data.value = value
        return data

    if data.input_type == InputType.URL:
        data.value = validate_url(value)
        return data

    if data.input_type == InputType.FILE:
        return data

    raise ValueError("Tipo de entrada inválido.")
