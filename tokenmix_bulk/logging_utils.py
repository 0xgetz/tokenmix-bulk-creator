"""Structured logging helpers shared across the package."""

from __future__ import annotations

import logging
import sys

_LEVEL_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[41m",
}
_RESET = "\033[0m"


class _ColorFormatter(logging.Formatter):
    """Small formatter that colourises the level name on TTYs."""

    def __init__(self, use_color: bool) -> None:
        super().__init__("%(asctime)s %(levelname)-8s %(message)s", "%H:%M:%S")
        self._use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if not self._use_color:
            return text
        color = _LEVEL_COLORS.get(record.levelname, "")
        return text.replace(record.levelname, f"{color}{record.levelname}{_RESET}", 1)


def get_logger(name: str = "tokenmix_bulk", level: int = logging.INFO) -> logging.Logger:
    """Return a package logger configured exactly once."""

    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(level)
        return logger

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_ColorFormatter(use_color=sys.stderr.isatty()))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger
