"""MainWindowController 单元测试"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, call

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.main_window.controller import MainWindowController
from mistake_book.ui.events.events import (
    QuestionAddedEvent,
    QuestionUpdatedEvent,
    QuestionDeletedEvent
)


@pytest.fixture
def mock_services():
    """创建 mock 服务"""
    return {
        'question_service': Mock(),
        'review_service': Mock(),
        'ui_service': Mock()
    }


@pytest.fixture
def mock_dialog_factory():
    """创建 mock 对话框工厂"""
    return Mock()


@pytest.fixture
def mock_event_bus():
    """创建 mock 事件总线"""
    return Mock()


@pytest.fixture
def controller(mock_services, mock_dialog_factory, mock_event_bus):
    """创建控制器实例"""
    return MainWindowController(mock_services, mock_dialog_factory, mock_event_bus)


class TestMainWindowControllerInitialization:
    """测试控制器初始化"""
    
    def test_controller_initialization(self, controller, mock_services, mock_dialog_factory, mock_event_bus):
        """测试控制器可以正确初始化"""
        assert controller.question_service == mock_services['question_service']
        assert controller.review_service == mock_services['review_service']
        assert controller.ui_service == mock_services['ui_service']
        assert controller.dialog_factory == mock_dialog_factory
        assert controller.event_bus == mock_event_bus
    
    def test_initial_state(self, controller):
        """测试初始状态"""
        assert controller.current_view_type == "all"
        assert controller.current_filters == {}
        assert controller.current_questions == []
    
    def test_event_subscription(self, controller, mock_event_bus):
        """测试事件订阅"""
        # 验证订阅了正确的事件
        assert mock_event_bus.subscribe.call_count == 3
        
        # 获取所有订阅调用
        calls = mock_event_bus.subscribe.call_args_list
        event_types = [call[0][0] for call in calls]
        
        assert QuestionAddedEvent in event_types
        assert QuestionUpdatedEvent in event_types
        assert QuestionDeletedEvent in event_types


class TestLoadQuestions:
    """测试加载题目"""
    
    def test_load_questions_success(self, controller, mock_services):
        """测试成功加载所有题目"""
        # 准备测试数据
        test_questions = [
            {'id': 1, 'content': '题目1'},
            {'id': 2, 'content': '题目2'}
        ]
        mock_services['ui_service'].get_all_questions.return_value = test_questions
        
        # 执行
        result = controller.load_questions()
        
        # 验证
        assert result == test_questions
        assert controller.current_view_type == "all"
        assert controller.current_filters == {}
        assert controller.current_questions == test_questions
        mock_services['ui_service'].get_all_questions.assert_called_once()
    
    def test_load_questions_empty(self, controller, mock_services):
        """测试加载空题目列表"""
        mock_services['ui_service'].get_all_questions.return_value = []
        
        result = controller.load_questions()
        
        assert result == []
        assert controller.current_questions == []


class TestSearch:
    """测试搜索功能"""
    
    def test_search_with_keyword(self, controller, mock_services):
        """测试使用关键词搜索"""
        test_questions = [{'id': 1, 'content': '数学题目'}]
        mock_services['ui_service'].search_questions.return_value = test_questions
        
        result = controller.on_search("数学")
        
        assert result == test_questions
        assert controller.current_view_type == "search"
        assert controller.current_filters == {'keyword': '数学'}
        assert controller.current_questions == test_questions
        mock_services['ui_service'].search_questions.assert_called_once_with("数学")
    
    def test_search_with_empty_keyword(self, controller, mock_services):
        """测试空关键词搜索（应返回所有题目）"""
        all_questions = [
            {'id': 1, 'content': '题目1'},
            {'id': 2, 'content': '题目2'}
        ]
        mock_services['ui_service'].get_all_questions.return_value = all_questions
        
        result = controller.on_search("")
        
        assert result == all_questions
        assert controller.current_view_type == "all"
        mock_services['ui_service'].get_all_questions.assert_called_once()
    
    def test_search_with_whitespace_keyword(self, controller, mock_services):
        """测试只有空格的关键词（应返回所有题目）"""
        all_questions = [{'id': 1, 'content': '题目1'}]
        mock_services['ui_service'].get_all_questions.return_value = all_questions
        
        result = controller.on_search("   ")
        
        assert result == all_questions
        assert controller.current_view_type == "all"


class TestNavFilter:
    """测试导航筛选"""
    
    def test_nav_filter_by_subject(self, controller, mock_services):
        """测试按科目筛选"""
        test_questions = [{'id': 1, 'subject': '数学'}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.on_nav_filter_changed({
            'type': 'subject',
            'value': '数学'
        })
        
        assert result == test_questions
        assert controller.current_view_type == "nav_filter"
        assert controller.current_filters == {'subject': '数学'}
        mock_services['ui_service'].filter_questions.assert_called_once_with({'subject': '数学'})
    
    def test_nav_filter_by_mastery(self, controller, mock_services):
        """测试按掌握度筛选"""
        test_questions = [{'id': 1, 'mastery_level': 2}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.on_nav_filter_changed({
            'type': 'mastery',
            'value': 2
        })
        
        assert result == test_questions
        assert controller.current_filters == {'mastery_level': 2}
        mock_services['ui_service'].filter_questions.assert_called_once_with({'mastery_level': 2})
    
    def test_nav_filter_by_tag(self, controller, mock_services):
        """测试按标签筛选"""
        test_questions = [{'id': 1, 'tags': ['重点']}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.on_nav_filter_changed({
            'type': 'tag',
            'value': '重点'
        })
        
        assert result == test_questions
        assert controller.current_filters == {'tags': ['重点']}
        mock_services['ui_service'].filter_questions.assert_called_once_with({'tags': ['重点']})


class TestFilterPanel:
    """测试右侧筛选面板"""
    
    def test_filter_changed(self, controller, mock_services):
        """测试筛选条件变化"""
        filters = {
            'subject': '数学',
            'difficulty': 3,
            'mastery_level': 1
        }
        test_questions = [{'id': 1, 'subject': '数学', 'difficulty': 3}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.on_filter_changed(filters)
        
        assert result == test_questions
        assert controller.current_view_type == "filter"
        assert controller.current_filters == filters
        assert controller.current_questions == test_questions
        mock_services['ui_service'].filter_questions.assert_called_once_with(filters)
    
    def test_filter_with_empty_filters(self, controller, mock_services):
        """测试空筛选条件"""
        mock_services['ui_service'].filter_questions.return_value = []
        
        result = controller.on_filter_changed({})
        
        assert result == []
        mock_services['ui_service'].filter_questions.assert_called_once_with({})


class TestRefreshView:
    """测试刷新视图"""
    
    def test_refresh_all_view(self, controller, mock_services):
        """测试刷新"所有题目"视图"""
        controller.current_view_type = "all"
        test_questions = [{'id': 1}]
        mock_services['ui_service'].get_all_questions.return_value = test_questions
        
        result = controller.refresh_current_view()
        
        assert result == test_questions
        mock_services['ui_service'].get_all_questions.assert_called_once()
    
    def test_refresh_search_view(self, controller, mock_services):
        """测试刷新搜索视图"""
        controller.current_view_type = "search"
        controller.current_filters = {'keyword': '数学'}
        test_questions = [{'id': 1}]
        mock_services['ui_service'].search_questions.return_value = test_questions
        
        result = controller.refresh_current_view()
        
        assert result == test_questions
        mock_services['ui_service'].search_questions.assert_called_once_with('数学')
    
    def test_refresh_filter_view(self, controller, mock_services):
        """测试刷新筛选视图"""
        controller.current_view_type = "filter"
        controller.current_filters = {'subject': '数学'}
        test_questions = [{'id': 1}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.refresh_current_view()
        
        assert result == test_questions
        mock_services['ui_service'].filter_questions.assert_called_once_with({'subject': '数学'})
    
    def test_refresh_nav_filter_view(self, controller, mock_services):
        """测试刷新导航筛选视图"""
        controller.current_view_type = "nav_filter"
        controller.current_filters = {'subject': '物理'}
        test_questions = [{'id': 2}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        result = controller.refresh_current_view()
        
        assert result == test_questions
        mock_services['ui_service'].filter_questions.assert_called_once_with({'subject': '物理'})


class TestDialogOperations:
    """测试对话框操作"""
    
    def test_show_add_dialog(self, controller, mock_dialog_factory):
        """测试显示添加对话框"""
        mock_dialog = Mock()
        mock_dialog_factory.create_add_question_dialog.return_value = mock_dialog
        
        controller.show_add_dialog()
        
        mock_dialog_factory.create_add_question_dialog.assert_called_once()
        mock_dialog.exec.assert_called_once()
    
    def test_show_add_dialog_with_parent(self, controller, mock_dialog_factory):
        """测试显示添加对话框（带父窗口）"""
        mock_dialog = Mock()
        mock_dialog_factory.create_add_question_dialog.return_value = mock_dialog
        parent = Mock()
        
        controller.show_add_dialog(parent)
        
        mock_dialog_factory.create_add_question_dialog.assert_called_once_with(parent)
        mock_dialog.exec.assert_called_once()
    
    def test_start_review(self, controller, mock_dialog_factory):
        """测试开始复习"""
        mock_selector = Mock()
        mock_dialog_factory.create_review_module_selector.return_value = mock_selector
        
        controller.start_review()
        
        mock_dialog_factory.create_review_module_selector.assert_called_once()
        mock_selector.exec.assert_called_once()


class TestDeleteQuestion:
    """测试删除题目"""
    
    def test_delete_question_success(self, controller, mock_services, mock_event_bus):
        """测试成功删除题目"""
        mock_services['question_service'].delete_question.return_value = (True, "删除成功")
        
        success, message = controller.delete_question(123)
        
        assert success is True
        assert message == "删除成功"
        mock_services['question_service'].delete_question.assert_called_once_with(123)
        
        # 验证发布了删除事件
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, QuestionDeletedEvent)
        assert event.question_id == 123
    
    def test_delete_question_failure(self, controller, mock_services, mock_event_bus):
        """测试删除题目失败"""
        mock_services['question_service'].delete_question.return_value = (False, "删除失败")
        
        success, message = controller.delete_question(123)
        
        assert success is False
        assert message == "删除失败"
        
        # 验证没有发布事件
        mock_event_bus.publish.assert_not_called()


class TestEventHandlers:
    """测试事件处理器"""
    
    def test_on_question_added(self, controller, mock_services):
        """测试题目添加事件处理"""
        # 设置当前视图
        controller.current_view_type = "all"
        test_questions = [{'id': 1}, {'id': 2}]
        mock_services['ui_service'].get_all_questions.return_value = test_questions
        
        # 触发事件
        event = QuestionAddedEvent(question_id=2, question_data={'content': '新题目'})
        controller._on_question_added(event)
        
        # 验证刷新了视图
        mock_services['ui_service'].get_all_questions.assert_called_once()
        assert controller.current_questions == test_questions
    
    def test_on_question_updated(self, controller, mock_services):
        """测试题目更新事件处理"""
        controller.current_view_type = "filter"
        controller.current_filters = {'subject': '数学'}
        test_questions = [{'id': 1, 'subject': '数学'}]
        mock_services['ui_service'].filter_questions.return_value = test_questions
        
        event = QuestionUpdatedEvent(question_id=1, updates={'content': '更新内容'})
        controller._on_question_updated(event)
        
        mock_services['ui_service'].filter_questions.assert_called_once_with({'subject': '数学'})
        assert controller.current_questions == test_questions
    
    def test_on_question_deleted(self, controller, mock_services):
        """测试题目删除事件处理"""
        controller.current_view_type = "search"
        controller.current_filters = {'keyword': '测试'}
        test_questions = []
        mock_services['ui_service'].search_questions.return_value = test_questions
        
        event = QuestionDeletedEvent(question_id=1)
        controller._on_question_deleted(event)
        
        mock_services['ui_service'].search_questions.assert_called_once_with('测试')
        assert controller.current_questions == test_questions


class TestControllerWithMockServices:
    """测试控制器可以使用 mock 服务"""
    
    def test_controller_accepts_mock_services(self, mock_services, mock_dialog_factory, mock_event_bus):
        """测试控制器接受 mock 服务"""
        controller = MainWindowController(mock_services, mock_dialog_factory, mock_event_bus)
        
        assert controller.question_service == mock_services['question_service']
        assert controller.review_service == mock_services['review_service']
        assert controller.ui_service == mock_services['ui_service']
    
    def test_controller_works_without_event_bus(self, mock_services, mock_dialog_factory):
        """测试控制器可以在没有事件总线的情况下工作"""
        controller = MainWindowController(mock_services, mock_dialog_factory, None)
        
        # 应该不会崩溃
        assert controller.event_bus is None
        
        # 删除操作应该正常工作（只是不发布事件）
        mock_services['question_service'].delete_question.return_value = (True, "成功")
        success, message = controller.delete_question(1)
        assert success is True
