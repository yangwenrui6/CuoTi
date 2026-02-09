"""DialogFactory单元测试

**Property 6: 工厂模式创建对话框**
**Validates: Requirements 4.1**

测试要求:
- 测试对话框创建
- 测试依赖注入
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.factories.dialog_factory import DialogFactory
from mistake_book.ui.events.event_bus import EventBus


@pytest.fixture
def mock_services():
    """创建mock服务"""
    return {
        'question_service': Mock(),
        'review_service': Mock(),
        'ui_service': Mock()
    }


@pytest.fixture
def event_bus():
    """创建事件总线"""
    bus = EventBus()
    bus.clear()
    return bus


@pytest.fixture
def dialog_factory(mock_services, event_bus):
    """创建对话框工厂"""
    return DialogFactory(mock_services, event_bus)


class TestDialogFactory:
    """DialogFactory单元测试"""
    
    def test_factory_initialization(self, dialog_factory, mock_services, event_bus):
        """测试工厂初始化"""
        assert dialog_factory.question_service == mock_services['question_service']
        assert dialog_factory.review_service == mock_services['review_service']
        assert dialog_factory.ui_service == mock_services['ui_service']
        assert dialog_factory.event_bus == event_bus
    
    def test_factory_initialization_without_event_bus(self, mock_services):
        """测试不带事件总线的初始化"""
        factory = DialogFactory(mock_services)
        assert factory.event_bus is None
    
    def test_create_add_question_dialog(self, dialog_factory):
        """测试创建添加错题对话框"""
        dialog = dialog_factory.create_add_question_dialog()
        
        # 验证对话框被创建
        assert dialog is not None
        assert hasattr(dialog, 'controller')
        
        # 验证控制器被正确注入
        assert dialog.controller is not None
        assert dialog.controller.question_service == dialog_factory.question_service
        assert dialog.controller.event_bus == dialog_factory.event_bus
    
    def test_create_detail_dialog(self, dialog_factory):
        """测试创建详情对话框"""
        question_data = {
            'id': 1,
            'subject': '数学',
            'content': '测试题目'
        }
        
        dialog = dialog_factory.create_detail_dialog(question_data)
        
        # 验证对话框被创建
        assert dialog is not None
        assert hasattr(dialog, 'controller')
        
        # 验证控制器被正确注入
        assert dialog.controller is not None
        assert dialog.controller.question_service == dialog_factory.question_service
        assert dialog.controller.event_bus == dialog_factory.event_bus
        assert dialog.controller.question_data == question_data
    
    def test_create_review_dialog(self, dialog_factory):
        """测试创建复习对话框"""
        questions = [
            {'id': 1, 'content': '题目1'},
            {'id': 2, 'content': '题目2'}
        ]
        
        dialog = dialog_factory.create_review_dialog(questions)
        
        # 验证对话框被创建
        assert dialog is not None
        assert hasattr(dialog, 'controller')
        
        # 验证控制器被正确注入
        assert dialog.controller is not None
        assert dialog.controller.review_service == dialog_factory.review_service
        assert dialog.controller.event_bus == dialog_factory.event_bus
        assert dialog.controller.questions == questions
    
    def test_dependency_injection(self, mock_services, event_bus):
        """测试依赖注入"""
        # 创建工厂
        factory = DialogFactory(mock_services, event_bus)
        
        # 创建对话框
        dialog = factory.create_add_question_dialog()
        
        # 验证依赖被正确注入
        assert dialog.controller.question_service is mock_services['question_service']
        assert dialog.controller.event_bus is event_bus
    
    def test_multiple_dialog_creation(self, dialog_factory):
        """测试创建多个对话框"""
        # 创建多个对话框
        dialog1 = dialog_factory.create_add_question_dialog()
        dialog2 = dialog_factory.create_add_question_dialog()
        
        # 验证是不同的实例
        assert dialog1 is not dialog2
        assert dialog1.controller is not dialog2.controller
    
    def test_services_shared_across_dialogs(self, dialog_factory):
        """测试服务在对话框间共享"""
        # 创建多个对话框
        dialog1 = dialog_factory.create_add_question_dialog()
        dialog2 = dialog_factory.create_add_question_dialog()
        
        # 验证服务是同一个实例
        assert dialog1.controller.question_service is dialog2.controller.question_service
        assert dialog1.controller.event_bus is dialog2.controller.event_bus
