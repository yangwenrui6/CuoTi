"""统一日志配置"""

import logging
from mistake_book.config.paths import get_app_paths


def setup_logger(name: str = "mistake_book") -> logging.Logger:
    """配置日志"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    paths = get_app_paths()
    fh = logging.FileHandler(paths.log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    
    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # 格式化
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
