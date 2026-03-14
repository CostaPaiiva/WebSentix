from __future__ import annotations

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.config.settings import settings
from app.utils.logger import get_logger
from app.utils.text_cleaner import clean_text
from app.utils.validators import validate_url

logger = get_logger(__name__)


class ContentExtractionError(Exception):
    """Erro de extração de conteúdo."""


class ContentExtractor:
    _REMOVABLE_TAGS = [
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
        "footer",
        "header",
        "nav",
        "aside",
        "form",
        "button",
    ]

    _NOISE_PATTERNS = [
        re.compile(r"cookie", re.IGNORECASE),
        re.compile(r"newsletter", re.IGNORECASE),
        re.compile(r"subscribe", re.IGNORECASE),
        re.compile(r"assine", re.IGNORECASE),
        re.compile(r"publicidade", re.IGNORECASE),
        re.compile(r"anúncio", re.IGNORECASE),
        re.compile(r"advert", re.IGNORECASE),
        re.compile(r"menu", re.IGNORECASE),
    ]

    def extract_from_url(self, url: str) -> dict[str, Any]:
        normalized_url = validate_url(url)
        html = self._download_html(normalized_url)
        text = self._extract_relevant_text(html)

        if not text or len(text.split()) < 20:
            raise ContentExtractionError(
                "Não foi possível extrair conteúdo textual relevante da URL informada."
            )

        cleaned = clean_text(text)[: settings.max_content_chars]

        return {
            "url": normalized_url,
            "text": cleaned,
            "raw_length": len(text),
            "cleaned_length": len(cleaned),
        }

    def _download_html(self, url: str) -> str:
        headers = {"User-Agent": settings.user_agent}

        try:
            with httpx.Client(
                headers=headers,
                follow_redirects=True,
                timeout=settings.request_timeout,
            ) as client:
                response = client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    raise ContentExtractionError(
                        "A URL informada não parece apontar para uma página HTML válida."
                    )

                return response.text

        except httpx.HTTPStatusError as exc:
            logger.warning("HTTP status error for %s: %s", url, exc)
            raise ContentExtractionError(
                "A página retornou erro HTTP e não pôde ser acessada."
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("HTTP request error for %s: %s", url, exc)
            raise ContentExtractionError(
                "Não foi possível acessar a URL. Verifique conexão, domínio ou restrições do site."
            ) from exc

    def _extract_relevant_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(self._REMOVABLE_TAGS):
            tag.decompose()

        for element in soup.find_all(True):
            class_str = " ".join(element.get("class", [])) if element.get("class") else ""
            id_str = element.get("id", "")
            searchable = f"{class_str} {id_str}".strip()

            if searchable and any(pattern.search(searchable) for pattern in self._NOISE_PATTERNS):
                element.decompose()

        candidates: list[tuple[int, str]] = []
        selectors = ["article", "main", "[role='main']", "section", "div"]

        for selector in selectors:
            for node in soup.select(selector):
                text = node.get_text(" ", strip=True)
                score = self._score_candidate_text(text)
                if score > 0:
                    candidates.append((score, text))

        if not candidates:
            return clean_text(soup.get_text(" ", strip=True))

        candidates.sort(key=lambda item: item[0], reverse=True)
        return clean_text(candidates[0][1])

    @staticmethod
    def _score_candidate_text(text: str) -> int:
        words = text.split()
        if len(words) < 20:
            return 0

        sentence_like = len(re.findall(r"[.!?]", text))
        paragraphs_like = len(re.findall(r"\n{2,}", text))
        return len(words) + sentence_like * 10 + paragraphs_like * 5
