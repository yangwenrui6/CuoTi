"""主窗口Controller - 三栏布局"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QFont
from mistake_book.config.paths import get_app_paths
from mistake_book.database.db_manager import DatabaseManager
from mistake_book.core.data_manager import DataManager
from mistake_book.core.review_scheduler import ReviewScheduler
from mistake_book.ui.dialogs.add_dialog import AddQuestionDialog
from mistake_book.ui.widgets.question_card import QuestionCard
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口 - 三栏布局"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("错题本 - 智能学习管理")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化数据层
        paths = get_app_paths()
        self.db_manager = DatabaseManager(paths.database_file)
        self.data_manager = DataManager(self.db_manager)
        self.scheduler = ReviewScheduler()
        
        # 初始化服务层
        from mistake_book.services import QuestionService, ReviewService, UIService
        
        # OCR引擎将在后台异步初始化，不阻塞UI
        self.ocr_engine = None
        self._init_ocr_async()
        
        self.question_service = QuestionService(self.data_manager, self.ocr_engine)
        self.review_service = ReviewService(self.data_manager, self.scheduler)
        self.ui_service = UIService(self.data_manager)
        
        # 字体缩放级别（无障碍）
        self.font_scale = 1.0
        
        # 当前视图状态
        self.current_view_type = "all"  # all, search, nav_filter, filter
        self.current_search_text = ""
        self.current_nav_filter = None
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_questions()
        
        # 显示OCR状态
        self.show_ocr_status()
    
    def init_ui(self):
        """初始化UI"""
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主布局
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建三栏分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左栏：导航树
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 中栏：错题卡片流
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # 右栏：筛选和统计
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割比例 (1:3:1)
        splitter.setSizes([250, 700, 250])
        
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 添加错题
        add_action = QAction("➕ 添加错题", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self.show_add_dialog)
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # 开始复习
        review_action = QAction("📚 开始复习", self)
        review_action.setShortcut(QKeySequence("Ctrl+R"))
        review_action.triggered.connect(self.start_review)
        toolbar.addAction(review_action)
        
        toolbar.addSeparator()
        
        # 导出
        export_action = QAction("📤 导出", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # 字体缩放（无障碍）
        zoom_in_action = QAction("🔍+ 放大", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍- 缩小", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        toolbar.addSeparator()
        
        # 高对比度模式
        contrast_action = QAction("🎨 高对比度", self)
        contrast_action.setCheckable(True)
        contrast_action.triggered.connect(self.toggle_high_contrast)
        toolbar.addAction(contrast_action)
    
    def create_left_panel(self):
        """创建左侧导航面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title = QLabel("📂 分类导航")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # 树形导航
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderLabel("科目/标签")
        self.nav_tree.itemClicked.connect(self.on_nav_item_clicked)
        
        # 从服务获取导航数据
        nav_data = self.ui_service.get_navigation_data()
        
        # 添加科目节点
        for subject in nav_data['subjects']:
            item = QTreeWidgetItem([subject])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "subject", "value": subject})
            self.nav_tree.addTopLevelItem(item)
        
        # 添加标签节点
        if nav_data['tags']:
            tags_root = QTreeWidgetItem(["🏷️ 标签"])
            for tag in nav_data['tags']:
                tag_item = QTreeWidgetItem([tag])
                tag_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "tag", "value": tag})
                tags_root.addChild(tag_item)
            self.nav_tree.addTopLevelItem(tags_root)
        
        # 添加掌握度节点
        mastery_root = QTreeWidgetItem(["📊 掌握度"])
        for level_data in nav_data['mastery_levels']:
            item = QTreeWidgetItem([f"{level_data['name']} ({level_data['count']})"])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "mastery", "value": level_data['value']})
            mastery_root.addChild(item)
        self.nav_tree.addTopLevelItem(mastery_root)
        
        self.nav_tree.expandAll()
        layout.addWidget(self.nav_tree)
        
        return panel
    
    def create_center_panel(self):
        """创建中间错题卡片流"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索错题...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
        
        return panel
    
    def create_right_panel(self):
        """创建右侧筛选和统计面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 筛选面板
        filter_group = QGroupBox("🔧 筛选")
        filter_layout = QVBoxLayout()
        
        # 从服务获取筛选选项
        filter_options = self.ui_service.get_filter_options()
        
        # 科目筛选
        filter_layout.addWidget(QLabel("科目:"))
        self.subject_filter = QComboBox()
        self.subject_filter.addItems(filter_options['subjects'])
        self.subject_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.subject_filter)
        
        # 难度筛选
        filter_layout.addWidget(QLabel("难度:"))
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItems(filter_options['difficulties'])
        self.difficulty_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.difficulty_filter)
        
        # 掌握度筛选
        filter_layout.addWidget(QLabel("掌握度:"))
        self.mastery_filter = QComboBox()
        self.mastery_filter.addItems(filter_options['mastery_levels'])
        self.mastery_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.mastery_filter)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 统计面板
        stats_group = QGroupBox("📊 统计")
        stats_layout = QVBoxLayout()
        
        self.total_label = QLabel("总题数: 0")
        self.mastered_label = QLabel("已掌握: 0")
        self.learning_label = QLabel("学习中: 0")
        self.review_due_label = QLabel("待复习: 0")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.mastered_label)
        stats_layout.addWidget(self.learning_label)
        stats_layout.addWidget(self.review_due_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        return panel
    
    def setup_shortcuts(self):
        """设置键盘快捷键（无障碍）"""
        # Ctrl+R 已在工具栏设置
        # Ctrl+N 已在工具栏设置
        pass
    
    def load_questions(self):
        """加载错题列表 - 显示全部"""
        self.current_view_type = "all"
        self.current_search_text = ""
        self.current_nav_filter = None
        
        questions = self.ui_service.get_all_questions()
        self.display_questions(questions)
        self.update_statistics()
    
    def refresh_current_view(self):
        """刷新当前视图 - 保持筛选状态"""
        if self.current_view_type == "search":
            # 重新执行搜索
            questions = self.ui_service.search_questions(self.current_search_text)
            self.display_questions(questions)
        elif self.current_view_type == "nav_filter":
            # 重新应用导航筛选
            questions = self.ui_service.filter_questions(self.current_nav_filter)
            self.display_questions(questions)
        elif self.current_view_type == "filter":
            # 重新应用右侧筛选
            self.apply_filters()
        else:
            # 默认显示全部
            questions = self.ui_service.get_all_questions()
            self.display_questions(questions)
        
        # 更新统计和导航树
        self.update_statistics()
        self.refresh_navigation()
    
    def refresh_navigation(self):
        """刷新导航树 - 保持选中状态"""
        # 保存当前选中项的数据
        current_item = self.nav_tree.currentItem()
        selected_data = None
        if current_item:
            selected_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        # 清空导航树
        self.nav_tree.clear()
        
        # 从服务获取最新导航数据
        nav_data = self.ui_service.get_navigation_data()
        
        # 添加科目节点
        for subject in nav_data['subjects']:
            item = QTreeWidgetItem([subject])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "subject", "value": subject})
            self.nav_tree.addTopLevelItem(item)
            
            # 恢复选中状态
            if selected_data and selected_data.get("type") == "subject" and selected_data.get("value") == subject:
                self.nav_tree.setCurrentItem(item)
        
        # 添加标签节点
        if nav_data['tags']:
            tags_root = QTreeWidgetItem(["🏷️ 标签"])
            for tag in nav_data['tags']:
                tag_item = QTreeWidgetItem([tag])
                tag_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "tag", "value": tag})
                tags_root.addChild(tag_item)
                
                # 恢复选中状态
                if selected_data and selected_data.get("type") == "tag" and selected_data.get("value") == tag:
                    self.nav_tree.setCurrentItem(tag_item)
            
            self.nav_tree.addTopLevelItem(tags_root)
        
        # 添加掌握度节点
        mastery_root = QTreeWidgetItem(["📊 掌握度"])
        for level_data in nav_data['mastery_levels']:
            item = QTreeWidgetItem([f"{level_data['name']} ({level_data['count']})"])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "mastery", "value": level_data['value']})
            mastery_root.addChild(item)
            
            # 恢复选中状态
            if selected_data and selected_data.get("type") == "mastery" and selected_data.get("value") == level_data['value']:
                self.nav_tree.setCurrentItem(item)
        
        self.nav_tree.addTopLevelItem(mastery_root)
        
        # 展开所有节点
        self.nav_tree.expandAll()
    
    def display_questions(self, questions):
        """显示错题卡片"""
        # 清空现有卡片
        while self.cards_layout.count() > 1:  # 保留stretch
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新卡片
        for question in questions:
            card = QuestionCard(question)
            # 点击卡片查看详情
            card.clicked.connect(lambda q=question: self.on_view_detail(q))
            # 删除按钮
            card.delete_requested.connect(lambda q=question: self.on_delete_question(q))
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
    
    def update_statistics(self):
        """更新统计信息"""
        stats = self.ui_service.get_statistics_summary()
        
        self.total_label.setText(f"总题数: {stats.get('total_questions', 0)}")
        self.mastered_label.setText(f"已掌握: {stats.get('mastered', 0)}")
        self.learning_label.setText(f"学习中: {stats.get('learning', 0)}")
        self.review_due_label.setText(f"待复习: {stats.get('due_count', 0)}")
    
    def show_add_dialog(self):
        """显示添加错题对话框"""
        # 创建对话框，传入服务
        dialog = AddQuestionDialog(self.question_service, self)
        
        if dialog.exec():
            # 对话框关闭且保存成功，刷新当前视图(保持筛选状态)
            self.refresh_current_view()
            self.statusBar().showMessage("添加成功", 3000)
    
    def start_review(self):
        """开始复习模式"""
        # 先显示模块选择对话框
        from mistake_book.ui.dialogs.review_module_selector import ReviewModuleSelectorDialog
        
        selector = ReviewModuleSelectorDialog(self.data_manager, self)
        
        # 连接信号
        selector.module_selected.connect(self.on_module_selected_for_review)
        
        # 显示对话框
        result = selector.exec()
        
        # 如果用户取消了，记录日志
        if result == 0:
            logger.info("用户取消了复习模块选择")
    
    def on_module_selected_for_review(self, subject: str, question_type: str):
        """模块选择后开始复习"""
        logger.info(f"选择的模块：科目={subject}, 题型={question_type}")
        
        # 构建筛选条件
        filters = {}
        if subject:  # 如果不为空，说明选择了特定模块
            filters['subject'] = subject
        if question_type:
            filters['question_type'] = question_type
        
        logger.info(f"筛选条件：{filters}")
        
        # 获取待复习题目（暂时获取所有题目，不考虑到期时间）
        all_questions = self.data_manager.search_questions(filters)
        logger.info(f"找到 {len(all_questions)} 道题目")
        
        if not all_questions:
            module_name = f"{subject} - {question_type}" if subject else "全部"
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "提示",
                f"{module_name} 暂无题目"
            )
            return
        
        # 创建新的复习对话框
        from mistake_book.ui.dialogs.review_dialog_new import ReviewDialog
        dialog = ReviewDialog(all_questions, self.review_service, self)
        dialog.exec()
        
        # 复习完成后刷新当前视图(保持筛选状态)
        self.refresh_current_view()
        # 复习完成后刷新当前视图(保持筛选状态)
        self.refresh_current_view()
    
    def on_nav_item_clicked(self, item, column):
        """导航树点击事件"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.current_view_type = "nav_filter"
            filters = {}
            if data["type"] == "subject":
                filters["subject"] = data["value"]
            elif data["type"] == "mastery":
                filters["mastery_level"] = data["value"]
            elif data["type"] == "tag":
                filters["tags"] = [data["value"]]
            
            self.current_nav_filter = filters
            questions = self.ui_service.filter_questions(filters)
            self.display_questions(questions)
    
    def on_search(self, text):
        """搜索事件"""
        self.current_view_type = "search"
        self.current_search_text = text
        
        questions = self.ui_service.search_questions(text)
        self.display_questions(questions)
    
    def on_view_detail(self, question):
        """查看详情事件 - 点击卡片触发"""
        # 调用服务获取完整详情
        success, message, detail = self.question_service.get_question_detail(question['id'])
        
        if success and detail:
            # 显示详情对话框
            from mistake_book.ui.dialogs.detail_dialog import QuestionDetailDialog
            dialog = QuestionDetailDialog(detail, self)
            
            # 连接答案更新信号
            dialog.answer_updated.connect(self.on_answer_updated)
            
            dialog.exec()
        else:
            # 显示错误
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", message)
    
    def on_answer_updated(self, question_id: int, updates: dict):
        """处理答案更新"""
        # 调用服务更新错题
        success, message = self.question_service.update_question(question_id, updates)
        
        if success:
            # 刷新显示
            self.refresh_current_view()
        else:
            # 显示错误
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "保存失败", message)
    
    def on_delete_question(self, question):
        """删除错题事件"""
        from PyQt6.QtWidgets import QMessageBox
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除这道错题吗？\n\n科目：{question.get('subject', '')}\n题型：{question.get('question_type', '')}\n\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 调用服务删除
            success, message = self.question_service.delete_question(question['id'])
            
            if success:
                # 删除成功，刷新当前视图(保持筛选状态)
                self.refresh_current_view()
                self.statusBar().showMessage("删除成功", 3000)
            else:
                # 显示错误
                QMessageBox.warning(self, "删除失败", message)
    
    def apply_filters(self):
        """应用筛选条件"""
        self.current_view_type = "filter"
        
        # 使用服务解析筛选条件
        filters = self.ui_service.parse_filter_from_ui(
            self.subject_filter.currentText(),
            self.difficulty_filter.currentText(),
            self.mastery_filter.currentText()
        )
        
        questions = self.ui_service.filter_questions(filters)
        self.display_questions(questions)
    
    def zoom_in(self):
        """放大字体（无障碍）"""
        self.font_scale = min(2.0, self.font_scale + 0.1)
        self.apply_font_scale()
    
    def zoom_out(self):
        """缩小字体（无障碍）"""
        self.font_scale = max(0.5, self.font_scale - 0.1)
        self.apply_font_scale()
    
    def apply_font_scale(self):
        """应用字体缩放"""
        font = QFont()
        font.setPointSize(int(10 * self.font_scale))
        self.setFont(font)
    
    def toggle_high_contrast(self, checked):
        """切换高对比度模式（无障碍）"""
        if checked:
            self.setStyleSheet("""
                QMainWindow { background-color: #000; color: #FFF; }
                QWidget { background-color: #000; color: #FFF; }
                QPushButton { background-color: #FFF; color: #000; border: 2px solid #FFF; }
                QTreeWidget { background-color: #000; color: #FFF; }
                QLineEdit { background-color: #000; color: #FFF; border: 2px solid #FFF; }
            """)
        else:
            self.setStyleSheet("")

    
    def show_ocr_status(self):
        """显示OCR状态提示"""
        if not self.ocr_engine:
            return
        
        # 检查是否正在初始化
        if hasattr(self.ocr_engine, 'is_initializing') and self.ocr_engine.is_initializing():
            # 显示状态栏消息
            self.statusBar().showMessage("⏳ OCR模型正在后台加载中...")
            logger.info("OCR模型正在后台加载中...")
    
    def _init_ocr_async(self):
        """在后台线程中初始化OCR引擎，避免阻塞UI"""
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class OCRInitWorker(QThread):
            """OCR初始化工作线程"""
            finished = pyqtSignal(object)  # 传递ocr_engine对象
            
            def run(self):
                """在后台线程中创建OCR引擎"""
                try:
                    from mistake_book.services.ocr_engine import create_ocr_engine
                    
                    # 创建OCR引擎（异步初始化模型）
                    ocr_engine = create_ocr_engine(async_init=True)
                    self.finished.emit(ocr_engine)
                except Exception as e:
                    logger.error(f"OCR引擎初始化失败: {e}")
                    self.finished.emit(None)
        
        # 创建并启动工作线程
        self.ocr_init_worker = OCRInitWorker()
        self.ocr_init_worker.finished.connect(self._on_ocr_engine_created)
        self.ocr_init_worker.start()
        
        logger.info("OCR引擎正在后台初始化...")
    
    def _on_ocr_engine_created(self, ocr_engine):
        """OCR引擎创建完成回调（在主线程中执行）"""
        if ocr_engine:
            logger.info("OCR引擎已准备就绪")
            self.ocr_engine = ocr_engine
            
            # 更新question_service的ocr_engine引用
            if hasattr(self, 'question_service'):
                self.question_service.ocr_engine = ocr_engine
            
            # 设置初始化完成回调（使用Qt信号确保线程安全）
            if hasattr(ocr_engine, 'set_init_complete_callback'):
                # 创建一个线程安全的回调包装器
                def thread_safe_callback():
                    # 使用QTimer.singleShot确保在主线程中执行
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, self.on_ocr_init_complete)
                
                ocr_engine.set_init_complete_callback(thread_safe_callback)
            
            # 更新OCR状态显示
            self.show_ocr_status()
        else:
            logger.warning("OCR引擎不可用,OCR功能将被禁用")
            self.ocr_engine = None
    
    def on_ocr_init_complete(self):
        """OCR初始化完成回调"""
        # 更新状态栏
        self.statusBar().showMessage("✅ OCR模型加载完成，现在可以使用图片识别功能了！", 5000)
        
        # 关闭加载提示对话框
        if hasattr(self, 'ocr_loading_msg') and self.ocr_loading_msg:
            self.ocr_loading_msg.close()
            self.ocr_loading_msg = None
        
        # 显示完成通知
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "OCR模型加载完成",
            "✅ OCR模型已成功加载！\n\n"
            "现在您可以在添加错题时拖拽或上传图片，\n"
            "程序会自动识别图片中的文字。"
        )
        
        logger.info("OCR模型加载完成，用户已收到通知")
