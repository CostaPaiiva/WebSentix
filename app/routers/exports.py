from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.dependencies import get_export_service, get_history_service
from app.services.export_service import ExportService
from app.services.history_service import HistoryService

router = APIRouter()


def _get_latest_result(history_service: HistoryService) -> dict:
    history = history_service.load_history()
    if not history:
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada para exportação.")
    return history[0]


@router.get("/latest/pdf")
def export_latest_pdf(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)
    pdf_bytes = export_service.export_single_result_pdf(result)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.pdf"'},
    )


@router.get("/latest/txt")
def export_latest_txt(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)
    txt_bytes = export_service.export_single_result_txt(result)
    return Response(
        content=txt_bytes,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.txt"'},
    )


@router.get("/latest/excel")
def export_latest_excel(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    result = _get_latest_result(history_service)
    excel_bytes = export_service.export_single_result_excel(result)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="resultado_analise.xlsx"'},
    )


@router.get("/history/excel")
def export_history_excel(
    export_service: ExportService = Depends(get_export_service),
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    history = history_service.load_history()
    excel_bytes = export_service.export_history_excel(history)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="historico_analises.xlsx"'},
    )
