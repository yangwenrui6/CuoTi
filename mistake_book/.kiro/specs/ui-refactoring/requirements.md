# UI层重构 - 需求文档

## 📋 项目概述

**目标**: 重构UI层，降低耦合度，提高可维护性和可测试性

**当前问题**:
1. UI文件过长（main_window.py 600+行，add_dialog.py 600+行）
2. 职责不清晰，一个类做太多事情
3. 组件耦合度高，难以复用
4. 缺少UI组件的单元测试
5. 直接在UI层创建对话框，违反依赖倒置原则

**预期收益**:
- 代码更易理解和维护
- 组件可复用
- 易于编写单元测试
- 新功能开发更快

---

## 🎯 用户故事

### 1. 作为开发者，我希望UI组件职责单一
**验收标准**:
- 每个UI组件类不超过200行
- 每个方法不超过30行
- 每个类只负责一个功能模块

### 2. 作为开发者，我希望UI组件可复用
**验收标准**:
- 图片上传组件可以在多个对话框中使用
- OCR面板可以独立使用
- 表单组件可以组合使用

### 3. 作为开发者，我希望UI层易于测试
**验收标准**:
- UI组件可以独立测试
- 不依赖完整的应用上下文
- 可以mock服务层

### 4. 作为开发者，我希望添加新功能时不影响现有代码
**验收标准**:
- 使用工厂模式创建对话框
- 使用事件总线解耦组件通信
- 使用依赖注入传递服务

---

## 📐 架构设计

### 当前结构
```
ui/
├── dialogs/
│   ├── add_dialog.py          # 600+ 行
│   ├── detail_dialog.py       # 400+ 行
│   ├── review_dialog_new.py
│   └── ...
├── widgets/
│   ├── question_card.py
│   └── ...
├── viewmodels/
│   └── question_vm.py
└── main_window.py             # 600+ 行
```

### 目标结构
```
ui/
├── components/                 # 可复用组件
│   ├── image_uploader.py      # 图片上传组件
│   ├── ocr_panel.py           # OCR识别面板
│   ├── question_form.py       # 题目表单
│   ├── tag_selector.py        # 标签选择器
│   ├── filter_panel.py        # 筛选面板
│   ├── statistics_panel.py    # 统计面板
│   └── navigation_tree.py     # 导航树
├── dialogs/
│   ├── add_question/          # 添加错题对话框模块
│   │   ├── dialog.py          # 主对话框（协调器）
│   │   └── controller.py      # 业务逻辑控制器
│   ├── detail/                # 详情对话框模块
│   │   ├── dialog.py
│   │   └── controller.py
│   └── review/                # 复习对话框模块
│       ├── dialog.py
│       └── controller.py
├── factories/                  # 工厂类
│   ├── dialog_factory.py      # 对话框工厂
│   └── component_factory.py   # 组件工厂
├── events/                     # 事件系统
│   ├── event_bus.py           # 事件总线
│   └── events.py              # 事件定义
├── viewmodels/                 # 视图模型
│   ├── question_vm.py
│   ├── review_vm.py
│   └── main_vm.py
├── widgets/                    # 自定义控件
│   ├── question_card.py
│   └── ...
└── main_window/               # 主窗口模块
    ├── window.py              # 主窗口（协调器）
    ├── controller.py          # 业务逻辑控制器
    └── panels.py              # 面板创建器
```

---

## 🔧 重构策略

### 阶段1: 提取可复用组件（1-2天）
**目标**: 将重复的UI代码提取为独立组件

#### 1.1 图片上传组件
**当前位置**: `add_dialog.py` 中的 `DropZoneWidget`
**目标位置**: `ui/components/image_uploader.py`
**功能**:
- 拖拽上传
- 点击选择
- 图片预览
- 查看大图

**接口设计**:
```python
class ImageUploader(QWidget):
    image_selected = pyqtSignal(str)  # 图片路径
    
    def __init__(self, parent=None):
        pass
    
    def get_image_path(self) -> Optional[str]:
        pass
    
    def clear(self):
        pass
```

#### 1.2 OCR识别面板
**当前位置**: `add_dialog.py` 中的OCR相关代码
**目标位置**: `ui/components/ocr_panel.py`
**功能**:
- 显示OCR状态
- 触发识别
- 显示识别结果

**接口设计**:
```python
class OCRPanel(QWidget):
    recognition_completed = pyqtSignal(str)  # 识别文本
    
    def __init__(self, ocr_service, parent=None):
        pass
    
    def recognize_image(self, image_path: str):
        pass
    
    def set_status(self, status: str):
        pass
```

#### 1.3 题目表单组件
**当前位置**: `add_dialog.py` 中的表单部分
**目标位置**: `ui/components/question_form.py`
**功能**:
- 科目选择
- 题型选择
- 内容输入
- 答案输入
- 难度选择

**接口设计**:
```python
class QuestionForm(QWidget):
    def __init__(self, parent=None):
        pass
    
    def get_data(self) -> Dict[str, Any]:
        pass
    
    def set_data(self, data: Dict[str, Any]):
        pass
    
    def validate(self) -> Tuple[bool, str]:
        pass
    
    def clear(self):
        pass
```

#### 1.4 标签选择器
**当前位置**: `add_dialog.py` 中的 `TagSelector`
**目标位置**: `ui/components/tag_selector.py`
**功能**:
- 搜索标签
- 选择标签
- 显示已选标签

#### 1.5 筛选面板
**当前位置**: `main_window.py` 中的右侧面板
**目标位置**: `ui/components/filter_panel.py`
**功能**:
- 科目筛选
- 难度筛选
- 掌握度筛选

#### 1.6 统计面板
**当前位置**: `main_window.py` 中的统计部分
**目标位置**: `ui/components/statistics_panel.py`
**功能**:
- 显示总题数
- 显示掌握度分布
- 显示待复习数量

#### 1.7 导航树
**当前位置**: `main_window.py` 中的左侧导航
**目标位置**: `ui/components/navigation_tree.py`
**功能**:
- 显示科目树
- 显示标签树
- 显示掌握度分类

---

### 阶段2: 重构对话框（2-3天）
**目标**: 将大型对话框拆分为模块化结构

#### 2.1 添加错题对话框重构
**当前**: `add_dialog.py` (600+行)
**目标**: 拆分为多个文件

**新结构**:
```
ui/dialogs/add_question/
├── __init__.py
├── dialog.py           # 主对话框（100行）
├── controller.py       # 业务逻辑（150行）
└── README.md          # 模块说明
```

**dialog.py 职责**:
- 组装UI组件
- 处理布局
- 连接信号槽

**controller.py 职责**:
- 处理业务逻辑
- 调用服务层
- 数据验证

**示例代码**:
```python
# dialog.py
class AddQuestionDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        # 创建组件
        self.image_uploader = ImageUploader()
        self.ocr_panel = OCRPanel(self.controller.ocr_service)
        self.question_form = QuestionForm()
        self.tag_selector = TagSelector()
        
        # 连接信号
        self.image_uploader.image_selected.connect(
            self.controller.on_image_selected
        )
        self.ocr_panel.recognition_completed.connect(
            self.controller.on_ocr_completed
        )
        
        # 布局
        self.setup_layout()

# controller.py
class AddQuestionController:
    def __init__(self, question_service, ocr_service):
        self.question_service = question_service
        self.ocr_service = ocr_service
    
    def on_image_selected(self, image_path: str):
        # 触发OCR识别
        pass
    
    def on_ocr_completed(self, text: str):
        # 填充到表单
        pass
    
    def save_question(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        # 调用服务层保存
        pass
```

#### 2.2 详情对话框重构
**当前**: `detail_dialog.py` (400+行)
**目标**: 拆分为模块化结构

#### 2.3 复习对话框重构
**当前**: `review_dialog_new.py`
**目标**: 拆分为模块化结构

---

### 阶段3: 重构主窗口（2-3天）
**目标**: 将主窗口拆分为更小的模块

#### 3.1 主窗口重构
**当前**: `main_window.py` (600+行)
**目标**: 拆分为多个文件

**新结构**:
```
ui/main_window/
├── __init__.py
├── window.py           # 主窗口（150行）
├── controller.py       # 业务逻辑（200行）
├── panels.py          # 面板创建器（150行）
└── README.md
```

**window.py 职责**:
- 创建工具栏
- 创建菜单栏
- 组装面板
- 处理窗口事件

**controller.py 职责**:
- 处理业务逻辑
- 调用服务层
- 管理视图状态

**panels.py 职责**:
- 创建左侧导航面板
- 创建中间卡片面板
- 创建右侧筛选面板

---

### 阶段4: 引入工厂模式（1天）
**目标**: 使用工厂模式创建对话框和组件

#### 4.1 对话框工厂
**位置**: `ui/factories/dialog_factory.py`

```python
class DialogFactory:
    def __init__(self, services):
        self.question_service = services.question_service
        self.review_service = services.review_service
        self.ocr_service = services.ocr_service
    
    def create_add_question_dialog(self, parent=None):
        controller = AddQuestionController(
            self.question_service,
            self.ocr_service
        )
        return AddQuestionDialog(controller, parent)
    
    def create_detail_dialog(self, question_data, parent=None):
        controller = DetailDialogController(
            self.question_service,
            question_data
        )
        return DetailDialog(controller, parent)
    
    def create_review_dialog(self, questions, parent=None):
        controller = ReviewDialogController(
            self.review_service,
            questions
        )
        return ReviewDialog(controller, parent)
```

#### 4.2 组件工厂
**位置**: `ui/factories/component_factory.py`

```python
class ComponentFactory:
    @staticmethod
    def create_image_uploader(parent=None):
        return ImageUploader(parent)
    
    @staticmethod
    def create_ocr_panel(ocr_service, parent=None):
        return OCRPanel(ocr_service, parent)
    
    @staticmethod
    def create_question_form(parent=None):
        return QuestionForm(parent)
```

---

### 阶段5: 引入事件总线（1天）
**目标**: 使用事件总线解耦组件通信

#### 5.1 事件定义
**位置**: `ui/events/events.py`

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
```

#### 5.2 事件总线
**位置**: `ui/events/event_bus.py`

```python
from typing import Callable, Dict, List
from .events import Event

class EventBus:
    """事件总线 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: Dict[type, List[Callable]] = {}
        return cls._instance
    
    def subscribe(self, event_type: type, handler: Callable):
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: type, handler: Callable):
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """发布事件"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

#### 5.3 使用示例
```python
# 在主窗口中订阅事件
event_bus = EventBus()
event_bus.subscribe(QuestionAddedEvent, self.on_question_added)
event_bus.subscribe(QuestionUpdatedEvent, self.on_question_updated)

# 在对话框中发布事件
event_bus = EventBus()
event_bus.publish(QuestionAddedEvent(
    question_id=123,
    question_data=data
))
```

---

## 📊 重构优先级

### P0 - 必须完成（核心重构）
1. ✅ 提取图片上传组件
2. ✅ 提取OCR面板组件
3. ✅ 提取题目表单组件
4. ✅ 重构添加错题对话框
5. ✅ 引入对话框工厂

### P1 - 应该完成（重要改进）
6. ✅ 提取筛选面板组件
7. ✅ 提取统计面板组件
8. ✅ 重构主窗口
9. ✅ 引入事件总线

### P2 - 可以完成（锦上添花）
10. ⭕ 重构详情对话框
11. ⭕ 重构复习对话框
12. ⭕ 添加UI组件单元测试
13. ⭕ 添加组件使用文档

---

## 🧪 测试策略

### 组件测试
```python
# tests/ui/components/test_image_uploader.py
def test_image_uploader_select_image():
    uploader = ImageUploader()
    # 模拟选择图片
    # 验证信号发出
    pass

def test_image_uploader_drag_drop():
    uploader = ImageUploader()
    # 模拟拖拽
    # 验证图片加载
    pass
```

### 对话框测试
```python
# tests/ui/dialogs/test_add_question_dialog.py
def test_add_question_dialog_save():
    # Mock服务层
    mock_service = Mock()
    controller = AddQuestionController(mock_service, None)
    
    # 测试保存逻辑
    result = controller.save_question(test_data)
    assert result[0] is True
```

---

## 📝 迁移计划

### 向后兼容
- 保留旧的对话框类作为别名
- 逐步迁移调用代码
- 标记旧代码为 `@deprecated`

### 迁移步骤
1. 创建新组件和对话框
2. 在新代码中使用新组件
3. 逐步迁移旧代码
4. 删除旧代码（在确认无问题后）

---

## 📈 成功指标

### 代码质量
- [ ] 单个文件不超过300行
- [ ] 单个方法不超过30行
- [ ] 代码重复率 < 5%

### 可维护性
- [ ] 新增功能开发时间减少30%
- [ ] Bug修复时间减少40%
- [ ] 代码审查时间减少50%

### 测试覆盖
- [ ] UI组件测试覆盖率 > 60%
- [ ] 对话框控制器测试覆盖率 > 80%

---

## 🚀 实施时间表

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|----------|--------|
| 1 | 提取可复用组件 | 2天 | TBD |
| 2 | 重构对话框 | 3天 | TBD |
| 3 | 重构主窗口 | 3天 | TBD |
| 4 | 引入工厂模式 | 1天 | TBD |
| 5 | 引入事件总线 | 1天 | TBD |
| 6 | 测试和文档 | 2天 | TBD |
| **总计** | | **12天** | |

---

## 📚 参考资料

### 设计模式
- [工厂模式](https://refactoring.guru/design-patterns/factory-method)
- [观察者模式](https://refactoring.guru/design-patterns/observer)
- [MVC/MVVM模式](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)

### PyQt最佳实践
- [Qt Model/View Programming](https://doc.qt.io/qt-6/model-view-programming.html)
- [Signals and Slots](https://doc.qt.io/qt-6/signalsandslots.html)

---

**文档版本**: 1.0  
**创建日期**: 2026-02-04  
**最后更新**: 2026-02-04  
**状态**: 待审核
