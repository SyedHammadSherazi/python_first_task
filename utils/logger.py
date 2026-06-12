import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def get_logger(name="task_cli"):
    """
    Centralized logger.

    Features:
    - Clean readable log format
    - File logging
    - Console logging
    - Log rotation
    """

    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    # Prevent logs from being duplicated by parent/root logger
    logger.propagate = False

    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_task_started(task_name):
    logger = get_logger()
    logger.info(f"TASK STARTED | {task_name}")


def log_task_completed(task_name):
    logger = get_logger()
    logger.info(f"TASK COMPLETED | {task_name}")


def log_task_error(task_name, error):
    logger = get_logger()
    logger.exception(f"TASK ERROR | {task_name} | Error: {error}")