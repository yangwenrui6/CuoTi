"""详情对话框控制器 - 业务逻辑"""

from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DetailDialogController:
    """详情对话框控制器 - 处理业务逻辑"""
    
    def __init__(self, question_service, question_data: Dict[str, Any], event_bus=None):
        """
        初始化控制器
        
        Args:
            question_service: QuestionService实例
            question_data: 题目数据
            event_bus: 事件总线（可选）
        """
        self.question_service = question_service
        self.question_data = question_data
        self.original_data = question_data.copy()
        self.event_bus = event_bus
        
        logger.debug(f"DetailDialogController初始化，题目ID: {question_data.get('id')}")
    
    def has_changes(self, current_data: Dict[str, Any]) -> bool:
        """
        检查是否有修改
        
        Args:
            current_data: 当前数据（从UI获取）
        
        Returns:
            是否有修改
        """
        # 检查可编辑字段是否有变化
        fields = ['content', 'my_answer', 'answer', 'explanation']
        
        for field in fields:
            # 处理None值，转换为空字符串
            current_value = (current_data.get(field) or '').strip()
            original_value = (self.original_data.get(field) or '').strip()
            
            if current_value != original_value:
                logger.debug(f"字段 '{field}' 已修改")
                return True
        
        return False
    
    def save_changes(self, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        保存修改
        
        Args:
            updates: 更新的字段
        
        Returns:
            (成功标志, 消息)
        """
        question_id = self.question_data.get('id')
        
        if not question_id:
            logger.error("题目ID不存在，无法保存")
            return False, "题目ID不存在"
        
        try:
            # 调用服务层更新
            success, message = self.question_service.update_question(
                question_id, updates
            )
            
            if success:
                logger.info(f"题目 {question_id} 更新成功")
                
                # 更新原始数据，避免重复提示
                for key, value in updates.items():
                    self.original_data[key] = value
                
                # 发布事件
                if self.event_bus:
                    try:
                        from mistake_book.ui.events.events import QuestionUpdatedEvent
                        self.event_bus.publish(QuestionUpdatedEvent(
                            question_id=question_id,
                            updates=updates
                        ))
                        logger.debug(f"QuestionUpdatedEvent已发布，题目ID: {question_id}")
                    except ImportError:
                        # 事件系统还未完全集成，忽略
                        logger.warning("无法导入QuestionUpdatedEvent")
                        pass
            else:
                logger.warning(f"题目 {question_id} 更新失败: {message}")
            
            return success, message
            
        except Exception as e:
            logger.error(f"保存修改失败: {e}", exc_info=True)
            return False, f"保存失败: {str(e)}"
