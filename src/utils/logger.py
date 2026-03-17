import logging
from pathlib import Path


def setup_logging(name: str = "insurance_ai_weekly") -> logging.Logger:
    Path("logs").mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 중복 핸들러 방지
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    file_handler = logging.FileHandler("logs/latest.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "insurance_ai_weekly") -> logging.Logger:
    setup_logging(name)
    return logging.getLogger(name)
