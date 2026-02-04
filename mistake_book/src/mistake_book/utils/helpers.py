"""日期格式化和路径安全等工具函数"""

from datetime import datetime
from pathlib import Path


def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    return dt.strftime(fmt)


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename
