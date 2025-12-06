import os
import sys
import logging
from logging.handlers import RotatingFileHandler

class InfoFilter(logging.Filter):
    """Chỉ cho phép log INFO vào file info.log"""
    def filter(self, record):
        return record.levelno == logging.INFO

def setup_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    logger.setLevel(logging.DEBUG)  # bắt cả DEBUG, nhưng handler sẽ lọc

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # chỉ in từ INFO trở lên
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'), 
        maxBytes=1000000, 
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 3️⃣ File handler cho info.log
    info_handler = RotatingFileHandler(
        os.path.join(log_dir, 'info.log'), 
        maxBytes=1000000, 
        backupCount=5,
        encoding='utf-8'
    )

    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    logger.propagate = False

    return logger
