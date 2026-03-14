from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    def __init__(self, history_file: str | None = None) -> None:
        self.history_path = Path(history_file or settings.history_file)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []

        try:
            return json.loads(self.history_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("History file is corrupted. Returning empty history.")
            return []

    def append_result(self, result: dict[str, Any], max_items: int = 30) -> None:
        history = self.load_history()
        history.insert(0, result)
        history = history[:max_items]
        self.history_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def clear_history(self) -> None:
        self.history_path.write_text("[]", encoding="utf-8")
