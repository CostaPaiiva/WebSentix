from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_history_service
from app.services.history_service import HistoryService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    history_service: HistoryService = Depends(get_history_service),
) -> HTMLResponse:
    history = history_service.load_history()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "history": history[:10],
            "result": None,
            "error": None,
            "active_mode": "text",
        },
    )
