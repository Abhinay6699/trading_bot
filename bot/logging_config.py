"""
bot/logging_config.py — Centralised logging setup for the trading bot.

Design decisions:
- Single root logger named 'trading_bot' so all child loggers (bot.client,
  bot.orders, …) inherit the same handlers automatically.
- RotatingFileHandler caps each log file at 5 MB with 3 backups — suitable
  for long-running bots without bloating disk.
- StreamHandler writes WARNING+ to the console so the terminal stays clean
  while INFO-level API traffic goes exclusively to the file.
- Call configure_logging() once at application start (in cli.py).
- Use get_logger(__name__) in every module to obtain a child logger.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent  # project root
LOG_FILE = LOG_DIR / "trading_bot.log"

_ROOT_LOGGER_NAME = "trading_bot"
_FILE_LEVEL = logging.INFO
_CONSOLE_LEVEL = logging.WARNING
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3

_FILE_FMT = (
    "%(asctime)s  %(levelname)-8s  %(name)s:%(lineno)d  %(message)s"
)
_CONSOLE_FMT = "%(levelname)s: %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"

_configured = False  # guard against calling configure_logging() twice


def configure_logging() -> None:
    """
    Set up the root 'trading_bot' logger with:
    - RotatingFileHandler → trading_bot.log (INFO level)
    - StreamHandler       → stderr         (WARNING level)

    Safe to call multiple times; subsequent calls are no-ops.
    """
    global _configured
    if _configured:
        return

    root = logging.getLogger(_ROOT_LOGGER_NAME)
    root.setLevel(logging.DEBUG)  # let handlers filter individually

    # --- File handler ---------------------------------------------------
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(LOG_FILE),
        mode="a",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(_FILE_LEVEL)
    file_handler.setFormatter(
        logging.Formatter(fmt=_FILE_FMT, datefmt=_DATE_FMT)
    )

    # --- Console handler ------------------------------------------------
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(_CONSOLE_LEVEL)
    console_handler.setFormatter(logging.Formatter(fmt=_CONSOLE_FMT))

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the 'trading_bot' namespace.

    Usage
    -----
    from bot.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Hello from %s", __name__)
    """
    # Ensure the root logger is configured even if configure_logging() was
    # not called explicitly (e.g. during unit tests).
    configure_logging()

    # If name already starts with the root, use it verbatim to avoid
    # double-prefixing (e.g. 'bot.client' → 'trading_bot.bot.client').
    if not name.startswith(_ROOT_LOGGER_NAME):
        full_name = f"{_ROOT_LOGGER_NAME}.{name}"
    else:
        full_name = name

    return logging.getLogger(full_name)
