"""EventBus单元测试

**Property 7: 事件总线解耦通信**
**Validates: Requirements 4.2**

测试要求:
- 测试订阅和发布
- 测试多个订阅者
- 测试错误处理
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.events.event_bus import EventBus
from mistake_book.ui.events.events import (
    Event,
    QuestionAddedEvent,
    QuestionUpdatedEvent,
    QuestionDeletedEvent
)


@pytest.fixture
def event_bus():
    """创建事件总线实例"""
    bus = EventBus()
    bus.clear()  # 清空之前的订阅
    return bus


class TestEventBus:
    """EventBus单元测试"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is bus2
    
    def test_subscribe_and_publish(self, event_bus):
        """测试订阅和发布"""
        # 创建mock处理器
        handler = Mock()
        
        # 订阅事件
        event_bus.subscribe(QuestionAddedEvent, handler)
        
        # 发布事件
        event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event_bus.publish(event)
        
        # 验证处理器被调用
        handler.assert_called_once_with(event)
    
    def test_multiple_subscribers(self, event_bus):
        """测试多个订阅者"""
        # 创建多个mock处理器
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()
        
        # 订阅同一事件
        event_bus.subscribe(QuestionAddedEvent, handler1)
        event_bus.subscribe(QuestionAddedEvent, handler2)
        event_bus.subscribe(QuestionAddedEvent, handler3)
        
        # 发布事件
        event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event_bus.publish(event)
        
        # 验证所有处理器都被调用
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)
        handler3.assert_called_once_with(event)
    
    def test_different_event_types(self, event_bus):
        """测试不同事件类型"""
        # 创建不同事件的处理器
        add_handler = Mock()
        update_handler = Mock()
        delete_handler = Mock()
        
        # 订阅不同事件
        event_bus.subscribe(QuestionAddedEvent, add_handler)
        event_bus.subscribe(QuestionUpdatedEvent, update_handler)
        event_bus.subscribe(QuestionDeletedEvent, delete_handler)
        
        # 发布添加事件
        add_event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event_bus.publish(add_event)
        
        # 只有add_handler被调用
        add_handler.assert_called_once_with(add_event)
        update_handler.assert_not_called()
        delete_handler.assert_not_called()
        
        # 重置mock
        add_handler.reset_mock()
        
        # 发布更新事件
        update_event = QuestionUpdatedEvent(
            question_id=1,
            updates={'content': '更新后的题目'}
        )
        event_bus.publish(update_event)
        
        # 只有update_handler被调用
        add_handler.assert_not_called()
        update_handler.assert_called_once_with(update_event)
        delete_handler.assert_not_called()
    
    def test_unsubscribe(self, event_bus):
        """测试取消订阅"""
        handler = Mock()
        
        # 订阅
        event_bus.subscribe(QuestionAddedEvent, handler)
        
        # 发布事件
        event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event_bus.publish(event)
        handler.assert_called_once()
        
        # 取消订阅
        event_bus.unsubscribe(QuestionAddedEvent, handler)
        handler.reset_mock()
        
        # 再次发布事件
        event_bus.publish(event)
        
        # 处理器不应该被调用
        handler.assert_not_called()
    
    def test_error_handling(self, event_bus):
        """测试错误处理 - 单个处理器失败不影响其他处理器"""
        # 创建处理器
        failing_handler = Mock(side_effect=Exception("处理器错误"))
        normal_handler = Mock()
        
        # 订阅
        event_bus.subscribe(QuestionAddedEvent, failing_handler)
        event_bus.subscribe(QuestionAddedEvent, normal_handler)
        
        # 发布事件
        event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event_bus.publish(event)
        
        # 验证两个处理器都被调用（即使第一个失败）
        failing_handler.assert_called_once_with(event)
        normal_handler.assert_called_once_with(event)
    
    def test_publish_without_subscribers(self, event_bus):
        """测试发布没有订阅者的事件"""
        # 发布事件（没有订阅者）
        event = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        
        # 不应该抛出异常
        event_bus.publish(event)
    
    def test_unsubscribe_nonexistent_handler(self, event_bus):
        """测试取消订阅不存在的处理器"""
        handler = Mock()
        
        # 取消订阅不存在的处理器（不应该抛出异常）
        event_bus.unsubscribe(QuestionAddedEvent, handler)
    
    def test_clear(self, event_bus):
        """测试清空所有订阅"""
        handler1 = Mock()
        handler2 = Mock()
        
        # 订阅多个事件
        event_bus.subscribe(QuestionAddedEvent, handler1)
        event_bus.subscribe(QuestionUpdatedEvent, handler2)
        
        # 清空
        event_bus.clear()
        
        # 发布事件
        event1 = QuestionAddedEvent(
            question_id=1,
            question_data={'content': '测试题目'}
        )
        event2 = QuestionUpdatedEvent(
            question_id=1,
            updates={'content': '更新后的题目'}
        )
        
        event_bus.publish(event1)
        event_bus.publish(event2)
        
        # 处理器不应该被调用
        handler1.assert_not_called()
        handler2.assert_not_called()
    
    def test_event_data_integrity(self, event_bus):
        """测试事件数据完整性"""
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_bus.subscribe(QuestionAddedEvent, handler)
        
        # 发布事件
        original_event = QuestionAddedEvent(
            question_id=123,
            question_data={'content': '测试题目', 'subject': '数学'}
        )
        event_bus.publish(original_event)
        
        # 验证接收到的事件数据完整
        assert len(received_events) == 1
        received_event = received_events[0]
        assert received_event.question_id == 123
        assert received_event.question_data['content'] == '测试题目'
        assert received_event.question_data['subject'] == '数学'
    
    def test_multiple_publishes(self, event_bus):
        """测试多次发布"""
        handler = Mock()
        event_bus.subscribe(QuestionAddedEvent, handler)
        
        # 发布多次
        for i in range(5):
            event = QuestionAddedEvent(
                question_id=i,
                question_data={'content': f'题目{i}'}
            )
            event_bus.publish(event)
        
        # 验证处理器被调用5次
        assert handler.call_count == 5
