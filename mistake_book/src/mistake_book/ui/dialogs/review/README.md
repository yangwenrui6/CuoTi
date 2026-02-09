# 复习对话框模块

## 概述

复习对话框模块采用 Dialog-Controller 分离模式，将UI展示和业务逻辑分离。

## 架构

```
review/
├── __init__.py          # 模块导出
├── controller.py        # 业务逻辑控制器
├── dialog.py           # UI对话框
└── README.md           # 本文档
```

## ReviewDialog

### 职责

- 组装UI组件（进度显示、题目内容、答案区域、评分按钮）
- 处理用户交互（显示答案、选择掌握度）
- 连接信号到Controller方法
- 显示复习总结

### 接口

#### `__init__(controller, parent=None)`

初始化对话框。

**参数**:
- `controller`: ReviewDialogController实例
- `parent`: 父窗口（可选）

### 信号

#### `review_completed`

当用户在总结页面点击"继续复习"时发出，通知主窗口返回模块选择器。

### 主要方法

#### `_load_question()`

加载当前题目，显示题目信息、图片、内容。

#### `_toggle_answer()`

切换答案显示状态。显示答案后，隐藏"显示答案"按钮，显示掌握度评分按钮。

#### `_on_quality_selected(result: ReviewResult)`

处理用户选择的掌握度评分，调用Controller提交复习结果。

#### `_show_summary()`

显示复习总结页面，包含统计信息和操作按钮。

### UI组件

- **进度栏**: 显示当前题号和总题数
- **题目信息卡片**: 显示科目、题型、难度
- **题目图片**: 如果有图片则显示
- **题目内容**: 显示题目文本
- **答案区域**: 显示我的答案、正确答案、解析（初始隐藏）
- **显示答案按钮**: 点击显示答案区域
- **掌握度按钮**: 四个评分按钮（生疏、困难、掌握、熟练）
- **总结页面**: 显示复习统计和操作按钮

## ReviewDialogController

### 职责

- 管理复习进度（当前题目索引、已复习数量）
- 提供题目访问接口
- 处理复习结果提交
- 调用ReviewService更新题目状态
- 发布ReviewCompletedEvent事件

### 接口

#### `__init__(review_service, questions, event_bus=None)`

初始化控制器。

**参数**:
- `review_service`: ReviewService实例
- `questions`: 待复习题目列表 `List[Dict[str, Any]]`
- `event_bus`: 事件总线（可选）

#### `get_current_question() -> Optional[Dict[str, Any]]`

获取当前题目。

**返回**: 当前题目数据字典，如果没有更多题目则返回None

#### `submit_review(quality: int) -> bool`

提交复习结果。

**参数**:
- `quality`: 质量评分 (0-5)，对应ReviewResult枚举值
  - 0: AGAIN (生疏)
  - 1: HARD (困难)
  - 2: GOOD (掌握)
  - 3: EASY (熟练)

**返回**: 是否还有下一题

**副作用**:
- 调用ReviewService更新题目状态
- 增加reviewed_count计数
- 移动到下一题
- 如果是最后一题，发布ReviewCompletedEvent

#### `get_progress() -> Tuple[int, int]`

获取复习进度。

**返回**: (当前题号, 总题数)，题号从1开始

#### `get_reviewed_count() -> int`

获取已复习题目数量。

**返回**: 已复习的题目数量

#### `has_more_questions() -> bool`

检查是否还有更多题目。

**返回**: 是否还有未复习的题目

#### `reset()`

重置控制器状态（用于重新开始复习）。

## 使用示例

### 基本使用

```python
from mistake_book.ui.dialogs.review import ReviewDialog, ReviewDialogController
from mistake_book.ui.events.event_bus import EventBus

# 创建控制器
controller = ReviewDialogController(
    review_service=review_service,
    questions=questions,
    event_bus=EventBus()
)

# 创建对话框
dialog = ReviewDialog(controller)

# 连接信号
dialog.review_completed.connect(on_review_completed)

# 显示对话框
dialog.exec()
```

### 使用工厂创建

```python
# 在DialogFactory中
def create_review_dialog(self, questions, parent=None):
    controller = ReviewDialogController(
        self.review_service,
        questions,
        self.event_bus
    )
    return ReviewDialog(controller, parent)
```

## 事件

### ReviewCompletedEvent

当所有题目复习完成时发布。

**字段**:
- `reviewed_count`: 已复习题目数量

**订阅示例**:
```python
def on_review_completed(event):
    print(f"复习完成，共复习 {event.reviewed_count} 道题目")
    # 刷新主窗口统计数据
    self.refresh_statistics()

event_bus.subscribe(ReviewCompletedEvent, on_review_completed)
```

## 测试

### Controller单元测试

位置: `tests/test_ui/dialogs/test_review_controller.py`

测试内容:
- 控制器初始化
- 获取当前题目
- 提交复习结果
- 进度跟踪
- 事件发布
- 边界情况处理

### Dialog集成测试

位置: `tests/test_ui/dialogs/test_review_dialog_integration.py`

测试内容:
- 对话框初始化
- 题目显示
- 答案切换
- 掌握度评分
- 进度显示
- 总结页面
- 信号发送
- Controller集成

## 设计原则

1. **单一职责**: Dialog只处理UI组装，Controller只处理业务逻辑
2. **依赖注入**: 通过构造函数注入Controller，便于测试
3. **事件驱动**: 使用EventBus发布事件，解耦组件通信
4. **可测试性**: Dialog和Controller都可以独立测试

## 代码质量

- **Dialog文件**: ~450行（符合<500行的要求）
- **Controller文件**: ~120行（符合<200行的要求）
- **方法行数**: 所有方法<30行
- **测试覆盖**: Controller 100%, Dialog集成测试覆盖主要流程

## 相关文档

- [UI层重构设计文档](../../../../.kiro/specs/ui-refactoring/design.md)
- [ReviewService文档](../../../services/review_service.py)
- [EventBus文档](../../events/event_bus.py)
