from app.services.sentiment_service import SentimentService


class FakeSentimentService(SentimentService):
    def __init__(self) -> None:
        pass

    def _aggregate_scores(self, chunks: list[str]) -> dict[str, float]:
        return {"positivo": 0.7, "negativo": 0.1, "neutro": 0.2}

    def _extract_keywords(self, text: str) -> list[dict[str, float]]:
        return [{"keyword": "produto", "score": 1.2}]


def test_derive_metrics():
    sentiment, confidence, polarity = SentimentService._derive_metrics(
        {"positivo": 0.65, "negativo": 0.15, "neutro": 0.20}
    )
    assert sentiment == "positivo"
    assert confidence == 0.65
    assert polarity == 0.50


def test_analyze_text_returns_expected_keys():
    service = FakeSentimentService()
    result = service.analyze_text(
        text="Gostei muito do produto. A experiência foi excelente e muito positiva.",
        source_type="text",
        source_value="texto_manual",
    )

    assert result["sentiment"] == "positivo"
    assert "summary" in result
    assert "distribution" in result
    assert result["text_length_words"] > 0
