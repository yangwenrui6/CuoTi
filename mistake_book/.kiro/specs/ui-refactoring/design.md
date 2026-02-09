# UI层重构 - 设计文档

## 概述

本文档描述UI层重构的技术设计方案。


### 重构目标

将现有的大型UI文件拆分为更小、职责单一的组件和模块，提高代码的可维护性、可测试性和可复用性。


### 当前问题分析

**main_window.py (600+行)**:
- 职责过多：窗口管理、导航树、卡片流、筛选面板、统计面板、工具栏
- 直接创建对话框实例，违反依赖倒置原则
- 难以单独测试各个面板功能

**add_dialog.py (600+行)**:
- 包含图片上传、OCR识别、表单输入、标签选择等多个功能
- DropZoneWidget、TagSelector等组件无法在其他地方复用
- 业务逻辑与UI代码混合

**detail_dialog.py (400+行)**:
- 显示逻辑和编辑逻辑混合
- 缺少控制器层，业务逻辑直接在UI中


## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Components  │  │   Dialogs    │  │ Main Window  │      │
│  │  (可复用组件) │  │  (对话框模块) │  │  (主窗口模块) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│  ┌─────────────────────────┴──────────────────────────┐     │
│  │              Factories & Event Bus                  │     │
│  │  ┌──────────────┐         ┌──────────────┐        │     │
│  │  │DialogFactory │         │  Event Bus   │        │     │
│  │  └──────────────┘         └──────────────┘        │     │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │QuestionSvc   │  │  ReviewSvc   │  │   UISvc      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 设计原则

1. **单一职责原则 (SRP)**: 每个类只负责一个功能模块
2. **依赖倒置原则 (DIP)**: 通过工厂模式和依赖注入解耦
3. **开闭原则 (OCP)**: 通过事件总线实现组件间松耦合
4. **接口隔离原则 (ISP)**: 组件提供清晰的信号接口
5. **组合优于继承**: 通过组合小组件构建复杂UI


## 组件设计

### 1. ImageUploader 组件

**位置**: `ui/components/image_uploader.py`

**职责**: 处理图片上传、拖拽、预览功能

**接口设计**:
```python
class ImageUploader(QWidget):
    """图片上传组件 - 支持拖拽和点击上传"""
    
    # 信号
    image_selected = pyqtSignal(str)  # 图片路径
    image_cleared = pyqtSignal()      # 清空图片
    
    def __init__(self, parent=None):
        """初始化组件"""
        super().__init__(parent)
        self._current_image_path: Optional[str] = None
        self._init_ui()
    
    def get_image_path(self) -> Optional[str]:
        """获取当前图片路径"""
        return self._current_image_path
    
    def set_image(self, path: str) -> bool:
        """设置图片（用于编辑场景）"""
        pass
    
    def clear(self):
        """清空图片"""
        pass
    
    def _init_ui(self):
        """初始化UI"""
        pass
    
    def _load_image(self, path: str) -> bool:
        """加载图片预览"""
        pass
    
    def _on_select_clicked(self):
        """点击选择图片"""
        pass
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        pass
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        pass
```

**关键特性**:
- 支持拖拽和点击两种上传方式
- 使用PIL加载图片，解决中文路径问题
- 提供图片预览和查看大图功能
- 清晰的信号接口，便于集成


### 2. OCRPanel 组件

**位置**: `ui/components/ocr_panel.py`

**职责**: OCR识别功能的UI封装

**接口设计**:
```python
class OCRPanel(QWidget):
    """OCR识别面板"""
    
    # 信号
    recognition_started = pyqtSignal()           # 开始识别
    recognition_completed = pyqtSignal(str)      # 识别完成(文本)
    recognition_failed = pyqtSignal(str)         # 识别失败(错误信息)
    
    def __init__(self, ocr_service, parent=None):
        """
        初始化OCR面板
        
        Args:
            ocr_service: OCR服务实例（QuestionService）
        """
        super().__init__(parent)
        self._ocr_service = ocr_service
        self._is_recognizing = False
        self._init_ui()
    
    def recognize_image(self, image_path: str):
        """
        识别图片
        
        Args:
            image_path: 图片路径
        """
        pass
    
    def set_status(self, status: str):
        """设置状态文本"""
        pass
    
    def is_recognizing(self) -> bool:
        """是否正在识别"""
        return self._is_recognizing
    
    def _init_ui(self):
        """初始化UI"""
        pass
    
    def _do_recognition(self, image_path: str):
        """在后台线程执行识别"""
        pass
```

**关键特性**:
- 封装OCR识别的UI交互
- 后台线程执行识别，不阻塞UI
- 显示识别状态和进度
- 处理OCR引擎未初始化的情况


### 3. QuestionForm 组件

**位置**: `ui/components/question_form.py`

**职责**: 题目信息表单（科目、题型、内容、答案等）

**接口设计**:
```python
class QuestionForm(QWidget):
    """题目表单组件"""
    
    # 信号
    data_changed = pyqtSignal()  # 数据变化
    
    def __init__(self, parent=None):
        """初始化表单"""
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
    
    def get_data(self) -> Dict[str, Any]:
        """
        获取表单数据
        
        Returns:
            {
                'subject': str,
                'question_type': str,
                'content': str,
                'my_answer': str,
                'answer': str,
                'explanation': str,
                'difficulty': int (1-5)
            }
        """
        pass
    
    def set_data(self, data: Dict[str, Any]):
        """设置表单数据（用于编辑场景）"""
        pass
    
    def validate(self) -> Tuple[bool, str]:
        """
        验证表单数据
        
        Returns:
            (是否有效, 错误信息)
        """
        pass
    
    def clear(self):
        """清空表单"""
        pass
    
    def set_content(self, text: str):
        """设置题目内容（用于OCR识别后填充）"""
        pass
    
    def focus_content(self):
        """聚焦到题目内容输入框"""
        pass
```

**关键特性**:
- 封装所有题目相关的输入字段
- 提供数据验证功能
- 支持数据的获取和设置（用于新增和编辑）
- 清晰的数据结构


### 4. FilterPanel 组件

**位置**: `ui/components/filter_panel.py`

**职责**: 筛选面板（科目、难度、掌握度）

**接口设计**:
```python
class FilterPanel(QWidget):
    """筛选面板组件"""
    
    # 信号
    filter_changed = pyqtSignal(dict)  # 筛选条件变化
    
    def __init__(self, ui_service, parent=None):
        """
        初始化筛选面板
        
        Args:
            ui_service: UI服务实例
        """
        super().__init__(parent)
        self._ui_service = ui_service
        self._init_ui()
    
    def get_filters(self) -> Dict[str, Any]:
        """获取当前筛选条件"""
        pass
    
    def reset_filters(self):
        """重置筛选条件"""
        pass
    
    def _init_ui(self):
        """初始化UI"""
        pass
    
    def _on_filter_changed(self):
        """筛选条件变化时触发"""
        pass
```

**关键特性**:
- 封装筛选UI和逻辑
- 通过信号通知筛选条件变化
- 支持重置功能


### 5. StatisticsPanel 组件

**位置**: `ui/components/statistics_panel.py`

**职责**: 统计信息显示

**接口设计**:
```python
class StatisticsPanel(QWidget):
    """统计面板组件"""
    
    def __init__(self, ui_service, parent=None):
        """
        初始化统计面板
        
        Args:
            ui_service: UI服务实例
        """
        super().__init__(parent)
        self._ui_service = ui_service
        self._init_ui()
    
    def update_statistics(self):
        """更新统计数据"""
        pass
    
    def _init_ui(self):
        """初始化UI"""
        pass
```

**关键特性**:
- 显示总题数、掌握度分布、待复习数量
- 从UIService获取统计数据
- 支持手动刷新


### 6. NavigationTree 组件

**位置**: `ui/components/navigation_tree.py`

**职责**: 左侧导航树（科目、标签、掌握度）

**接口设计**:
```python
class NavigationTree(QWidget):
    """导航树组件"""
    
    # 信号
    item_selected = pyqtSignal(dict)  # 选中项变化 {type, value}
    
    def __init__(self, ui_service, parent=None):
        """
        初始化导航树
        
        Args:
            ui_service: UI服务实例
        """
        super().__init__(parent)
        self._ui_service = ui_service
        self._init_ui()
    
    def refresh(self):
        """刷新导航树数据"""
        pass
    
    def get_selected_filter(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的筛选条件"""
        pass
    
    def _init_ui(self):
        """初始化UI"""
        pass
    
    def _on_item_clicked(self, item, column):
        """树节点点击事件"""
        pass
```

**关键特性**:
- 显示科目、标签、掌握度分类
- 支持刷新和保持选中状态
- 通过信号通知选中项变化


## 对话框架构

### Dialog-Controller 模式

每个对话框拆分为两个文件：
- **dialog.py**: UI组装和布局，处理信号槽连接
- **controller.py**: 业务逻辑，调用服务层

**优势**:
1. UI和业务逻辑分离
2. Controller可以独立测试
3. 易于维护和扩展

### 1. AddQuestionDialog 重构

**目录结构**:
```
ui/dialogs/add_question/
├── __init__.py
├── dialog.py          # 对话框UI
└── controller.py      # 业务逻辑控制器
```

**dialog.py 设计**:
```python
class AddQuestionDialog(QDialog):
    """添加错题对话框 - UI组装器"""
    
    def __init__(self, controller, parent=None):
        """
        初始化对话框
        
        Args:
            controller: AddQuestionController实例
        """
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("➕ 添加错题")
        self.setMinimumSize(800, 700)
        
        # 创建组件
        self.image_uploader = ImageUploader()
        self.ocr_panel = OCRPanel(controller.question_service)
        self.question_form = QuestionForm()
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout(self)
        
        # 图片上传区域
        upload_group = QGroupBox("📷 图片上传")
        upload_layout = QVBoxLayout()
        upload_layout.addWidget(self.image_uploader)
        upload_layout.addWidget(self.ocr_panel)
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # 表单区域
        form_group = QGroupBox("📝 题目信息")
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.question_form)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 按钮
        self._add_buttons(layout)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 图片选择 -> OCR识别
        self.image_uploader.image_selected.connect(
            self.controller.on_image_selected
        )
        
        # OCR完成 -> 填充表单
        self.ocr_panel.recognition_completed.connect(
            self.controller.on_ocr_completed
        )
        
        # 保存按钮
        self.save_btn.clicked.connect(self._on_save_clicked)
    
    def _on_save_clicked(self):
        """保存按钮点击"""
        # 获取表单数据
        data = self.question_form.get_data()
        data['image_path'] = self.image_uploader.get_image_path()
        
        # 调用控制器保存
        success, message = self.controller.save_question(data)
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "保存失败", message)
```


**controller.py 设计**:
```python
class AddQuestionController:
    """添加错题控制器 - 业务逻辑"""
    
    def __init__(self, question_service, event_bus=None):
        """
        初始化控制器
        
        Args:
            question_service: QuestionService实例
            event_bus: 事件总线（可选）
        """
        self.question_service = question_service
        self.event_bus = event_bus
        self._current_image_path: Optional[str] = None
    
    def on_image_selected(self, image_path: str):
        """
        图片选择事件处理
        
        Args:
            image_path: 图片路径
        """
        self._current_image_path = image_path
        # 可以在这里添加额外的业务逻辑
    
    def on_ocr_completed(self, text: str):
        """
        OCR识别完成事件处理
        
        Args:
            text: 识别的文本
        """
        # 这里可以对识别的文本进行处理
        # 例如：智能分段、格式化等
        return text
    
    def save_question(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        保存错题
        
        Args:
            data: 题目数据
        
        Returns:
            (成功标志, 消息)
        """
        # 调用服务层保存
        success, message, question_id = self.question_service.create_question(data)
        
        if success and self.event_bus:
            # 发布事件
            from ui.events.events import QuestionAddedEvent
            self.event_bus.publish(QuestionAddedEvent(
                question_id=question_id,
                question_data=data
            ))
        
        return success, message
```

**关键改进**:
1. Dialog只负责UI组装，不包含业务逻辑
2. Controller处理所有业务逻辑，可独立测试
3. 使用组件组合，代码从600行降至约150行（dialog）+ 100行（controller）
4. 组件可在其他对话框中复用


### 2. DetailDialog 重构

**目录结构**:
```
ui/dialogs/detail/
├── __init__.py
├── dialog.py          # 详情对话框UI
└── controller.py      # 详情控制器
```

**controller.py 设计**:
```python
class DetailDialogController:
    """详情对话框控制器"""
    
    def __init__(self, question_service, question_data, event_bus=None):
        """
        初始化控制器
        
        Args:
            question_service: QuestionService实例
            question_data: 题目数据
            event_bus: 事件总线（可选）
        """
        self.question_service = question_service
        self.question_data = question_data
        self.original_data = question_data.copy()
        self.event_bus = event_bus
    
    def has_changes(self, current_data: Dict[str, Any]) -> bool:
        """检查是否有修改"""
        fields = ['content', 'my_answer', 'answer', 'explanation']
        return any(
            current_data.get(f) != self.original_data.get(f)
            for f in fields
        )
    
    def save_changes(self, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        保存修改
        
        Args:
            updates: 更新的字段
        
        Returns:
            (成功标志, 消息)
        """
        question_id = self.question_data['id']
        success, message = self.question_service.update_question(
            question_id, updates
        )
        
        if success and self.event_bus:
            from ui.events.events import QuestionUpdatedEvent
            self.event_bus.publish(QuestionUpdatedEvent(
                question_id=question_id,
                updates=updates
            ))
        
        return success, message
```


### 3. ReviewDialog 重构

**目录结构**:
```
ui/dialogs/review/
├── __init__.py
├── dialog.py          # 复习对话框UI
└── controller.py      # 复习控制器
```

**controller.py 设计**:
```python
class ReviewDialogController:
    """复习对话框控制器"""
    
    def __init__(self, review_service, questions, event_bus=None):
        """
        初始化控制器
        
        Args:
            review_service: ReviewService实例
            questions: 待复习题目列表
            event_bus: 事件总线（可选）
        """
        self.review_service = review_service
        self.questions = questions
        self.current_index = 0
        self.reviewed_count = 0
        self.event_bus = event_bus
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """获取当前题目"""
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    
    def submit_review(self, quality: int) -> bool:
        """
        提交复习结果
        
        Args:
            quality: 质量评分 (0-5)
        
        Returns:
            是否还有下一题
        """
        question = self.get_current_question()
        if not question:
            return False
        
        # 调用服务层更新复习数据
        self.review_service.update_review_data(
            question['id'], quality
        )
        
        self.reviewed_count += 1
        self.current_index += 1
        
        # 检查是否完成
        if self.current_index >= len(self.questions):
            if self.event_bus:
                from ui.events.events import ReviewCompletedEvent
                self.event_bus.publish(ReviewCompletedEvent(
                    reviewed_count=self.reviewed_count
                ))
            return False
        
        return True
    
    def get_progress(self) -> Tuple[int, int]:
        """获取进度 (当前, 总数)"""
        return self.current_index + 1, len(self.questions)
```


## 主窗口重构

### 目录结构
```
ui/main_window/
├── __init__.py
├── window.py          # 主窗口UI
├── controller.py      # 主窗口控制器
└── panels.py          # 面板创建器
```

### window.py 设计

**职责**: 窗口框架、工具栏、菜单栏、面板组装

```python
class MainWindow(QMainWindow):
    """主窗口 - UI组装器"""
    
    def __init__(self, controller):
        """
        初始化主窗口
        
        Args:
            controller: MainWindowController实例
        """
        super().__init__()
        self.controller = controller
        self.setWindowTitle("错题本 - 智能学习管理")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建面板
        self.panel_factory = PanelFactory(controller)
        
        self._init_ui()
        self._connect_signals()
        
        # 初始加载
        self.controller.load_questions()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主布局
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
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
        
        splitter.setSizes([250, 700, 250])
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        
        self.statusBar().showMessage("就绪")
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 添加错题
        add_action = QAction("➕ 添加错题", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self.controller.show_add_dialog)
        toolbar.addAction(add_action)
        
        # 开始复习
        review_action = QAction("📚 开始复习", self)
        review_action.setShortcut(QKeySequence("Ctrl+R"))
        review_action.triggered.connect(self.controller.start_review)
        toolbar.addAction(review_action)
    
    def _connect_signals(self):
        """连接信号"""
        # 导航树选择
        self.nav_tree.item_selected.connect(
            self.controller.on_nav_filter_changed
        )
        
        # 筛选面板
        self.right_panel.filter_panel.filter_changed.connect(
            self.controller.on_filter_changed
        )
        
        # 搜索
        self.card_panel.search_input.textChanged.connect(
            self.controller.on_search
        )
```


### controller.py 设计

**职责**: 主窗口业务逻辑、视图状态管理

```python
class MainWindowController:
    """主窗口控制器"""
    
    def __init__(self, services, dialog_factory, event_bus):
        """
        初始化控制器
        
        Args:
            services: 服务集合 {question_service, review_service, ui_service}
            dialog_factory: 对话框工厂
            event_bus: 事件总线
        """
        self.question_service = services['question_service']
        self.review_service = services['review_service']
        self.ui_service = services['ui_service']
        self.dialog_factory = dialog_factory
        self.event_bus = event_bus
        
        # 视图状态
        self.current_view_type = "all"  # all, search, nav_filter, filter
        self.current_filters = {}
        self.current_questions = []
        
        # 订阅事件
        self._subscribe_events()
    
    def _subscribe_events(self):
        """订阅事件"""
        self.event_bus.subscribe(QuestionAddedEvent, self._on_question_added)
        self.event_bus.subscribe(QuestionUpdatedEvent, self._on_question_updated)
        self.event_bus.subscribe(QuestionDeletedEvent, self._on_question_deleted)
    
    def load_questions(self):
        """加载所有题目"""
        self.current_view_type = "all"
        self.current_filters = {}
        self.current_questions = self.ui_service.get_all_questions()
        return self.current_questions
    
    def on_search(self, keyword: str):
        """搜索事件"""
        self.current_view_type = "search"
        self.current_questions = self.ui_service.search_questions(keyword)
        return self.current_questions
    
    def on_nav_filter_changed(self, filter_data: Dict[str, Any]):
        """导航筛选变化"""
        self.current_view_type = "nav_filter"
        self.current_filters = filter_data
        self.current_questions = self.ui_service.filter_questions(filter_data)
        return self.current_questions
    
    def on_filter_changed(self, filters: Dict[str, Any]):
        """右侧筛选变化"""
        self.current_view_type = "filter"
        self.current_filters = filters
        self.current_questions = self.ui_service.filter_questions(filters)
        return self.current_questions
    
    def refresh_current_view(self):
        """刷新当前视图（保持筛选状态）"""
        if self.current_view_type == "all":
            return self.load_questions()
        elif self.current_view_type == "nav_filter" or self.current_view_type == "filter":
            self.current_questions = self.ui_service.filter_questions(self.current_filters)
            return self.current_questions
        return self.current_questions
    
    def show_add_dialog(self):
        """显示添加对话框"""
        dialog = self.dialog_factory.create_add_question_dialog()
        dialog.exec()
    
    def start_review(self):
        """开始复习"""
        # 显示模块选择器
        selector = self.dialog_factory.create_review_module_selector()
        selector.exec()
    
    def delete_question(self, question_id: int) -> Tuple[bool, str]:
        """删除题目"""
        success, message = self.question_service.delete_question(question_id)
        if success:
            self.event_bus.publish(QuestionDeletedEvent(question_id=question_id))
        return success, message
    
    def _on_question_added(self, event: QuestionAddedEvent):
        """题目添加事件处理"""
        self.refresh_current_view()
    
    def _on_question_updated(self, event: QuestionUpdatedEvent):
        """题目更新事件处理"""
        self.refresh_current_view()
    
    def _on_question_deleted(self, event: QuestionDeletedEvent):
        """题目删除事件处理"""
        self.refresh_current_view()
```


### panels.py 设计

**职责**: 创建各个面板组件

```python
class PanelFactory:
    """面板工厂 - 创建主窗口的各个面板"""
    
    def __init__(self, controller):
        """
        初始化面板工厂
        
        Args:
            controller: MainWindowController实例
        """
        self.controller = controller
    
    def create_navigation_panel(self) -> NavigationTree:
        """创建导航面板"""
        nav_tree = NavigationTree(self.controller.ui_service)
        return nav_tree
    
    def create_card_panel(self) -> QWidget:
        """创建卡片流面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 搜索框
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 搜索错题...")
        layout.addWidget(search_input)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # 卡片容器
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.addStretch()
        
        scroll.setWidget(cards_container)
        layout.addWidget(scroll)
        
        # 保存引用
        panel.search_input = search_input
        panel.cards_container = cards_container
        panel.cards_layout = cards_layout
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """创建右侧面板（筛选+统计）"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 筛选面板
        filter_panel = FilterPanel(self.controller.ui_service)
        layout.addWidget(filter_panel)
        
        # 统计面板
        stats_panel = StatisticsPanel(self.controller.ui_service)
        layout.addWidget(stats_panel)
        
        layout.addStretch()
        
        # 保存引用
        panel.filter_panel = filter_panel
        panel.stats_panel = stats_panel
        
        return panel
```

**关键改进**:
1. 主窗口从600行降至约200行（window）+ 200行（controller）+ 150行（panels）
2. 职责清晰：window负责UI，controller负责逻辑，panels负责创建
3. 使用组件组合，提高可维护性


## 工厂模式设计

### DialogFactory

**位置**: `ui/factories/dialog_factory.py`

**职责**: 创建对话框实例，注入依赖

```python
class DialogFactory:
    """对话框工厂 - 负责创建和配置对话框"""
    
    def __init__(self, services, event_bus):
        """
        初始化工厂
        
        Args:
            services: 服务字典 {question_service, review_service, ui_service}
            event_bus: 事件总线
        """
        self.question_service = services['question_service']
        self.review_service = services['review_service']
        self.ui_service = services['ui_service']
        self.event_bus = event_bus
    
    def create_add_question_dialog(self, parent=None):
        """创建添加错题对话框"""
        from ui.dialogs.add_question.controller import AddQuestionController
        from ui.dialogs.add_question.dialog import AddQuestionDialog
        
        controller = AddQuestionController(
            self.question_service,
            self.event_bus
        )
        return AddQuestionDialog(controller, parent)
    
    def create_detail_dialog(self, question_data, parent=None):
        """创建详情对话框"""
        from ui.dialogs.detail.controller import DetailDialogController
        from ui.dialogs.detail.dialog import DetailDialog
        
        controller = DetailDialogController(
            self.question_service,
            question_data,
            self.event_bus
        )
        return DetailDialog(controller, parent)
    
    def create_review_dialog(self, questions, parent=None):
        """创建复习对话框"""
        from ui.dialogs.review.controller import ReviewDialogController
        from ui.dialogs.review.dialog import ReviewDialog
        
        controller = ReviewDialogController(
            self.review_service,
            questions,
            self.event_bus
        )
        return ReviewDialog(controller, parent)
    
    def create_review_module_selector(self, parent=None):
        """创建复习模块选择器"""
        from ui.dialogs.review_module_selector import ReviewModuleSelectorDialog
        return ReviewModuleSelectorDialog(
            self.ui_service,
            self.review_service,
            parent
        )
```

**优势**:
1. 集中管理对话框创建逻辑
2. 自动注入依赖，避免在UI层直接创建服务
3. 易于测试（可以mock工厂）
4. 符合依赖倒置原则


## 事件总线设计

### EventBus

**位置**: `ui/events/event_bus.py`

**职责**: 组件间解耦通信

```python
from typing import Callable, Dict, List, Type
from .events import Event

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
            except ValueError:
                pass
    
    def publish(self, event: Event):
        """
        发布事件
        
        Args:
            event: 事件实例
        """
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"事件处理失败: {e}")
    
    def clear(self):
        """清空所有订阅（用于测试）"""
        self._handlers.clear()
```


### Events

**位置**: `ui/events/events.py`

**职责**: 定义所有事件类型

```python
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class Event:
    """基础事件类"""
    pass

@dataclass
class QuestionAddedEvent(Event):
    """题目添加事件"""
    question_id: int
    question_data: Dict[str, Any]

@dataclass
class QuestionUpdatedEvent(Event):
    """题目更新事件"""
    question_id: int
    updates: Dict[str, Any]

@dataclass
class QuestionDeletedEvent(Event):
    """题目删除事件"""
    question_id: int

@dataclass
class ReviewCompletedEvent(Event):
    """复习完成事件"""
    reviewed_count: int

@dataclass
class OCRCompletedEvent(Event):
    """OCR识别完成事件"""
    text: str
    success: bool

@dataclass
class FilterChangedEvent(Event):
    """筛选条件变化事件"""
    filters: Dict[str, Any]
```

### 使用示例

**发布事件**:
```python
# 在AddQuestionController中
def save_question(self, data):
    success, message, question_id = self.question_service.create_question(data)
    
    if success and self.event_bus:
        self.event_bus.publish(QuestionAddedEvent(
            question_id=question_id,
            question_data=data
        ))
    
    return success, message
```

**订阅事件**:
```python
# 在MainWindowController中
def __init__(self, ...):
    # ...
    self.event_bus.subscribe(QuestionAddedEvent, self._on_question_added)
    self.event_bus.subscribe(QuestionUpdatedEvent, self._on_question_updated)

def _on_question_added(self, event: QuestionAddedEvent):
    """处理题目添加事件"""
    self.refresh_current_view()
    self.stats_panel.update_statistics()
    self.nav_tree.refresh()
```

**优势**:
1. 组件间松耦合，不需要直接引用
2. 易于扩展，添加新事件不影响现有代码
3. 便于测试，可以mock事件总线
4. 支持多个订阅者


## 数据模型

### 组件接口数据结构

**ImageUploader**:
- 输入: 图片文件路径 (str)
- 输出: image_selected信号 (str)

**OCRPanel**:
- 输入: 图片路径 (str), OCR服务实例
- 输出: recognition_completed信号 (str), recognition_failed信号 (str)

**QuestionForm**:
- 输入/输出: Dict[str, Any]
  ```python
  {
      'subject': str,
      'question_type': str,
      'content': str,
      'my_answer': str,
      'answer': str,
      'explanation': str,
      'difficulty': int  # 1-5
  }
  ```

**FilterPanel**:
- 输出: Dict[str, Any]
  ```python
  {
      'subject': Optional[str],
      'difficulty': Optional[int],
      'mastery_level': Optional[int]
  }
  ```

### Controller数据流

**AddQuestionController**:
```
图片选择 -> OCR识别 -> 文本填充 -> 表单验证 -> 保存 -> 发布事件
```

**DetailDialogController**:
```
加载数据 -> 显示 -> 编辑 -> 检测变化 -> 保存 -> 发布事件
```

**MainWindowController**:
```
加载数据 -> 应用筛选 -> 显示卡片 -> 监听事件 -> 刷新视图
```


## 正确性属性 (Correctness Properties)

*属性是一种特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 组件独立性属性

**Property 1: 组件可独立实例化**
*对于任何*可复用组件（ImageUploader, OCRPanel, QuestionForm, FilterPanel, StatisticsPanel, NavigationTree），该组件应该能够在没有完整应用上下文的情况下被实例化并正常工作
**验证: Requirements 3.2**

**Property 2: 组件接受依赖注入**
*对于任何*需要服务的组件，该组件应该通过构造函数接受服务实例，而不是在内部创建服务
**验证: Requirements 4.3**

**Property 3: 组件可在多处复用**
*对于任何*可复用组件，该组件应该能够在不同的对话框或窗口中被多次实例化，每个实例独立工作互不干扰
**验证: Requirements 2.1, 2.2, 2.3**

### 代码质量属性

**Property 4: 组件文件行数限制**
*对于任何*重构后的组件文件，该文件的代码行数应该不超过200行（不包括空行和注释）
**验证: Requirements 1.1**

**Property 5: 方法行数限制**
*对于任何*重构后的方法，该方法的代码行数应该不超过30行（不包括空行和注释）
**验证: Requirements 1.2**

### 架构模式属性

**Property 6: 工厂模式创建对话框**
*对于任何*对话框实例，该对话框应该通过DialogFactory创建，而不是直接在UI代码中实例化
**验证: Requirements 4.1**

**Property 7: 事件总线解耦通信**
*对于任何*跨组件的状态变化通知，应该通过EventBus发布事件，而不是直接调用其他组件的方法
**验证: Requirements 4.2**

### Dialog-Controller分离属性

**Property 8: Dialog只包含UI代码**
*对于任何*重构后的Dialog类，该类应该只包含UI组装、布局和信号连接代码，不包含业务逻辑
**验证: Requirements 1.3**

**Property 9: Controller处理业务逻辑**
*对于任何*重构后的Controller类，该类应该处理所有业务逻辑、数据验证和服务调用，不包含UI代码
**验证: Requirements 1.3**

**Property 10: Controller可独立测试**
*对于任何*Controller类，该类应该能够在没有UI的情况下被实例化和测试，通过mock服务验证业务逻辑
**验证: Requirements 3.1, 3.3**

### 组件接口属性

**Property 11: 组件提供清晰信号接口**
*对于任何*可复用组件，该组件应该通过PyQt信号暴露其状态变化，而不是要求调用者轮询或直接访问内部状态
**验证: Requirements 2.1, 2.2, 2.3**

**Property 12: QuestionForm数据往返一致性**
*对于任何*有效的题目数据字典，调用QuestionForm.set_data(data)然后QuestionForm.get_data()应该返回等价的数据
**验证: Requirements 2.3**


## 错误处理

### 组件级错误处理

**ImageUploader**:
- 图片加载失败：显示错误提示，不发送image_selected信号
- 不支持的文件格式：显示格式错误提示
- 中文路径问题：使用PIL加载，避免QPixmap的中文路径bug

**OCRPanel**:
- OCR引擎未初始化：显示等待提示，提供重试机制
- 识别失败：显示失败原因，允许重新识别
- 网络错误（模型下载）：提供清晰的错误信息和解决方案

**QuestionForm**:
- 必填字段为空：validate()返回False和错误信息
- 数据格式错误：在set_data()中进行类型检查

### Controller级错误处理

**AddQuestionController**:
- 保存失败：返回(False, error_message)，不发布事件
- OCR识别失败：记录日志，允许用户手动输入
- 图片复制失败：记录警告，使用原路径

**DetailDialogController**:
- 更新失败：返回错误信息，不更新original_data
- 数据不存在：在初始化时检查，提前返回

**MainWindowController**:
- 服务调用失败：捕获异常，显示用户友好的错误信息
- 事件处理失败：记录日志，不影响其他订阅者

### 事件总线错误处理

- 事件处理器异常：捕获并记录，不影响其他处理器
- 订阅/取消订阅错误：静默处理，记录日志

### 错误日志

所有错误都应该通过Python logging模块记录：
```python
import logging
logger = logging.getLogger(__name__)

try:
    # 操作
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```


## 测试策略

### 双重测试方法

本项目采用**单元测试**和**属性测试**相结合的方式：

- **单元测试**: 验证具体示例、边界情况和错误条件
- **属性测试**: 验证跨所有输入的通用属性
- 两者互补：单元测试捕获具体bug，属性测试验证通用正确性

### 组件单元测试

**ImageUploader测试**:
```python
# tests/ui/components/test_image_uploader.py
def test_image_uploader_initialization():
    """测试组件可以独立初始化"""
    uploader = ImageUploader()
    assert uploader is not None
    assert uploader.get_image_path() is None

def test_image_uploader_load_valid_image():
    """测试加载有效图片"""
    uploader = ImageUploader()
    test_image = "tests/fixtures/test_image.png"
    uploader.set_image(test_image)
    assert uploader.get_image_path() == test_image

def test_image_uploader_signal_emission():
    """测试信号发送"""
    uploader = ImageUploader()
    signal_received = []
    uploader.image_selected.connect(lambda path: signal_received.append(path))
    
    uploader.set_image("test.png")
    assert len(signal_received) == 1
```

**QuestionForm测试**:
```python
# tests/ui/components/test_question_form.py
def test_question_form_data_round_trip():
    """测试数据往返一致性"""
    form = QuestionForm()
    test_data = {
        'subject': '数学',
        'question_type': '单选题',
        'content': '测试题目',
        'my_answer': '我的答案',
        'answer': '正确答案',
        'explanation': '解析',
        'difficulty': 3
    }
    
    form.set_data(test_data)
    result = form.get_data()
    
    assert result == test_data

def test_question_form_validation():
    """测试表单验证"""
    form = QuestionForm()
    
    # 空内容应该验证失败
    form.set_data({'content': '', 'answer': '答案'})
    is_valid, error = form.validate()
    assert not is_valid
    assert '内容' in error
```

### Controller单元测试

**AddQuestionController测试**:
```python
# tests/ui/dialogs/test_add_question_controller.py
def test_controller_save_question_success():
    """测试保存成功场景"""
    mock_service = Mock()
    mock_service.create_question.return_value = (True, "成功", 123)
    
    controller = AddQuestionController(mock_service)
    success, message = controller.save_question({
        'content': '测试',
        'answer': '答案'
    })
    
    assert success
    assert mock_service.create_question.called

def test_controller_with_mock_service():
    """测试可以使用mock服务"""
    mock_service = Mock()
    controller = AddQuestionController(mock_service)
    assert controller.question_service == mock_service
```

### 属性测试配置

使用**Hypothesis**库进行属性测试（Python的属性测试框架）：

```python
# tests/ui/properties/test_component_properties.py
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_question_form_content_preservation(content):
    """
    Property 12: QuestionForm数据往返一致性
    Feature: ui-refactoring, Property 12: QuestionForm数据往返一致性
    """
    form = QuestionForm()
    data = {'content': content, 'answer': 'test'}
    form.set_data(data)
    result = form.get_data()
    assert result['content'] == content
```

**属性测试配置**:
- 每个属性测试至少运行100次迭代
- 使用Hypothesis的@given装饰器生成随机输入
- 每个测试用注释标记对应的设计属性

### 集成测试

**对话框集成测试**:
```python
# tests/ui/integration/test_add_dialog_integration.py
def test_add_dialog_with_real_services():
    """测试对话框与真实服务的集成"""
    # 使用测试数据库
    services = create_test_services()
    factory = DialogFactory(services, EventBus())
    
    dialog = factory.create_add_question_dialog()
    assert dialog is not None
    assert dialog.controller is not None
```

### 测试覆盖率目标

- **组件单元测试**: > 70%
- **Controller单元测试**: > 80%
- **属性测试**: 覆盖所有12个正确性属性
- **集成测试**: 覆盖主要用户流程

### 测试工具

- **pytest**: 测试框架
- **pytest-qt**: PyQt测试支持
- **hypothesis**: 属性测试
- **unittest.mock**: Mock对象
- **pytest-cov**: 覆盖率报告


## 迁移策略

### 向后兼容性

为了确保平滑迁移，采用以下策略：

**1. 保留旧接口**:
```python
# ui/dialogs/__init__.py
from ui.dialogs.add_question.dialog import AddQuestionDialog as AddQuestionDialogNew
from ui.dialogs.add_dialog import AddQuestionDialog as AddQuestionDialogOld

# 提供别名，逐步迁移
AddQuestionDialog = AddQuestionDialogNew  # 新代码使用新版本

# 标记旧版本为废弃
import warnings
def create_old_add_dialog(*args, **kwargs):
    warnings.warn(
        "AddQuestionDialogOld is deprecated, use AddQuestionDialogNew",
        DeprecationWarning
    )
    return AddQuestionDialogOld(*args, **kwargs)
```

**2. 渐进式迁移**:
- Phase 1: 创建新组件和对话框，旧代码继续工作
- Phase 2: 新功能使用新架构
- Phase 3: 逐步迁移现有调用
- Phase 4: 删除旧代码

**3. 功能标志**:
```python
# config/settings.py
USE_NEW_UI_ARCHITECTURE = True  # 可以通过配置切换

# main.py
if USE_NEW_UI_ARCHITECTURE:
    from ui.main_window.window import MainWindow
else:
    from ui.main_window_old import MainWindow
```

### 迁移步骤

**Step 1: 创建新组件** (不影响现有代码)
- 创建ui/components/目录
- 实现所有可复用组件
- 编写组件单元测试

**Step 2: 创建新对话框** (并行存在)
- 创建ui/dialogs/add_question/目录
- 实现新的Dialog和Controller
- 保留旧的add_dialog.py

**Step 3: 创建工厂和事件总线** (基础设施)
- 实现DialogFactory
- 实现EventBus
- 编写测试

**Step 4: 重构主窗口** (关键迁移)
- 创建ui/main_window/目录
- 实现新的Window、Controller、Panels
- 更新main.py使用新主窗口

**Step 5: 迁移调用点**
- 更新所有创建对话框的地方使用DialogFactory
- 更新所有直接调用的地方使用EventBus

**Step 6: 清理旧代码**
- 删除旧的main_window.py
- 删除旧的add_dialog.py
- 删除旧的detail_dialog.py
- 更新文档

### 回滚计划

如果迁移出现问题，可以快速回滚：

```python
# config/settings.py
USE_NEW_UI_ARCHITECTURE = False  # 切换回旧版本
```

所有旧代码在确认新版本稳定前保留，确保可以随时回滚。

### 数据兼容性

UI重构不涉及数据库schema变更，因此：
- 数据库完全兼容
- 图片路径处理保持一致
- 服务层接口不变


## 性能考虑

### 组件实例化

**问题**: 频繁创建组件可能影响性能

**解决方案**:
- 组件设计为轻量级，实例化开销小
- 对于重量级组件（如OCRPanel），考虑延迟初始化
- 使用对象池复用组件实例（如果需要）

### 事件总线性能

**问题**: 大量事件可能影响性能

**解决方案**:
- 事件处理器应该快速返回
- 耗时操作在后台线程执行
- 避免在事件处理器中进行同步IO

### UI刷新优化

**问题**: 频繁刷新UI可能导致卡顿

**解决方案**:
- 使用防抖（debounce）减少刷新频率
- 批量更新卡片，而不是逐个更新
- 使用虚拟滚动（如果卡片数量很大）

```python
# 防抖示例
from PyQt6.QtCore import QTimer

class MainWindowController:
    def __init__(self):
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh)
    
    def refresh_current_view(self):
        """延迟刷新，避免频繁更新"""
        self._refresh_timer.start(300)  # 300ms后刷新
    
    def _do_refresh(self):
        """实际执行刷新"""
        # ...
```

### 内存管理

**问题**: 组件未正确释放可能导致内存泄漏

**解决方案**:
- 确保信号槽正确断开
- 使用Qt的父子关系自动管理内存
- 在组件销毁时清理资源

```python
class ImageUploader(QWidget):
    def __del__(self):
        """清理资源"""
        if self._current_image_path:
            # 清理临时文件等
            pass
```


## 依赖关系

### 组件依赖图

```
┌─────────────────────────────────────────────────────────┐
│                    Application                          │
│                         │                               │
│                         ▼                               │
│                  ┌─────────────┐                        │
│                  │ MainWindow  │                        │
│                  └─────────────┘                        │
│                         │                               │
│         ┌───────────────┼───────────────┐              │
│         ▼               ▼               ▼              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │NavigationTree│ │ CardPanel  │  │RightPanel  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│                                    │         │          │
│                                    ▼         ▼          │
│                            ┌────────────┐ ┌────────────┐│
│                            │FilterPanel │ │StatsPanel  ││
│                            └────────────┘ └────────────┘│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Dialog Factory                          │
│                         │                               │
│         ┌───────────────┼───────────────┐              │
│         ▼               ▼               ▼              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │AddQuestion │  │   Detail   │  │   Review   │       │
│  │  Dialog    │  │   Dialog   │  │   Dialog   │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │               │               │              │
│         ▼               ▼               ▼              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │AddQuestion │  │   Detail   │  │   Review   │       │
│  │ Controller │  │ Controller │  │ Controller │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │               │               │              │
│         └───────────────┴───────────────┘              │
│                         │                               │
│                         ▼                               │
│                  ┌─────────────┐                        │
│                  │  Services   │                        │
│                  └─────────────┘                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Components                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ImageUploader│ │  OCRPanel  │  │QuestionForm│        │
│  └────────────┘  └────────────┘  └────────────┘        │
│                                                          │
│  可被多个Dialog使用                                      │
└─────────────────────────────────────────────────────────┘
```

### 外部依赖

**Python标准库**:
- typing: 类型注解
- dataclasses: 事件定义
- logging: 日志记录
- pathlib: 路径处理

**PyQt6**:
- QtWidgets: UI组件
- QtCore: 信号槽、线程
- QtGui: 图形相关

**第三方库**:
- PIL (Pillow): 图片处理
- pytest: 测试框架
- hypothesis: 属性测试

**内部依赖**:
- services层: QuestionService, ReviewService, UIService
- core层: DataManager, ReviewScheduler
- database层: DatabaseManager
- utils层: validators, image_processor

### 依赖注入

所有服务通过构造函数注入，避免在UI层创建服务实例：

```python
# ❌ 错误：在UI中创建服务
class AddQuestionDialog(QDialog):
    def __init__(self):
        self.question_service = QuestionService(...)  # 不好

# ✅ 正确：通过依赖注入
class AddQuestionDialog(QDialog):
    def __init__(self, controller):
        self.controller = controller  # controller包含服务

# ✅ 正确：工厂负责创建和注入
class DialogFactory:
    def create_add_question_dialog(self):
        controller = AddQuestionController(self.question_service)
        return AddQuestionDialog(controller)
```


## 实施顺序

### Phase 1: 基础组件 (2天)

**目标**: 创建可复用的UI组件

**任务**:
1. 创建ui/components/目录结构
2. 实现ImageUploader组件
3. 实现OCRPanel组件
4. 实现QuestionForm组件
5. 实现FilterPanel组件
6. 实现StatisticsPanel组件
7. 实现NavigationTree组件
8. 为每个组件编写单元测试

**验收标准**:
- 所有组件可以独立实例化
- 所有组件测试通过
- 组件文件不超过200行

### Phase 2: 对话框重构 (3天)

**目标**: 重构AddQuestionDialog为Dialog-Controller模式

**任务**:
1. 创建ui/dialogs/add_question/目录
2. 实现AddQuestionController
3. 实现AddQuestionDialog（使用新组件）
4. 编写Controller单元测试
5. 编写Dialog集成测试
6. 重构DetailDialog
7. 重构ReviewDialog

**验收标准**:
- Dialog代码不超过200行
- Controller可以独立测试
- 所有测试通过

### Phase 3: 主窗口重构 (3天)

**目标**: 重构MainWindow为模块化结构

**任务**:
1. 创建ui/main_window/目录
2. 实现MainWindowController
3. 实现PanelFactory
4. 实现MainWindow（使用新组件和面板）
5. 编写Controller单元测试
6. 更新main.py使用新主窗口

**验收标准**:
- 主窗口代码拆分为3个文件，每个不超过250行
- Controller可以独立测试
- 所有功能正常工作

### Phase 4: 工厂和事件总线 (1天)

**目标**: 引入工厂模式和事件总线

**任务**:
1. 创建ui/factories/目录
2. 实现DialogFactory
3. 创建ui/events/目录
4. 实现EventBus
5. 定义所有事件类型
6. 更新Controller使用EventBus
7. 更新MainWindow使用DialogFactory
8. 编写工厂和事件总线测试

**验收标准**:
- 所有对话框通过工厂创建
- 组件间通信使用事件总线
- 测试覆盖率 > 80%

### Phase 5: 测试和文档 (2天)

**目标**: 完善测试和文档

**任务**:
1. 编写属性测试（12个属性）
2. 编写集成测试
3. 运行覆盖率报告
4. 编写组件使用文档
5. 编写迁移指南
6. 代码审查和优化

**验收标准**:
- 所有属性测试通过
- 测试覆盖率达标
- 文档完整

### Phase 6: 清理和发布 (1天)

**目标**: 清理旧代码，发布新版本

**任务**:
1. 标记旧代码为deprecated
2. 更新所有调用点
3. 删除旧代码
4. 更新CHANGELOG
5. 发布新版本

**验收标准**:
- 旧代码已删除
- 所有功能正常
- 文档已更新

## 总时间: 12天


## 风险和缓解措施

### 风险1: 重构破坏现有功能

**影响**: 高
**概率**: 中

**缓解措施**:
- 保留旧代码直到新代码稳定
- 使用功能标志控制新旧版本切换
- 编写全面的测试覆盖
- 渐进式迁移，每个阶段验证功能

### 风险2: 性能下降

**影响**: 中
**概率**: 低

**缓解措施**:
- 组件设计为轻量级
- 使用性能分析工具监控
- 优化事件总线性能
- 实施防抖和批量更新

### 风险3: 学习曲线

**影响**: 中
**概率**: 中

**缓解措施**:
- 编写详细的组件使用文档
- 提供代码示例
- 进行代码审查和知识分享
- 逐步引入新模式

### 风险4: 测试覆盖不足

**影响**: 高
**概率**: 中

**缓解措施**:
- 设定明确的覆盖率目标
- 使用属性测试增加覆盖
- 代码审查检查测试质量
- 持续集成自动运行测试

### 风险5: 事件总线复杂性

**影响**: 中
**概率**: 低

**缓解措施**:
- 限制事件类型数量
- 清晰的事件命名和文档
- 提供事件调试工具
- 避免事件循环依赖

## 成功指标

### 代码质量指标

- ✅ 单个文件不超过300行
- ✅ 单个方法不超过30行
- ✅ 代码重复率 < 5%
- ✅ 圈复杂度 < 10

### 测试指标

- ✅ 组件单元测试覆盖率 > 70%
- ✅ Controller单元测试覆盖率 > 80%
- ✅ 所有12个属性测试通过
- ✅ 集成测试覆盖主要流程

### 可维护性指标

- ✅ 新增功能开发时间减少30%
- ✅ Bug修复时间减少40%
- ✅ 代码审查时间减少50%
- ✅ 组件可在3个以上地方复用

### 性能指标

- ✅ UI响应时间 < 100ms
- ✅ 对话框打开时间 < 200ms
- ✅ 内存使用不增加 > 10%

## 参考资料

### 设计模式

- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
- [Observer Pattern](https://refactoring.guru/design-patterns/observer)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)

### PyQt最佳实践

- [Qt Model/View Programming](https://doc.qt.io/qt-6/model-view-programming.html)
- [Signals and Slots](https://doc.qt.io/qt-6/signalsandslots.html)
- [Qt Thread Basics](https://doc.qt.io/qt-6/thread-basics.html)

### 测试

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)

### 代码质量

- [PEP 8 Style Guide](https://pep8.org/)
- [Clean Code Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**文档版本**: 1.0  
**创建日期**: 2025-02-04  
**最后更新**: 2025-02-04  
**状态**: 待审核  
**作者**: Kiro AI Assistant

