from __future__ import annotations

import re
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import yake
from transformers import pipeline

from app.config.settings import settings
from app.utils.text_cleaner import clean_text, split_sentences


class SentimentServiceError(Exception):
    """Erro na análise de sentimentos."""


class SentimentService:
    """
    Serviço de análise de sentimentos para português.

    Escolha técnica:
    - modelo multilíngue com melhor cobertura para português
    - YAKE para palavras-chave
    - sumarização heurística leve, sem dependência de outro modelo
    """

    LABEL_MAP = {
        "positive": "positivo",
        "neutral": "neutro",
        "negative": "negativo",
    }

    def __init__(self) -> None:
        self._classifier = pipeline(
            task="text-classification",
            model=settings.model_name,
            tokenizer=settings.model_name,
            top_k=None,
            truncation=True,
        )
        self._keyword_extractor = yake.KeywordExtractor(
            lan="pt",
            n=2,
            dedupLim=0.9,
            top=8,
            features=None,
        )

    def analyze_text(self, text: str, source_type: str, source_value: str) -> dict[str, Any]:
        start = time.perf_counter()
        cleaned = clean_text(text)

        if len(cleaned.split()) < 3:
            raise SentimentServiceError("O texto informado é muito curto para análise confiável.")

        chunks = self._chunk_text(cleaned)
        scores = self._aggregate_scores(chunks)
        sentiment, confidence, polarity = self._derive_metrics(scores)
        summary = self._summarize(cleaned)
        keywords = self._extract_keywords(cleaned)

        processing_ms = int((time.perf_counter() - start) * 1000)
        sentences = split_sentences(cleaned)

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "polarity": polarity,
            "summary": summary,
            "keywords": keywords,
            "text_length_chars": len(cleaned),
            "text_length_words": len(cleaned.split()),
            "sentence_count": len(sentences),
            "processing_time_ms": processing_ms,
            "distribution": scores,
            "cleaned_text": cleaned,
            "source_type": source_type,
            "source_value": source_value,
            "model_name": settings.model_name,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _chunk_text(self, text: str, max_chars: int = 700) -> list[str]:
        sentences = split_sentences(text)
        if not sentences:
            return [text[:max_chars]]

        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            tentative = f"{current} {sentence}".strip()
            if len(tentative) <= max_chars:
                current = tentative
            else:
                if current:
                    chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks or [text[:max_chars]]

    def _aggregate_scores(self, chunks: list[str]) -> dict[str, float]:
        aggregate = {"positivo": 0.0, "negativo": 0.0, "neutro": 0.0}

        try:
            for chunk in chunks:
                raw_predictions = self._classifier(chunk)
                predictions = raw_predictions[0] if isinstance(raw_predictions, list) else raw_predictions

                for item in predictions:
                    label = item["label"].lower()
                    mapped = self.LABEL_MAP.get(label)
                    if mapped:
                        aggregate[mapped] += float(item["score"])

            chunk_count = max(len(chunks), 1)
            normalized = {key: value / chunk_count for key, value in aggregate.items()}
            total = sum(normalized.values()) or 1.0
            return {key: value / total for key, value in normalized.items()}

        except Exception as exc:
            raise SentimentServiceError(
                "Falha ao executar o modelo de análise de sentimentos."
            ) from exc

    @staticmethod
    def _derive_metrics(scores: dict[str, float]) -> tuple[str, float, float]:
        sentiment = max(scores, key=scores.get)
        confidence = scores[sentiment]
        polarity = scores["positivo"] - scores["negativo"]
        return sentiment, confidence, polarity

    def _extract_keywords(self, text: str) -> list[dict[str, float]]:
        keywords = self._keyword_extractor.extract_keywords(text)
        return [
            {"keyword": keyword, "score": round(1 / (score + 1e-9), 4)}
            for keyword, score in keywords[:6]
        ]

    def _summarize(self, text: str, max_sentences: int = 3) -> str:
        sentences = split_sentences(text)
        if len(sentences) <= max_sentences:
            return text

        word_freq = self._build_frequency_map(text)
        ranked_sentences = []

        for sentence in sentences:
            words = re.findall(r"\b[\wÀ-ÿ]+\b", sentence.lower())
            if not words:
                continue
            score = sum(word_freq.get(word, 0) for word in words) / len(words)
            ranked_sentences.append((score, sentence))

        ranked_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = {sentence for _, sentence in ranked_sentences[:max_sentences]}
        ordered_summary = [sentence for sentence in sentences if sentence in top_sentences]
        return " ".join(ordered_summary).strip()

    @staticmethod
    def _build_frequency_map(text: str) -> dict[str, int]:
        stopwords_pt = {
            "a", "o", "e", "de", "do", "da", "dos", "das", "em", "um", "uma",
            "para", "com", "no", "na", "nos", "nas", "por", "que", "se", "ao",
            "aos", "as", "os", "é", "foi", "ser", "são", "como", "mais", "menos",
            "muito", "muita", "muitas", "muitos", "já", "também", "ou", "não",
            "sim", "isso", "isto", "aquele", "aquela", "sobre", "entre", "até",
            "após", "sem", "há", "era", "sua", "seu", "suas", "seus", "ele", "ela",
        }
        words = re.findall(r"\b[\wÀ-ÿ]+\b", text.lower())
        filtered = [word for word in words if len(word) > 2 and word not in stopwords_pt]
        return dict(Counter(filtered))
