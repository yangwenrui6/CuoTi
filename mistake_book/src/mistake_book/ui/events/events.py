"""事件定义"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Event:
    """基础事件类"""
    pass


@dataclass
class QuestionAddedEvent(Event):
    """题目添加事件"""
    question_id: int
    question_data: Dict[str, Any]


@dataclass
class QuestionUpdatedEvent(Event):
    """题目更新事件"""
    question_id: int
    updates: Dict[str, Any]


@dataclass
class QuestionDeletedEvent(Event):
    """题目删除事件"""
    question_id: int


@dataclass
class ReviewCompletedEvent(Event):
    """复习完成事件"""
    reviewed_count: int


@dataclass
class OCRCompletedEvent(Event):
    """OCR识别完成事件"""
    text: str
    success: bool


@dataclass
class FilterChangedEvent(Event):
    """筛选条件变化事件"""
    filters: Dict[str, Any]
