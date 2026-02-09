"""添加错题对话框控制器 - 业务逻辑"""

from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AddQuestionController:
    """添加错题控制器 - 处理业务逻辑"""
    
    def __init__(self, question_service, event_bus=None):
        """
        初始化控制器
        
        Args:
            question_service: QuestionService实例
            event_bus: 事件总线（可选）
        """
        self.question_service = question_service
        self.event_bus = event_bus
        self._current_image_path: Optional[str] = None
    
    def on_image_selected(self, image_path: str):
        """
        图片选择事件处理
        
        Args:
            image_path: 图片路径
        """
        self._current_image_path = image_path
        logger.info(f"图片已选择: {image_path}")
    
    def on_ocr_completed(self, text: str) -> str:
        """
        OCR识别完成事件处理
        
        Args:
            text: 识别的文本
            
        Returns:
            处理后的文本
        """
        # 这里可以对识别的文本进行处理
        # 例如：智能分段、格式化等
        if text is not None:
            logger.info(f"OCR识别完成，文本长度: {len(text)}")
        else:
            logger.warning("OCR识别返回None")
        return text
    
    def save_question(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        保存错题
        
        Args:
            data: 题目数据
        
        Returns:
            (成功标志, 消息)
        """
        try:
            # 调用服务层保存
            success, message, question_id = self.question_service.create_question(data)
            
            if success and self.event_bus:
                # 发布事件
                try:
                    from mistake_book.ui.events.events import QuestionAddedEvent
                    self.event_bus.publish(QuestionAddedEvent(
                        question_id=question_id,
                        question_data=data
                    ))
                except ImportError:
                    # 事件系统还未实现，忽略
                    pass
            
            return success, message
            
        except Exception as e:
            logger.error(f"保存错题失败: {e}")
            return False, f"保存失败: {str(e)}"
