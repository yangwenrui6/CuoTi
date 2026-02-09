"""复习对话框控制器 - 业务逻辑"""

from typing import List, Dict, Any, Optional, Tuple
from mistake_book.config.constants import ReviewResult
import logging

logger = logging.getLogger(__name__)


class ReviewDialogController:
    """复习对话框控制器 - 处理复习业务逻辑"""
    
    def __init__(self, review_service, questions: List[Dict[str, Any]], event_bus=None):
        """
        初始化控制器
        
        Args:
            review_service: ReviewService实例
            questions: 待复习题目列表
            event_bus: 事件总线（可选）
        """
        self.review_service = review_service
        self.questions = questions
        self.current_index = 0
        self.reviewed_count = 0
        self.event_bus = event_bus
        
        logger.info(f"初始化复习控制器，共 {len(questions)} 道题目")
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        获取当前题目
        
        Returns:
            当前题目数据，如果没有更多题目则返回None
        """
        if 0 <= self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            logger.debug(f"获取当前题目: index={self.current_index}, id={question.get('id')}")
            return question
        
        logger.debug(f"没有更多题目: index={self.current_index}, total={len(self.questions)}")
        return None
    
    def submit_review(self, quality: int) -> bool:
        """
        提交复习结果
        
        Args:
            quality: 质量评分 (0-5)，对应ReviewResult枚举值
        
        Returns:
            是否还有下一题
        """
        question = self.get_current_question()
        if not question:
            logger.warning("提交复习失败：没有当前题目")
            return False
        
        question_id = question.get('id')
        
        # 将质量评分转换为ReviewResult枚举
        try:
            result = ReviewResult(quality)
        except ValueError:
            logger.error(f"无效的质量评分: {quality}")
            return False
        
        logger.info(f"提交复习结果: question_id={question_id}, quality={quality}, result={result}")
        
        # 调用服务层更新复习数据
        success, message, updates = self.review_service.process_review_result(
            question_id, result
        )
        
        if success:
            logger.info(f"复习数据更新成功: {message}")
        else:
            logger.error(f"复习数据更新失败: {message}")
        
        # 无论保存是否成功，都继续下一题
        self.reviewed_count += 1
        self.current_index += 1
        
        # 检查是否完成所有题目
        has_next = self.current_index < len(self.questions)
        
        if not has_next:
            # 所有题目复习完成，发布事件
            logger.info(f"复习完成，共复习 {self.reviewed_count} 道题目")
            if self.event_bus:
                from mistake_book.ui.events.events import ReviewCompletedEvent
                self.event_bus.publish(ReviewCompletedEvent(
                    reviewed_count=self.reviewed_count
                ))
        
        return has_next
    
    def get_progress(self) -> Tuple[int, int]:
        """
        获取复习进度
        
        Returns:
            (当前题号, 总题数)，题号从1开始
        """
        current = self.current_index + 1
        total = len(self.questions)
        logger.debug(f"获取进度: {current}/{total}")
        return current, total
    
    def get_reviewed_count(self) -> int:
        """
        获取已复习题目数量
        
        Returns:
            已复习的题目数量
        """
        return self.reviewed_count
    
    def has_more_questions(self) -> bool:
        """
        是否还有更多题目
        
        Returns:
            是否还有未复习的题目
        """
        return self.current_index < len(self.questions)
    
    def reset(self):
        """重置控制器状态（用于重新开始复习）"""
        logger.info("重置复习控制器")
        self.current_index = 0
        self.reviewed_count = 0
