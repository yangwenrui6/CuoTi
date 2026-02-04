"""复习服务 - 处理复习相关的业务逻辑"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from mistake_book.core.data_manager import DataManager
from mistake_book.core.review_scheduler import ReviewScheduler
from mistake_book.config.constants import ReviewResult


class ReviewService:
    """复习服务类 - 封装复习相关的业务逻辑"""
    
    def __init__(self, data_manager: DataManager, scheduler: ReviewScheduler):
        """
        初始化复习服务
        
        Args:
            data_manager: 数据管理器
            scheduler: 复习调度器
        """
        self.data_manager = data_manager
        self.scheduler = scheduler
    
    def get_due_questions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取需要复习的题目
        
        Args:
            filters: 筛选条件（可选）
        
        Returns:
            到期题目列表
        """
        # 获取所有题目
        all_questions = self.data_manager.search_questions(filters or {})
        
        # 筛选到期题目
        due_questions = self.scheduler.get_due_questions(all_questions)
        
        return due_questions
    
    def process_review_result(
        self, 
        question_id: int, 
        result: ReviewResult,
        time_spent: Optional[int] = None
    ) -> tuple[bool, str, Dict[str, Any]]:
        """
        处理复习结果
        
        Args:
            question_id: 题目ID
            result: 复习结果
            time_spent: 耗时（秒）
        
        Returns:
            (成功标志, 消息, 更新后的数据)
        """
        try:
            # 获取题目当前数据
            question = self.data_manager.get_question(question_id)
            if not question:
                return False, "题目不存在", {}
            
            # 计算新的复习数据
            interval, reps, ef = self.scheduler.calculate_next_review(
                question.get('interval', 0),
                question.get('repetitions', 0),
                question.get('easiness_factor', 2.5),
                result
            )
            
            # 计算下次复习日期
            next_review = datetime.now() + timedelta(days=interval)
            
            # 准备更新数据
            updates = {
                'interval': interval,
                'repetitions': reps,
                'easiness_factor': ef,
                'mastery_level': result.value,
                'next_review_date': next_review
            }
            
            # 保存到数据库
            success = self.data_manager.update_question(question_id, updates)
            
            if success:
                # TODO: 可以在这里添加复习记录
                return True, "复习数据已更新", updates
            else:
                return False, "更新失败", {}
                
        except Exception as e:
            return False, f"处理失败: {str(e)}", {}
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """
        获取复习统计数据
        
        Returns:
            统计数据字典
        """
        try:
            # 获取基础统计
            stats = self.data_manager.get_statistics()
            
            # 获取到期题目数量
            due_questions = self.get_due_questions()
            stats['due_count'] = len(due_questions)
            
            # 计算今日复习数量（可以从复习记录表查询）
            stats['today_reviewed'] = 0  # TODO: 实现
            
            return stats
        except Exception as e:
            return {
                'total_questions': 0,
                'mastered': 0,
                'learning': 0,
                'due_count': 0,
                'today_reviewed': 0,
                'error': str(e)
            }
    
    def calculate_next_review_info(
        self, 
        question: Dict[str, Any], 
        result: ReviewResult
    ) -> Dict[str, Any]:
        """
        预览复习结果（不保存）
        
        Args:
            question: 题目数据
            result: 复习结果
        
        Returns:
            预览数据
        """
        interval, reps, ef = self.scheduler.calculate_next_review(
            question.get('interval', 0),
            question.get('repetitions', 0),
            question.get('easiness_factor', 2.5),
            result
        )
        
        next_review = datetime.now() + timedelta(days=interval)
        
        return {
            'interval': interval,
            'repetitions': reps,
            'easiness_factor': ef,
            'next_review_date': next_review,
            'mastery_level': result.value
        }
