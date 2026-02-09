# 主窗口模块

## 概述

主窗口模块采用 Controller 模式，将业务逻辑与 UI 代码分离。

## 文件结构

```
main_window/
├── __init__.py          # 模块导出
├── controller.py        # 业务逻辑控制器
└── README.md           # 本文档
```

## MainWindowController

### 职责

- 管理视图状态（当前视图类型、筛选条件）
- 处理题目加载、搜索、筛选逻辑
- 调用服务层获取数据
- 订阅和处理事件总线事件
- 提供对话框显示接口

### 视图状态管理

Controller 维护以下状态：

- `current_view_type`: 当前视图类型
  - `"all"`: 显示所有题目
  - `"search"`: 搜索结果
  - `"nav_filter"`: 导航树筛选
  - `"filter"`: 右侧筛选面板筛选

- `current_filters`: 当前筛选条件
- `current_questions`: 当前显示的题目列表

### 主要方法

#### 数据加载

```python
# 加载所有题目
questions = controller.load_questions()

# 搜索题目
questions = controller.on_search("关键词")

# 导航筛选
questions = controller.on_nav_filter_changed({
    'type': 'subject',
    'value': '数学'
})

# 右侧筛选
questions = controller.on_filter_changed({
    'subject': '数学',
    'difficulty': 3,
    'mastery_level': 1
})

# 刷新当前视图（保持筛选状态）
questions = controller.refresh_current_view()
```

#### 对话框操作

```python
# 显示添加错题对话框
controller.show_add_dialog(parent)

# 开始复习（显示模块选择器）
controller.start_review(parent)
```

#### 题目操作

```python
# 删除题目
success, message = controller.delete_question(question_id)
```

### 事件订阅

Controller 自动订阅以下事件：

- `QuestionAddedEvent`: 题目添加后刷新视图
- `QuestionUpdatedEvent`: 题目更新后刷新视图
- `QuestionDeletedEvent`: 题目删除后刷新视图

### 使用示例

```python
from mistake_book.ui.main_window import MainWindowController
from mistake_book.ui.events.event_bus import EventBus
from mistake_book.ui.factories.dialog_factory import DialogFactory

# 创建服务字典
services = {
    'question_service': question_service,
    'review_service': review_service,
    'ui_service': ui_service
}

# 创建事件总线和工厂
event_bus = EventBus()
dialog_factory = DialogFactory(services, event_bus)

# 创建控制器
controller = MainWindowController(services, dialog_factory, event_bus)

# 加载题目
questions = controller.load_questions()

# 搜索
questions = controller.on_search("数学")

# 刷新视图
questions = controller.refresh_current_view()
```

## 设计原则

### 单一职责

Controller 只负责业务逻辑，不包含 UI 代码：
- ✅ 调用服务层获取数据
- ✅ 管理视图状态
- ✅ 处理事件
- ❌ 不创建 UI 组件
- ❌ 不处理布局

### 依赖注入

所有依赖通过构造函数注入：
- 服务层（question_service, review_service, ui_service）
- 对话框工厂（dialog_factory）
- 事件总线（event_bus）

### 可测试性

Controller 可以独立测试：
- 使用 mock 服务
- 使用 mock 事件总线
- 不依赖 UI 组件

## 测试

参见 `tests/test_ui/main_window/test_controller.py`

## 相关文档

- [UI 层重构设计文档](../../../../.kiro/specs/ui-refactoring/design.md)
- [事件总线文档](../events/README.md)
- [对话框工厂文档](../factories/README.md)
