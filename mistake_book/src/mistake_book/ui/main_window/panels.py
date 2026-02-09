"""面板工厂 - 创建主窗口的各个面板"""

from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QScrollArea
from PyQt6.QtCore import Qt
import logging

from mistake_book.ui.components.navigation_tree import NavigationTree
from mistake_book.ui.components.filter_panel import FilterPanel
from mistake_book.ui.components.statistics_panel import StatisticsPanel

if TYPE_CHECKING:
    from mistake_book.ui.main_window.controller import MainWindowController

logger = logging.getLogger(__name__)


class PanelFactory:
    """面板工厂 - 创建主窗口的各个面板"""
    
    def __init__(self, controller: 'MainWindowController'):
        """
        初始化面板工厂
        
        Args:
            controller: MainWindowController实例
        """
        self.controller = controller
        logger.debug("PanelFactory 初始化完成")
    
    def create_navigation_panel(self) -> NavigationTree:
        """
        创建导航面板
        
        Returns:
            NavigationTree组件实例
        """
        logger.debug("创建导航面板")
        nav_tree = NavigationTree(self.controller.ui_service)
        return nav_tree
    
    def create_card_panel(self) -> QWidget:
        """
        创建卡片流面板
        
        Returns:
            包含搜索框和卡片容器的面板
        """
        logger.debug("创建卡片流面板")
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 搜索框
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 搜索错题...")
        search_input.setMinimumHeight(35)
        layout.addWidget(search_input)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 卡片容器
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(5, 5, 5, 5)
        cards_layout.setSpacing(10)
        cards_layout.addStretch()
        
        scroll.setWidget(cards_container)
        layout.addWidget(scroll)
        
        # 保存引用，方便外部访问
        panel.search_input = search_input
        panel.cards_container = cards_container
        panel.cards_layout = cards_layout
        panel.scroll_area = scroll
        
        logger.debug("卡片流面板创建完成")
        return panel
    
    def create_right_panel(self) -> QWidget:
        """
        创建右侧面板（筛选+统计）
        
        Returns:
            包含筛选面板和统计面板的组合面板
        """
        logger.debug("创建右侧面板")
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 筛选面板
        filter_panel = FilterPanel(self.controller.ui_service)
        layout.addWidget(filter_panel)
        
        # 统计面板
        stats_panel = StatisticsPanel(self.controller.ui_service)
        layout.addWidget(stats_panel)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 保存引用，方便外部访问
        panel.filter_panel = filter_panel
        panel.stats_panel = stats_panel
        
        logger.debug("右侧面板创建完成")
        return panel
