import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "bot.log",
    level: int = logging.INFO,
) -> logging.Logger:
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    full_path = log_path / log_file

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        full_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("togethernet_bot")
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(level)
    discord_logger.addHandler(file_handler)
    discord_logger.addHandler(console_handler)

    return logger