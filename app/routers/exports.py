# 1. Cria rotas de exportação para resultados de análise em diferentes formatos (PDF, TXT, Excel).
# 2. Usa serviços de histórico e exportação para recuperar e converter dados.
# 3. Implementa função auxiliar para obter o último resultado analisado.
# 4. Configura respostas HTTP com cabeçalhos adequados para download de arquivos.
# 5. Garante tratamento de erros quando não há resultados disponíveis para exportação.

# Importa suporte para anotações futuras de tipo
from __future__ import annotations

# Importa classes do FastAPI para criar rotas e dependências
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

# Importa dependências da aplicação (injeção de serviços)
from app.dependencies import get_export_service, get_history_service
# Importa serviços de exportação e histórico
from app.services.export_service import ExportService
from app.services.history_service import HistoryService

# Cria objeto de roteamento da API
router = APIRouter()


# Função auxiliar para obter o último resultado do histórico
def _get_latest_result(history_service: HistoryService) -> dict:
    history = history_service.load_history()  # Carrega histórico
    if not history:  # Se não houver histórico, lança erro 404
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada para exportação.")
    return history[0]  # Retorna o resultado mais recente


# Rota GET para exportar o último resultado em PDF
@router.get("/latest/pdf")
def export_latest_pdf(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)  # Obtém último resultado
    pdf_bytes = export_service.export_single_result_pdf(result)  # Converte para PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.pdf"'},  # Configura download
    )


# Rota GET para exportar o último resultado em TXT
@router.get("/latest/txt")
def export_latest_txt(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)  # Obtém último resultado
    txt_bytes = export_service.export_single_result_txt(result)  # Converte para TXT
    return Response(
        content=txt_bytes,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.txt"'},  # Configura download
    )


# Rota GET para exportar o último resultado em Excel
@router.get("/latest/excel")
def export_latest_excel(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)  # Obtém último resultado
    excel_bytes = export_service.export_single_result_excel(result)  # Converte para Excel
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.xlsx"'},  # Configura download
    )


# Rota GET para exportar todo o histórico em Excel
@router.get("/history/excel")
def export_history_excel(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    history = history_service.load_history()  # Carrega todo o histórico
    excel_bytes = export_service.export_history_excel(history)  # Converte histórico para Excel
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="historico_analises.xlsx"'},  # Configura download
    )
