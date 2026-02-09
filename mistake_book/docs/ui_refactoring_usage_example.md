# UI重构使用示例

本文档展示如何使用重构后的UI组件和架构。

## 1. 使用DialogFactory创建对话框

### 初始化工厂

```python
from mistake_book.ui.factories import DialogFactory
from mistake_book.ui.events import EventBus

# 准备服务
services = {
    'question_service': question_service,
    'review_service': review_service,
    'ui_service': ui_service
}

# 创建事件总线
event_bus = EventBus()

# 创建对话框工厂
dialog_factory = DialogFactory(services, event_bus)
```

### 创建添加错题对话框

```python
# 使用工厂创建对话框
dialog = dialog_factory.create_add_question_dialog(parent=main_window)

# 显示对话框
if dialog.exec():
    print("题目添加成功")
```

## 2. 使用EventBus订阅事件

### 在主窗口中订阅事件

```python
from mistake_book.ui.events import (
    EventBus,
    QuestionAddedEvent,
    QuestionUpdatedEvent,
    QuestionDeletedEvent
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 获取事件总线
        self.event_bus = EventBus()
        
        # 订阅事件
        self.event_bus.subscribe(QuestionAddedEvent, self.on_question_added)
        self.event_bus.subscribe(QuestionUpdatedEvent, self.on_question_updated)
        self.event_bus.subscribe(QuestionDeletedEvent, self.on_question_deleted)
    
    def on_question_added(self, event: QuestionAddedEvent):
        """题目添加事件处理"""
        print(f"新题目已添加: ID={event.question_id}")
        # 刷新题目列表
        self.refresh_questions()
    
    def on_question_updated(self, event: QuestionUpdatedEvent):
        """题目更新事件处理"""
        print(f"题目已更新: ID={event.question_id}")
        # 刷新题目列表
        self.refresh_questions()
    
    def on_question_deleted(self, event: QuestionDeletedEvent):
        """题目删除事件处理"""
        print(f"题目已删除: ID={event.question_id}")
        # 刷新题目列表
        self.refresh_questions()
```

## 3. 使用可复用组件

### 使用ImageUploader

```python
from mistake_book.ui.components import ImageUploader

class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建图片上传组件
        self.image_uploader = ImageUploader()
        
        # 连接信号
        self.image_uploader.image_selected.connect(self.on_image_selected)
        self.image_uploader.image_cleared.connect(self.on_image_cleared)
        
        # 添加到布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_uploader)
    
    def on_image_selected(self, path: str):
        print(f"选择了图片: {path}")
    
    def on_image_cleared(self):
        print("图片已清空")
```

### 使用OCRPanel

```python
from mistake_book.ui.components import OCRPanel

class MyDialog(QDialog):
    def __init__(self, question_service, parent=None):
        super().__init__(parent)
        
        # 创建OCR面板
        self.ocr_panel = OCRPanel(question_service)
        
        # 连接信号
        self.ocr_panel.recognition_completed.connect(self.on_ocr_completed)
        self.ocr_panel.recognition_failed.connect(self.on_ocr_failed)
        
        # 添加到布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.ocr_panel)
    
    def on_ocr_completed(self, text: str):
        print(f"识别完成: {text}")
    
    def on_ocr_failed(self, message: str):
        print(f"识别失败: {message}")
```

### 使用QuestionForm

```python
from mistake_book.ui.components import QuestionForm

class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建表单
        self.question_form = QuestionForm()
        
        # 连接信号
        self.question_form.data_changed.connect(self.on_data_changed)
        
        # 添加到布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.question_form)
        
        # 添加保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
    
    def on_data_changed(self):
        print("表单数据已变化")
    
    def save(self):
        # 验证表单
        valid, error_msg = self.question_form.validate()
        if not valid:
            QMessageBox.warning(self, "验证失败", error_msg)
            return
        
        # 获取数据
        data = self.question_form.get_data()
        print(f"保存数据: {data}")
```

### 组合使用多个组件

```python
from mistake_book.ui.components import (
    ImageUploader, 
    OCRPanel, 
    QuestionForm
)

class AddQuestionDialog(QDialog):
    def __init__(self, question_service, parent=None):
        super().__init__(parent)
        
        # 创建组件
        self.image_uploader = ImageUploader()
        self.ocr_panel = OCRPanel(question_service)
        self.question_form = QuestionForm()
        
        # 连接信号：图片选择 -> OCR识别
        self.image_uploader.image_selected.connect(
            self.ocr_panel.recognize_image
        )
        
        # 连接信号：OCR完成 -> 填充表单
        self.ocr_panel.recognition_completed.connect(
            self.question_form.set_content
        )
        
        # 布局
        layout = QVBoxLayout(self)
        
        upload_group = QGroupBox("图片上传")
        upload_layout = QVBoxLayout()
        upload_layout.addWidget(self.image_uploader)
        upload_layout.addWidget(self.ocr_panel)
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        form_group = QGroupBox("题目信息")
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.question_form)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
```

## 4. 使用FilterPanel和StatisticsPanel

```python
from mistake_book.ui.components import FilterPanel, StatisticsPanel

class MainWindow(QMainWindow):
    def __init__(self, ui_service):
        super().__init__()
        
        # 创建筛选面板
        self.filter_panel = FilterPanel(ui_service)
        self.filter_panel.filter_changed.connect(self.on_filter_changed)
        
        # 创建统计面板
        self.stats_panel = StatisticsPanel(ui_service)
        
        # 布局
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        layout.addWidget(self.filter_panel)
        layout.addWidget(self.stats_panel)
        layout.addStretch()
    
    def on_filter_changed(self, filters: dict):
        print(f"筛选条件变化: {filters}")
        # 应用筛选
        self.apply_filters(filters)
        # 更新统计
        self.stats_panel.update_statistics()
```

## 5. 使用NavigationTree

```python
from mistake_book.ui.components import NavigationTree

class MainWindow(QMainWindow):
    def __init__(self, ui_service):
        super().__init__()
        
        # 创建导航树
        self.nav_tree = NavigationTree(ui_service)
        self.nav_tree.item_selected.connect(self.on_nav_item_selected)
        
        # 布局
        left_panel = QWidget()
        layout = QVBoxLayout(left_panel)
        layout.addWidget(self.nav_tree)
    
    def on_nav_item_selected(self, data: dict):
        print(f"选中导航项: {data}")
        # 获取筛选条件
        filters = self.nav_tree.get_selected_filter()
        if filters:
            self.apply_filters(filters)
    
    def refresh_navigation(self):
        """刷新导航树"""
        self.nav_tree.refresh()
```

## 6. 完整示例：使用新架构的主窗口

```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from mistake_book.ui.factories import DialogFactory
from mistake_book.ui.events import EventBus, QuestionAddedEvent
from mistake_book.ui.components import (
    NavigationTree,
    FilterPanel,
    StatisticsPanel
)

class MainWindow(QMainWindow):
    def __init__(self, services):
        super().__init__()
        
        # 创建事件总线
        self.event_bus = EventBus()
        
        # 创建对话框工厂
        self.dialog_factory = DialogFactory(services, self.event_bus)
        
        # 订阅事件
        self.event_bus.subscribe(QuestionAddedEvent, self.on_question_added)
        
        # 创建UI
        self.init_ui(services['ui_service'])
    
    def init_ui(self, ui_service):
        """初始化UI"""
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # 创建三栏分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左栏：导航树
        self.nav_tree = NavigationTree(ui_service)
        self.nav_tree.item_selected.connect(self.on_nav_filter_changed)
        splitter.addWidget(self.nav_tree)
        
        # 中栏：卡片流（省略）
        center_panel = QWidget()
        splitter.addWidget(center_panel)
        
        # 右栏：筛选和统计
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.filter_panel = FilterPanel(ui_service)
        self.filter_panel.filter_changed.connect(self.on_filter_changed)
        right_layout.addWidget(self.filter_panel)
        
        self.stats_panel = StatisticsPanel(ui_service)
        right_layout.addWidget(self.stats_panel)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        splitter.setSizes([250, 700, 250])
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
    
    def show_add_dialog(self):
        """显示添加对话框"""
        dialog = self.dialog_factory.create_add_question_dialog(self)
        dialog.exec()
    
    def on_question_added(self, event: QuestionAddedEvent):
        """题目添加事件处理"""
        # 刷新导航树
        self.nav_tree.refresh()
        # 更新统计
        self.stats_panel.update_statistics()
        # 刷新题目列表
        self.refresh_questions()
    
    def on_nav_filter_changed(self, data: dict):
        """导航筛选变化"""
        filters = self.nav_tree.get_selected_filter()
        if filters:
            self.apply_filters(filters)
    
    def on_filter_changed(self, filters: dict):
        """右侧筛选变化"""
        self.apply_filters(filters)
    
    def apply_filters(self, filters: dict):
        """应用筛选条件"""
        print(f"应用筛选: {filters}")
        # 实现筛选逻辑
        pass
    
    def refresh_questions(self):
        """刷新题目列表"""
        print("刷新题目列表")
        # 实现刷新逻辑
        pass
```

## 7. 迁移指南

### 从旧版本迁移到新版本

**步骤1：更新导入**
```python
# 旧版本
from mistake_book.ui.dialogs.add_dialog import AddQuestionDialog

# 新版本
from mistake_book.ui.factories import DialogFactory
```

**步骤2：使用工厂创建对话框**
```python
# 旧版本
dialog = AddQuestionDialog(question_service, parent)

# 新版本
factory = DialogFactory(services, event_bus)
dialog = factory.create_add_question_dialog(parent)
```

**步骤3：订阅事件**
```python
# 新增：订阅事件以响应对话框操作
event_bus = EventBus()
event_bus.subscribe(QuestionAddedEvent, self.on_question_added)
```

---

**文档版本**: 1.0  
**创建时间**: 2026-02-06
