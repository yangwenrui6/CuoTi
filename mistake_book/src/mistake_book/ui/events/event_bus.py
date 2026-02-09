"""事件总线 - 单例模式"""

from typing import Callable, Dict, List, Type
from .events import Event
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """事件总线 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: Dict[Type[Event], List[Callable]] = {}
        return cls._instance
    
    def subscribe(self, event_type: Type[Event], handler: Callable):
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        handler_name = getattr(handler, '__name__', repr(handler))
        logger.debug(f"订阅事件: {event_type.__name__}, 处理器: {handler_name}")
    
    def unsubscribe(self, event_type: Type[Event], handler: Callable):
        """
        取消订阅
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                handler_name = getattr(handler, '__name__', repr(handler))
                logger.debug(f"取消订阅事件: {event_type.__name__}, 处理器: {handler_name}")
            except ValueError:
                handler_name = getattr(handler, '__name__', repr(handler))
                logger.warning(f"处理器不存在: {handler_name}")
    
    def publish(self, event: Event):
        """
        发布事件
        
        Args:
            event: 事件实例
        """
        event_type = type(event)
        logger.debug(f"发布事件: {event_type.__name__}")
        
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"事件处理失败: {e}", exc_info=True)
    
    def clear(self):
        """清空所有订阅（用于测试）"""
        self._handlers.clear()
        logger.debug("清空所有事件订阅")
