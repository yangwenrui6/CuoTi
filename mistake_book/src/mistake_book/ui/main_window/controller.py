"""主窗口控制器 - 业务逻辑"""

from typing import Dict, Any, List, Tuple, Optional
import logging

from mistake_book.ui.events.events import (
    QuestionAddedEvent,
    QuestionUpdatedEvent,
    QuestionDeletedEvent
)

logger = logging.getLogger(__name__)


class MainWindowController:
    """主窗口控制器 - 处理主窗口的业务逻辑"""
    
    def __init__(self, services: Dict[str, Any], dialog_factory, event_bus):
        """
        初始化控制器
        
        Args:
            services: 服务集合 {question_service, review_service, ui_service}
            dialog_factory: 对话框工厂
            event_bus: 事件总线
        """
        self.question_service = services.get('question_service')
        self.review_service = services.get('review_service')
        self.ui_service = services.get('ui_service')
        self.dialog_factory = dialog_factory
        self.event_bus = event_bus
        
        # 视图状态
        self.current_view_type = "all"  # all, search, nav_filter, filter
        self.current_filters: Dict[str, Any] = {}
        self.current_questions: List[Dict[str, Any]] = []
        
        # 订阅事件
        self._subscribe_events()
        
        logger.info("MainWindowController 初始化完成")
    
    def _subscribe_events(self):
        """订阅事件"""
        if self.event_bus:
            self.event_bus.subscribe(QuestionAddedEvent, self._on_question_added)
            self.event_bus.subscribe(QuestionUpdatedEvent, self._on_question_updated)
            self.event_bus.subscribe(QuestionDeletedEvent, self._on_question_deleted)
            logger.debug("已订阅题目相关事件")
    
    def load_questions(self) -> List[Dict[str, Any]]:
        """
        加载所有题目
        
        Returns:
            题目列表
        """
        logger.info("加载所有题目")
        self.current_view_type = "all"
        self.current_filters = {}
        self.current_questions = self.ui_service.get_all_questions()
        logger.debug(f"加载了 {len(self.current_questions)} 个题目")
        return self.current_questions
    
    def on_search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索事件处理
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            搜索结果列表
        """
        logger.info(f"搜索题目: {keyword}")
        
        if not keyword or not keyword.strip():
            # 空搜索，返回所有题目
            return self.load_questions()
        
        self.current_view_type = "search"
        self.current_filters = {'keyword': keyword}
        self.current_questions = self.ui_service.search_questions(keyword)
        logger.debug(f"搜索到 {len(self.current_questions)} 个题目")
        return self.current_questions
    
    def on_nav_filter_changed(self, filter_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        导航筛选变化事件处理
        
        Args:
            filter_data: 筛选条件 {type: 'subject'|'tag'|'mastery', value: ...}
        
        Returns:
            筛选后的题目列表
        """
        logger.info(f"导航筛选变化: {filter_data}")
        self.current_view_type = "nav_filter"
        
        # 将导航筛选转换为标准筛选格式
        filters = {}
        filter_type = filter_data.get('type')
        filter_value = filter_data.get('value')
        
        if filter_type == 'subject':
            filters['subject'] = filter_value
        elif filter_type == 'mastery':
            filters['mastery_level'] = filter_value
        elif filter_type == 'tag':
            filters['tags'] = [filter_value]
        
        self.current_filters = filters
        self.current_questions = self.ui_service.filter_questions(filters)
        logger.debug(f"筛选到 {len(self.current_questions)} 个题目")
        return self.current_questions
    
    def on_filter_changed(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        右侧筛选面板变化事件处理
        
        Args:
            filters: 筛选条件字典
        
        Returns:
            筛选后的题目列表
        """
        logger.info(f"筛选条件变化: {filters}")
        self.current_view_type = "filter"
        self.current_filters = filters
        self.current_questions = self.ui_service.filter_questions(filters)
        logger.debug(f"筛选到 {len(self.current_questions)} 个题目")
        return self.current_questions
    
    def refresh_current_view(self) -> List[Dict[str, Any]]:
        """
        刷新当前视图（保持筛选状态）
        
        Returns:
            刷新后的题目列表
        """
        logger.info(f"刷新当前视图: {self.current_view_type}")
        
        if self.current_view_type == "all":
            return self.load_questions()
        elif self.current_view_type == "search":
            keyword = self.current_filters.get('keyword', '')
            return self.on_search(keyword)
        elif self.current_view_type in ("nav_filter", "filter"):
            self.current_questions = self.ui_service.filter_questions(self.current_filters)
            logger.debug(f"刷新后有 {len(self.current_questions)} 个题目")
            return self.current_questions
        
        return self.current_questions
    
    def show_add_dialog(self, parent=None):
        """
        显示添加错题对话框
        
        Args:
            parent: 父窗口
        """
        logger.info("显示添加错题对话框")
        dialog = self.dialog_factory.create_add_question_dialog(parent)
        dialog.exec()
    
    def start_review(self, parent=None):
        """
        开始复习（显示模块选择器）
        
        Args:
            parent: 父窗口
        """
        logger.info("显示复习模块选择器")
        selector = self.dialog_factory.create_review_module_selector(parent)
        selector.exec()
    
    def delete_question(self, question_id: int) -> Tuple[bool, str]:
        """
        删除题目
        
        Args:
            question_id: 题目ID
        
        Returns:
            (成功标志, 消息)
        """
        logger.info(f"删除题目: {question_id}")
        success, message = self.question_service.delete_question(question_id)
        
        if success and self.event_bus:
            self.event_bus.publish(QuestionDeletedEvent(question_id=question_id))
            logger.debug(f"已发布题目删除事件: {question_id}")
        
        return success, message
    
    def _on_question_added(self, event: QuestionAddedEvent):
        """
        题目添加事件处理
        
        Args:
            event: 题目添加事件
        """
        logger.info(f"处理题目添加事件: {event.question_id}")
        self.refresh_current_view()
    
    def _on_question_updated(self, event: QuestionUpdatedEvent):
        """
        题目更新事件处理
        
        Args:
            event: 题目更新事件
        """
        logger.info(f"处理题目更新事件: {event.question_id}")
        self.refresh_current_view()
    
    def _on_question_deleted(self, event: QuestionDeletedEvent):
        """
        题目删除事件处理
        
        Args:
            event: 题目删除事件
        """
        logger.info(f"处理题目删除事件: {event.question_id}")
        self.refresh_current_view()
