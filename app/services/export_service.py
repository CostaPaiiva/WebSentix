from __future__ import annotations

import io
from typing import Any

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ExportService:
    """Exporta resultados em PDF, TXT e Excel."""

    def export_single_result_txt(self, result: dict[str, Any]) -> bytes:
        content = [
            "RELATORIO DE ANALISE DE SENTIMENTOS",
            "=" * 40,
            f"Data/Hora: {result.get('analyzed_at', '-')}",
            f"Origem: {result.get('source_type', '-')}",
            f"Valor de origem: {result.get('source_value', '-')}",
            f"Sentimento: {result.get('sentiment', '-')}",
            f"Confianca: {result.get('confidence', 0):.2%}",
            f"Polaridade: {result.get('polarity', 0):+.3f}",
            f"Caracteres: {result.get('text_length_chars', 0)}",
            f"Palavras: {result.get('text_length_words', 0)}",
            f"Sentencas: {result.get('sentence_count', 0)}",
            f"Tempo de processamento: {result.get('processing_time_ms', 0)} ms",
            "",
            "Resumo:",
            result.get("summary", "-"),
            "",
            "Palavras-chave:",
            ", ".join([item["keyword"] for item in result.get("keywords", [])]) or "-",
            "",
            "Distribuicao:",
            str(result.get("distribution", {})),
            "",
            "Texto processado:",
            result.get("cleaned_text", ""),
        ]
        return "\n".join(content).encode("utf-8")

    def export_single_result_pdf(self, result: dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        _, height = A4
        y = height - 40

        pdf.setTitle("Relatorio de Analise de Sentimentos")
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, "Relatorio de Analise de Sentimentos")
        y -= 30

        pdf.setFont("Helvetica", 10)
        lines = self.export_single_result_txt(result).decode("utf-8").splitlines()

        for line in lines:
            for wrapped in self._wrap_text(line, 95):
                pdf.drawString(40, y, wrapped)
                y -= 14
                if y < 40:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = height - 40

        pdf.save()
        buffer.seek(0)
        return buffer.read()

    def export_single_result_excel(self, result: dict[str, Any]) -> bytes:
        output = io.BytesIO()
        flat_result = result.copy()
        flat_result["keywords"] = ", ".join(
            [item["keyword"] for item in result.get("keywords", [])]
        )
        flat_result["distribution"] = str(result.get("distribution", {}))

        df = pd.DataFrame([flat_result])

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="resultado")

        output.seek(0)
        return output.read()

    def export_history_excel(self, history: list[dict[str, Any]]) -> bytes:
        output = io.BytesIO()
        df = pd.DataFrame(history if history else [])

        if not df.empty:
            if "keywords" in df.columns:
                df["keywords"] = df["keywords"].apply(
                    lambda items: ", ".join([item["keyword"] for item in items]) if isinstance(items, list) else str(items)
                )
            if "distribution" in df.columns:
                df["distribution"] = df["distribution"].astype(str)

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="historico")

        output.seek(0)
        return output.read()

    @staticmethod
    def _wrap_text(text: str, max_chars: int) -> list[str]:
        if not text:
            return [""]

        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            tentative = f"{current} {word}".strip()
            if len(tentative) <= max_chars:
                current = tentative
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines
