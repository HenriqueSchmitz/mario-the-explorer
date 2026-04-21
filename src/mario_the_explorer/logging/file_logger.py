import coloredlogs
import logging
from datetime import datetime
from logging import Logger, FileHandler, Formatter

def get_file_logger(run_name: str, log_level: str) -> Logger:
    logger = logging.getLogger(run_name)
    logger.setLevel(log_level)
    coloredlogs.install(level=log_level, logger=logger, fmt="%(asctime)s [%(levelname)s] %(message)s", isatty=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_name = f"{run_name}_{timestamp}.log"
    file_handler = FileHandler(log_file_name)
    file_handler.setLevel(log_level)
    formatter = Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f"Session log for run {run_name} with level [{log_level}] initialized at: {log_file_name}")
    return logger