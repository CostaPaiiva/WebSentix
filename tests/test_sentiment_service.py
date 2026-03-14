from app.services.sentiment_service import SentimentService  # Importa o serviço de análise de sentimentos


# Cria uma classe falsa que herda de SentimentService para simular resultados previsíveis
class FakeSentimentService(SentimentService):
    def __init__(self) -> None:  # Construtor vazio, não inicializa nada
        pass

    def _aggregate_scores(self, chunks: list[str]) -> dict[str, float]:
        # Simula a agregação de sentimentos retornando valores fixos
        return {"positivo": 0.7, "negativo": 0.1, "neutro": 0.2}

    def _extract_keywords(self, text: str) -> list[dict[str, float]]:
        # Simula a extração de palavras-chave retornando uma lista fixa
        return [{"keyword": "produto", "score": 1.2}]


def test_derive_metrics():  # Testa o método estático _derive_metrics
    sentiment, confidence, polarity = SentimentService._derive_metrics(
        {"positivo": 0.65, "negativo": 0.15, "neutro": 0.20}  # Dicionário de sentimentos simulado
    )
    assert sentiment == "positivo"   # Verifica se o sentimento dominante é positivo
    assert confidence == 0.65        # Verifica se a confiança corresponde ao valor positivo
    assert polarity == 0.50          # Verifica se a polaridade foi calculada corretamente


def test_analyze_text_returns_expected_keys():  # Testa se analyze_text retorna os campos esperados
    service = FakeSentimentService()  # Usa o serviço falso para garantir resultados previsíveis
    result = service.analyze_text(
        text="Gostei muito do produto. A experiência foi excelente e muito positiva.",  # Texto de entrada
        source_type="text",       # Tipo da fonte
        source_value="texto_manual",  # Valor da fonte
    )

    assert result["sentiment"] == "positivo"  # Verifica se o sentimento detectado é positivo
    assert "summary" in result               