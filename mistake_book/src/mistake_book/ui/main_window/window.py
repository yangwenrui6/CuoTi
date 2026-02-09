"""主窗口 - UI组装器"""

from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QToolBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence
import logging

from mistake_book.ui.main_window.panels import PanelFactory
from mistake_book.ui.widgets.question_card import QuestionCard

if TYPE_CHECKING:
    from mistake_book.ui.main_window.controller import MainWindowController

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口 - UI组装器"""
    
    def __init__(self, controller: 'MainWindowController'):
        """
        初始化主窗口
        
        Args:
            controller: MainWindowController实例
        """
        super().__init__()
        self.controller = controller
        self.setWindowTitle("错题本 - 智能学习管理")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建面板工厂
        self.panel_factory = PanelFactory(controller)
        
        # 当前显示的卡片列表
        self.current_cards = []
        
        # 初始化UI
        self._init_ui()
        self._connect_signals()
        
        # 初始加载
        self._load_initial_data()
        
        logger.info("MainWindow 初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主布局
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建三栏分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左栏：导航树
        self.nav_tree = self.panel_factory.create_navigation_panel()
        splitter.addWidget(self.nav_tree)
        
        # 中栏：卡片流
        self.card_panel = self.panel_factory.create_card_panel()
        splitter.addWidget(self.card_panel)
        
        # 右栏：筛选和统计
        self.right_panel = self.panel_factory.create_right_panel()
        splitter.addWidget(self.right_panel)
        
        # 设置分割比例 (1:3:1)
        splitter.setSizes([250, 700, 250])
        
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        logger.debug("UI初始化完成")
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 添加错题
        add_action = QAction("➕ 添加错题", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self._on_add_clicked)
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # 开始复习
        review_action = QAction("📚 开始复习", self)
        review_action.setShortcut(QKeySequence("Ctrl+R"))
        review_action.triggered.connect(self._on_review_clicked)
        toolbar.addAction(review_action)
        
        toolbar.addSeparator()
        
        # 刷新
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._on_refresh_clicked)
        toolbar.addAction(refresh_action)
        
        logger.debug("工具栏创建完成")
    
    def _connect_signals(self):
        """连接信号槽"""
        # 导航树选择
        self.nav_tree.item_selected.connect(self._on_nav_filter_changed)
        
        # 筛选面板
        self.right_panel.filter_panel.filter_changed.connect(self._on_filter_changed)
        
        # 搜索
        self.card_panel.search_input.textChanged.connect(self._on_search_changed)
        
        logger.debug("信号连接完成")
    
    def _load_initial_data(self):
        """加载初始数据"""
        questions = self.controller.load_questions()
        self._display_questions(questions)
        
        # 刷新导航树和统计
        self.nav_tree.refresh()
        self.right_panel.stats_panel.update_statistics()
        
        logger.debug(f"初始加载了 {len(questions)} 个题目")
    
    def _display_questions(self, questions):
        """
        显示题目列表
        
        Args:
            questions: 题目列表
        """
        # 清空现有卡片
        self._clear_cards()
        
        # 创建新卡片
        for question in questions:
            card = QuestionCard(question)
            card.clicked.connect(lambda q: self._on_view_question(q.get('id')))
            card.delete_requested.connect(lambda q: self._on_delete_question(q.get('id')))
            
            # 插入到布局中（在stretch之前）
            self.card_panel.cards_layout.insertWidget(
                self.card_panel.cards_layout.count() - 1,
                card
            )
            self.current_cards.append(card)
        
        # 更新状态栏
        self.statusBar().showMessage(f"显示 {len(questions)} 个题目")
        
        logger.debug(f"显示了 {len(questions)} 个题目卡片")
    
    def _clear_cards(self):
        """清空所有卡片"""
        for card in self.current_cards:
            self.card_panel.cards_layout.removeWidget(card)
            card.deleteLater()
        self.current_cards.clear()
    
    def _on_add_clicked(self):
        """添加按钮点击"""
        logger.info("点击添加错题按钮")
        self.controller.show_add_dialog(self)
        # 刷新视图
        self._refresh_view()
    
    def _on_review_clicked(self):
        """复习按钮点击"""
        logger.info("点击开始复习按钮")
        self.controller.start_review(self)
    
    def _on_refresh_clicked(self):
        """刷新按钮点击"""
        logger.info("点击刷新按钮")
        self._refresh_view()
    
    def _on_search_changed(self, keyword: str):
        """
        搜索框文本变化
        
        Args:
            keyword: 搜索关键词
        """
        logger.debug(f"搜索: {keyword}")
        questions = self.controller.on_search(keyword)
        self._display_questions(questions)
    
    def _on_nav_filter_changed(self, filter_data):
        """
        导航筛选变化
        
        Args:
            filter_data: 筛选条件
        """
        logger.debug(f"导航筛选: {filter_data}")
        questions = self.controller.on_nav_filter_changed(filter_data)
        self._display_questions(questions)
    
    def _on_filter_changed(self, filters):
        """
        筛选条件变化
        
        Args:
            filters: 筛选条件字典
        """
        logger.debug(f"筛选条件: {filters}")
        questions = self.controller.on_filter_changed(filters)
        self._display_questions(questions)
    
    def _on_view_question(self, question_id: int):
        """
        查看题目详情
        
        Args:
            question_id: 题目ID
        """
        logger.info(f"查看题目详情: {question_id}")
        
        # 获取题目数据
        question_data = None
        for q in self.controller.current_questions:
            if q.get('id') == question_id:
                question_data = q
                break
        
        if question_data:
            dialog = self.controller.dialog_factory.create_detail_dialog(
                question_data, self
            )
            dialog.exec()
            # 刷新视图
            self._refresh_view()
    
    def _on_delete_question(self, question_id: int):
        """
        删除题目
        
        Args:
            question_id: 题目ID
        """
        logger.info(f"删除题目: {question_id}")
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个错题吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.controller.delete_question(question_id)
            if success:
                self.statusBar().showMessage("删除成功", 3000)
                self._refresh_view()
            else:
                QMessageBox.warning(self, "删除失败", message)
    
    def _refresh_view(self):
        """刷新当前视图"""
        questions = self.controller.refresh_current_view()
        self._display_questions(questions)
        
        # 刷新导航树和统计
        self.nav_tree.refresh()
        self.right_panel.stats_panel.update_statistics()
        
        logger.debug("视图刷新完成")
