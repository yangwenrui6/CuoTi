"""MainWindow集成测试"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from mistake_book.ui.main_window.window import MainWindow
from mistake_book.ui.main_window.controller import MainWindowController
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
def mock_dialog_factory():
    """创建mock对话框工厂"""
    factory = Mock()
    factory.create_add_question_dialog = Mock(return_value=Mock())
    factory.create_detail_dialog = Mock(return_value=Mock())
    factory.create_review_module_selector = Mock(return_value=Mock())
    return factory


@pytest.fixture
def event_bus():
    """创建事件总线"""
    bus = EventBus()
    bus.clear()
    return bus


@pytest.fixture
def controller(mock_services, mock_dialog_factory, event_bus):
    """创建控制器"""
    return MainWindowController(mock_services, mock_dialog_factory, event_bus)


@pytest.fixture
def main_window(qtbot, controller):
    """创建主窗口"""
    # Mock UIService方法
    controller.ui_service.get_all_questions = Mock(return_value=[])
    controller.ui_service.get_subjects = Mock(return_value=[])
    controller.ui_service.get_tags = Mock(return_value=[])
    controller.ui_service.get_statistics = Mock(return_value={
        'total': 0,
        'mastery_distribution': {},
        'due_today': 0
    })
    controller.ui_service.get_navigation_data = Mock(return_value={
        'subjects': [],
        'tags': [],
        'mastery_levels': []
    })
    controller.ui_service.get_filter_options = Mock(return_value={
        'subjects': ['全部'],
        'difficulties': ['全部', '1', '2', '3', '4', '5'],
        'mastery_levels': ['全部', '0', '1', '2', '3', '4', '5']
    })
    
    window = MainWindow(controller)
    qtbot.addWidget(window)
    return window


class TestMainWindowIntegration:
    """MainWindow集成测试"""
    
    def test_window_initialization(self, main_window):
        """测试窗口初始化"""
        assert main_window.windowTitle() == "错题本 - 智能学习管理"
        assert main_window.controller is not None
        assert main_window.panel_factory is not None
    
    def test_panels_created(self, main_window):
        """测试面板创建"""
        # 验证导航树存在
        assert main_window.nav_tree is not None
        
        # 验证卡片面板存在
        assert main_window.card_panel is not None
        assert hasattr(main_window.card_panel, 'search_input')
        assert hasattr(main_window.card_panel, 'cards_container')
        
        # 验证右侧面板存在
        assert main_window.right_panel is not None
        assert hasattr(main_window.right_panel, 'filter_panel')
        assert hasattr(main_window.right_panel, 'stats_panel')
    
    def test_toolbar_created(self, main_window):
        """测试工具栏创建"""
        from PyQt6.QtWidgets import QToolBar
        # 查找所有工具栏
        toolbars = main_window.findChildren(QToolBar)
        assert len(toolbars) > 0, "应该至少有一个工具栏"
        
        # 验证工具栏有动作
        toolbar = toolbars[0]
        assert len(toolbar.actions()) >= 3, "工具栏应该有至少3个动作（添加、复习、刷新）"
    
    def test_signals_connected(self, main_window):
        """测试信号连接"""
        # 验证导航树信号连接
        assert main_window.nav_tree.receivers(
            main_window.nav_tree.item_selected
        ) > 0
        
        # 验证筛选面板信号连接
        assert main_window.right_panel.filter_panel.receivers(
            main_window.right_panel.filter_panel.filter_changed
        ) > 0
        
        # 验证搜索框信号连接
        assert main_window.card_panel.search_input.receivers(
            main_window.card_panel.search_input.textChanged
        ) > 0
    
    def test_display_questions(self, main_window):
        """测试显示题目"""
        # 准备测试数据
        questions = [
            {'id': 1, 'subject': '数学', 'content': '题目1'},
            {'id': 2, 'subject': '英语', 'content': '题目2'}
        ]
        
        # 显示题目
        main_window._display_questions(questions)
        
        # 验证卡片数量
        assert len(main_window.current_cards) == 2
        
        # 验证状态栏
        assert "显示 2 个题目" in main_window.statusBar().currentMessage()
    
    def test_clear_cards(self, main_window):
        """测试清空卡片"""
        # 先显示一些题目
        questions = [
            {'id': 1, 'subject': '数学', 'content': '题目1'}
        ]
        main_window._display_questions(questions)
        assert len(main_window.current_cards) == 1
        
        # 清空卡片
        main_window._clear_cards()
        assert len(main_window.current_cards) == 0
    
    def test_search_functionality(self, main_window, qtbot):
        """测试搜索功能"""
        # Mock搜索结果
        search_results = [
            {'id': 1, 'subject': '数学', 'content': '搜索结果'}
        ]
        main_window.controller.on_search = Mock(return_value=search_results)
        
        # 输入搜索关键词
        main_window.card_panel.search_input.setText("测试")
        qtbot.wait(100)  # 等待信号处理
        
        # 验证搜索被调用
        main_window.controller.on_search.assert_called_with("测试")
    
    def test_nav_filter_functionality(self, main_window):
        """测试导航筛选功能"""
        # Mock筛选结果
        filter_results = [
            {'id': 1, 'subject': '数学', 'content': '筛选结果'}
        ]
        main_window.controller.on_nav_filter_changed = Mock(
            return_value=filter_results
        )
        
        # 触发导航筛选
        filter_data = {'type': 'subject', 'value': '数学'}
        main_window.nav_tree.item_selected.emit(filter_data)
        
        # 验证筛选被调用
        main_window.controller.on_nav_filter_changed.assert_called_with(
            filter_data
        )
    
    def test_filter_panel_functionality(self, main_window):
        """测试筛选面板功能"""
        # Mock筛选结果
        filter_results = [
            {'id': 1, 'subject': '数学', 'content': '筛选结果'}
        ]
        main_window.controller.on_filter_changed = Mock(
            return_value=filter_results
        )
        
        # 触发筛选
        filters = {'subject': '数学', 'difficulty': 3}
        main_window.right_panel.filter_panel.filter_changed.emit(filters)
        
        # 验证筛选被调用
        main_window.controller.on_filter_changed.assert_called_with(filters)
    
    def test_add_button_click(self, main_window, qtbot):
        """测试添加按钮点击"""
        # Mock show_add_dialog
        main_window.controller.show_add_dialog = Mock()
        
        # 点击添加按钮
        main_window._on_add_clicked()
        
        # 验证对话框被显示
        main_window.controller.show_add_dialog.assert_called_once()
    
    def test_review_button_click(self, main_window):
        """测试复习按钮点击"""
        # Mock start_review
        main_window.controller.start_review = Mock()
        
        # 点击复习按钮
        main_window._on_review_clicked()
        
        # 验证复习被启动
        main_window.controller.start_review.assert_called_once()
    
    def test_refresh_button_click(self, main_window):
        """测试刷新按钮点击"""
        # Mock refresh_current_view
        main_window.controller.refresh_current_view = Mock(return_value=[])
        main_window.controller.ui_service.get_subjects = Mock(return_value=[])
        main_window.controller.ui_service.get_tags = Mock(return_value=[])
        main_window.controller.ui_service.get_statistics = Mock(return_value={
            'total': 0,
            'mastery_distribution': {},
            'due_today': 0
        })
        
        # 点击刷新按钮
        main_window._on_refresh_clicked()
        
        # 验证刷新被调用
        main_window.controller.refresh_current_view.assert_called_once()
    
    def test_view_question(self, main_window):
        """测试查看题目详情"""
        # 准备测试数据
        question_data = {'id': 1, 'subject': '数学', 'content': '题目1'}
        main_window.controller.current_questions = [question_data]
        
        # Mock对话框工厂
        mock_dialog = Mock()
        mock_dialog.exec = Mock()
        main_window.controller.dialog_factory.create_detail_dialog = Mock(
            return_value=mock_dialog
        )
        
        # 查看题目
        main_window._on_view_question(1)
        
        # 验证对话框被创建和显示
        main_window.controller.dialog_factory.create_detail_dialog.assert_called_once()
        mock_dialog.exec.assert_called_once()
    
    def test_delete_question_confirmed(self, main_window, qtbot, monkeypatch):
        """测试删除题目（确认）"""
        from PyQt6.QtWidgets import QMessageBox
        
        # Mock确认对话框返回Yes
        monkeypatch.setattr(
            QMessageBox,
            'question',
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes
        )
        
        # Mock删除成功
        main_window.controller.delete_question = Mock(
            return_value=(True, "删除成功")
        )
        main_window.controller.refresh_current_view = Mock(return_value=[])
        
        # 删除题目
        main_window._on_delete_question(1)
        
        # 验证删除被调用
        main_window.controller.delete_question.assert_called_with(1)
    
    def test_delete_question_cancelled(self, main_window, monkeypatch):
        """测试删除题目（取消）"""
        from PyQt6.QtWidgets import QMessageBox
        
        # Mock确认对话框返回No
        monkeypatch.setattr(
            QMessageBox,
            'question',
            lambda *args, **kwargs: QMessageBox.StandardButton.No
        )
        
        # Mock删除
        main_window.controller.delete_question = Mock()
        
        # 删除题目
        main_window._on_delete_question(1)
        
        # 验证删除未被调用
        main_window.controller.delete_question.assert_not_called()
    
    def test_initial_data_load(self, main_window):
        """测试初始数据加载"""
        # 验证初始加载被调用
        assert main_window.controller.ui_service.get_all_questions.called
    
    def test_window_geometry(self, main_window):
        """测试窗口几何属性"""
        geometry = main_window.geometry()
        assert geometry.width() == 1400
        assert geometry.height() == 900
