"""间隔重复算法(SM-2)和复习计划生成"""

from datetime import datetime, timedelta
from typing import List, Tuple
from mistake_book.config.constants import ReviewResult


class ReviewScheduler:
    """基于SM-2算法的复习调度器"""
    
    def __init__(self, easy_bonus: float = 1.3, interval_modifier: float = 1.0):
        self.easy_bonus = easy_bonus
        self.interval_modifier = interval_modifier
    
    def calculate_next_review(
        self,
        current_interval: int,
        repetitions: int,
        easiness_factor: float,
        review_result: ReviewResult
    ) -> Tuple[int, int, float]:
        """
        计算下次复习时间
        
        Returns:
            (新间隔天数, 重复次数, 新难度因子)
        """
        # 更新难度因子
        if review_result == ReviewResult.AGAIN:
            easiness_factor = max(1.3, easiness_factor - 0.2)
            repetitions = 0
            interval = 1
        elif review_result == ReviewResult.HARD:
            easiness_factor = max(1.3, easiness_factor - 0.15)
            interval = max(1, int(current_interval * 1.2))
            repetitions += 1
        elif review_result == ReviewResult.GOOD:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = int(current_interval * easiness_factor)
            repetitions += 1
        else:  # EASY
            easiness_factor = min(2.5, easiness_factor + 0.15)
            interval = int(current_interval * easiness_factor * self.easy_bonus)
            repetitions += 1
        
        # 应用间隔修正
        interval = int(interval * self.interval_modifier)
        interval = max(1, min(interval, 365))  # 限制在1-365天
        
        return interval, repetitions, easiness_factor
    
    def get_due_questions(self, questions: List[dict]) -> List[dict]:
        """获取到期需要复习的题目"""
        today = datetime.now().date()
        return [q for q in questions if q.get("next_review_date", today) <= today]
