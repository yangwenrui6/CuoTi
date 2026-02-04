"""外部能力封装模块"""

from .question_service import QuestionService
from .review_service import ReviewService
from .ui_service import UIService
from .notification import NotificationService
from .ocr_engine import OCREngine, EasyOCREngine, create_ocr_engine

__all__ = [
    "QuestionService",
    "ReviewService",
    "UIService",
    "NotificationService",
    "OCREngine",
    "EasyOCREngine",
    "create_ocr_engine",
]
