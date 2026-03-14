from __future__ import annotations

import logging
from logging import Logger

from app.config.settings import settings


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper(), logging.INFO),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

    return logger
