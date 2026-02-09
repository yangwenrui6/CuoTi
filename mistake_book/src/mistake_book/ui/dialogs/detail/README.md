# 详情对话框模块

## 概述

详情对话框模块采用 Dialog-Controller 分离模式，将UI展示和业务逻辑分离。

## 架构

```
detail/
├── __init__.py          # 模块导出
├── controller.py        # 业务逻辑控制器
└── README.md           # 本文档
```

## DetailDialogController

### 职责

- 管理题目数据状态
- 检测数据变化
- 保存修改到服务层
- 发布QuestionUpdatedEvent事件

### 使用示例

```python
from mistake_book.ui.dialogs.detail import DetailDialogController
from mistake_book.ui.events.event_bus import EventBus

# 创建控制器
controller = DetailDialogController(
    question_service=question_service,
    question_data=question_data,
    event_bus=EventBus()
)

# 检查是否有修改
current_data = {
    'content': '题目内容',
    'my_answer': '我的答案',
    'answer': '正确答案',
    'explanation': '解析'
}
has_changes = controller.has_changes(current_data)

# 保存修改
if has_changes:
    success, message = controller.save_changes(current_data)
```

## 设计原则

1. **单一职责**: Controller只处理业务逻辑，不包含UI代码
2. **依赖注入**: 通过构造函数注入服务和事件总线
3. **事件驱动**: 通过EventBus发布更新事件，解耦组件通信
