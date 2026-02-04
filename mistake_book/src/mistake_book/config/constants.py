"""枚举和常量定义"""

from enum import Enum


class MasteryLevel(Enum):
    """掌握度等级"""
    NOT_STARTED = 0  # 未开始
    LEARNING = 1     # 学习中
    FAMILIAR = 2     # 熟悉
    MASTERED = 3     # 掌握
    PERFECT = 4      # 完全掌握


class QuestionType(Enum):
    """错题类型"""
    SINGLE_CHOICE = "单选题"
    MULTIPLE_CHOICE = "多选题"
    TRUE_FALSE = "判断题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "简答题"
    CALCULATION = "计算题"
    OTHER = "其他"


class ReviewResult(Enum):
    """复习结果"""
    AGAIN = 0      # 完全不会
    HARD = 1       # 困难
    GOOD = 2       # 良好
    EASY = 3       # 简单
