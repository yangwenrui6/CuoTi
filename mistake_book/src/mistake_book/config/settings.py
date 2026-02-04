"""动态配置管理"""

from dataclasses import dataclass, field
from typing import Dict, Any
import json
from pathlib import Path


@dataclass
class Settings:
    """应用配置"""
    theme: str = "light"  # light/dark
    database_path: str = ""
    backup_enabled: bool = True
    backup_interval_days: int = 7
    ocr_engine: str = "paddleocr"  # paddleocr/tesseract
    review_algorithm_params: Dict[str, Any] = field(default_factory=lambda: {
        "easy_bonus": 1.3,
        "interval_modifier": 1.0,
        "max_interval": 365
    })
    
    @classmethod
    def load(cls, config_path: Path) -> "Settings":
        """从文件加载配置"""
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self, config_path: Path):
        """保存配置到文件"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=2, ensure_ascii=False)
