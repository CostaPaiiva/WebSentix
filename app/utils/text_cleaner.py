from __future__ import annotations

import html
import re
import unicodedata


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def remove_extra_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = normalize_unicode(text)
    text = strip_html(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", " ", text)
    text = remove_extra_spaces(text)
    return text


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]
