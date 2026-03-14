# 1. Define tipos de entrada possíveis para análise (texto, URL ou arquivo).
# 2. Cria modelos de dados com Pydantic para validar entradas e saídas da aplicação.
# 3. Representa itens de palavras-chave com seus respectivos scores de relevância.
# 4. Estrutura o resultado da análise de sentimentos, incluindo confiança, polaridade e estatísticas do texto.
# 5. Garante consistência e tipagem forte para os dados processados, facilitando manutenção e integração.

# Importa suporte para anotações futuras de tipo (permite usar tipos modernos em versões antigas do Python)
from __future__ import annotations

# Importa Enum para criar tipos enumerados (valores fixos)
from enum import Enum
# Importa Literal para restringir valores possíveis de uma variável
from typing import Literal

# Importa BaseModel e Field da biblioteca Pydantic para validação de dados
from pydantic import BaseModel, Field


# Cria um Enum para definir os tipos de entrada aceitos
class InputType(str, Enum):
    TEXT = "text"   # Entrada de texto puro
    URL = "url"     # Entrada via URL
    FILE = "file"   # Entrada via arquivo


# Modelo para representar a entrada de análise
class AnalysisInput(BaseModel):
    input_type: InputType              # Tipo da entrada (texto, URL ou arquivo)
    value: str = Field(min_length=1)   # Valor da entrada, deve ter pelo menos 1 caractere


# Modelo para representar uma palavra-chave encontrada na análise
class KeywordItem(BaseModel):
    keyword: str   # Palavra-chave identificada
    score: float   # Relevância da palavra-chave (pontuação)


# Modelo para representar o resultado completo da análise de sentimentos
class SentimentResult(BaseModel):
    sentiment: Literal["positivo", "negativo", "neutro"]  # Sentimento identificado
    confidence: float          # Nível de confiança da análise
    polarity: float            # Polaridade do texto (positivo/negativo)
    summary: str               # Resumo da análise
    keywords: list[KeywordItem] # Lista de palavras-chave relevantes
    text_length_chars: int     # Quantidade de caracteres do texto
    text_length_words: int     # Quantidade de palavras do texto
    sentence_count: int        # Número de sentenças no texto
    processing_time_ms: int    # Tempo de processamento em milissegundos
    distribution: dict[str, float] # Distribuição dos sentimentos (ex.: {"positivo":0.7})
    cleaned_text: str          # Texto limpo após pré-processamento
    source_type: str           # Tipo da fonte (texto, URL ou arquivo)
    source_value: str          # Valor da fonte original
    model_name: str            # Nome do modelo usado na análise
    analyzed_at: str           # Data/hora em que a análise foi feita
