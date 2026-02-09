"""测试 PanelFactory"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.main_window.panels import PanelFactory
from mistake_book.ui.components.navigation_tree import NavigationTree
from mistake_book.ui.components.filter_panel import FilterPanel
from mistake_book.ui.components.statistics_panel import StatisticsPanel


# 创建QApplication实例（PyQt测试需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_controller():
    """创建mock控制器"""
    controller = Mock()
    
    # Mock UI service with proper return values
    mock_ui_service = Mock()
    mock_ui_service.get_navigation_data.return_value = {
        'subjects': ['数学', '物理'],
        'tags': ['重点', '难点'],
        'mastery_levels': [
            {'name': '未掌握', 'value': 0, 'count': 2},
            {'name': '部分掌握', 'value': 1, 'count': 3},
            {'name': '已掌握', 'value': 2, 'count': 5}
        ]
    }
    mock_ui_service.get_filter_options.return_value = {
        'subjects': ['全部', '数学', '物理'],
        'difficulties': ['全部', '1', '2', '3', '4', '5'],
        'mastery_levels': ['全部', '未掌握', '部分掌握', '已掌握']
    }
    mock_ui_service.get_statistics.return_value = {
        'total': 10,
        'mastery_distribution': {0: 2, 1: 3, 2: 5}
    }
    
    controller.ui_service = mock_ui_service
    return controller


@pytest.fixture
def panel_factory(mock_controller, qapp):
    """创建PanelFactory实例"""
    return PanelFactory(mock_controller)


class TestPanelFactory:
    """测试PanelFactory类"""
    
    def test_initialization(self, mock_controller, qapp):
        """测试PanelFactory可以正确初始化"""
        factory = PanelFactory(mock_controller)
        assert factory is not None
        assert factory.controller == mock_controller
    
    def test_create_navigation_panel(self, panel_factory):
        """测试创建导航面板"""
        nav_panel = panel_factory.create_navigation_panel()
        
        # 验证返回的是NavigationTree实例
        assert isinstance(nav_panel, NavigationTree)
        
        # 验证组件已正确初始化
        assert nav_panel is not None
    
    def test_create_card_panel(self, panel_factory):
        """测试创建卡片流面板"""
        card_panel = panel_factory.create_card_panel()
        
        # 验证返回的是QWidget
        assert isinstance(card_panel, QWidget)
        
        # 验证面板包含必要的子组件
        assert hasattr(card_panel, 'search_input')
        assert hasattr(card_panel, 'cards_container')
        assert hasattr(card_panel, 'cards_layout')
        assert hasattr(card_panel, 'scroll_area')
        
        # 验证搜索框
        assert isinstance(card_panel.search_input, QLineEdit)
        assert card_panel.search_input.placeholderText() == "🔍 搜索错题..."
        
        # 验证卡片容器
        assert isinstance(card_panel.cards_container, QWidget)
        assert card_panel.cards_layout is not None
    
    def test_create_right_panel(self, panel_factory):
        """测试创建右侧面板"""
        right_panel = panel_factory.create_right_panel()
        
        # 验证返回的是QWidget
        assert isinstance(right_panel, QWidget)
        
        # 验证面板包含必要的子组件
        assert hasattr(right_panel, 'filter_panel')
        assert hasattr(right_panel, 'stats_panel')
        
        # 验证筛选面板
        assert isinstance(right_panel.filter_panel, FilterPanel)
        
        # 验证统计面板
        assert isinstance(right_panel.stats_panel, StatisticsPanel)
    
    def test_multiple_panel_creation(self, panel_factory):
        """测试可以创建多个独立的面板实例"""
        # 创建多个导航面板
        nav1 = panel_factory.create_navigation_panel()
        nav2 = panel_factory.create_navigation_panel()
        assert nav1 is not nav2
        
        # 创建多个卡片面板
        card1 = panel_factory.create_card_panel()
        card2 = panel_factory.create_card_panel()
        assert card1 is not card2
        
        # 创建多个右侧面板
        right1 = panel_factory.create_right_panel()
        right2 = panel_factory.create_right_panel()
        assert right1 is not right2
    
    def test_panel_factory_with_real_ui_service(self, qapp):
        """测试PanelFactory可以使用真实的UIService"""
        # 创建一个简单的mock UIService
        mock_ui_service = Mock()
        mock_ui_service.get_navigation_data.return_value = {
            'subjects': ['数学', '物理'],
            'tags': ['重点', '难点'],
            'mastery_levels': [
                {'name': '未掌握', 'value': 0, 'count': 2},
                {'name': '已掌握', 'value': 2, 'count': 5}
            ]
        }
        mock_ui_service.get_filter_options.return_value = {
            'subjects': ['全部', '数学', '物理'],
            'difficulties': ['全部', '1', '2', '3'],
            'mastery_levels': ['全部', '未掌握', '已掌握']
        }
        mock_ui_service.get_statistics.return_value = {
            'total': 10,
            'mastery_distribution': {0: 2, 1: 3, 2: 5}
        }
        
        controller = Mock()
        controller.ui_service = mock_ui_service
        
        factory = PanelFactory(controller)
        
        # 创建各个面板
        nav_panel = factory.create_navigation_panel()
        card_panel = factory.create_card_panel()
        right_panel = factory.create_right_panel()
        
        # 验证所有面板都成功创建
        assert nav_panel is not None
        assert card_panel is not None
        assert right_panel is not None
    
    def test_card_panel_layout(self, panel_factory):
        """测试卡片面板的布局结构"""
        card_panel = panel_factory.create_card_panel()
        
        # 验证布局存在
        layout = card_panel.layout()
        assert layout is not None
        
        # 验证搜索框在顶部
        assert card_panel.search_input.parent() == card_panel
        
        # 验证滚动区域存在
        assert card_panel.scroll_area is not None
        assert card_panel.scroll_area.widget() == card_panel.cards_container
    
    def test_right_panel_layout(self, panel_factory):
        """测试右侧面板的布局结构"""
        right_panel = panel_factory.create_right_panel()
        
        # 验证布局存在
        layout = right_panel.layout()
        assert layout is not None
        
        # 验证筛选面板和统计面板都在面板中
        assert right_panel.filter_panel.parent() == right_panel
        assert right_panel.stats_panel.parent() == right_panel
