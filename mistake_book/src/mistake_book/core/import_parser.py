"""CSV/图片批量导入解析"""

from pathlib import Path
from typing import List, Dict, Any
import csv


class ImportParser:
    """导入解析器"""
    
    def parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """解析CSV文件"""
        questions = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
        return questions
    
    def parse_images(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """批量解析图片（需要OCR）"""
        # TODO: 集成OCR服务
        return []
