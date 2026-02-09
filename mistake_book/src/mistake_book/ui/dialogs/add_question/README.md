# 添加错题对话框模块

本模块实现了添加错题的对话框，采用Dialog-Controller分离模式。

## 文件结构

```
add_question/
├── __init__.py          # 模块导出
├── controller.py        # 业务逻辑控制器
├── dialog.py            # UI组装器
└── README.md           # 本文档
```

## 架构设计

### Dialog-Controller模式

```
┌─────────────────────────────────────────┐
│         AddQuestionDialog               │
│         (UI组装器)                       │
│  ┌────────────┐  ┌────────────┐        │
│  │ImageUploader│  │ OCRPanel   │        │
│  └────────────┘  └────────────┘        │
│  ┌────────────────────────────┐        │
│  │     QuestionForm           │        │
│  └────────────────────────────┘        │
└─────────────────────────────────────────┘
              │ 信号连接
              ↓
┌─────────────────────────────────────────┐
│      AddQuestionController              │
│      (业务逻辑)                          │
│  • on_image_selected()                  │
│  • on_ocr_completed()                   │
│  • save_question()                      │
└─────────────────────────────────────────┘
              │ 调用
              ↓
┌─────────────────────────────────────────┐
│       QuestionService                   │
│       (服务层)                           │
└─────────────────────────────────────────┘
```

## 使用方法

### 基本使用

```python
from mistake_book.ui.dialogs.add_question import (
    AddQuestionController, 
    AddQuestionDialog
)

# 创建控制器
controller = AddQuestionController(
    question_service=question_service,
    event_bus=event_bus  # 可选
)

# 创建对话框
dialog = AddQuestionDialog(controller, parent=main_window)

# 显示对话框
if dialog.exec():
    print("题目添加成功")
else:
    print("用户取消")
```

### 使用工厂模式（推荐）

```python
from mistake_book.ui.factories import DialogFactory

# 创建工厂
factory = DialogFactory(services, event_bus)

# 创建对话框
dialog = factory.create_add_question_dialog(parent=main_window)
dialog.exec()
```

## Controller API

### AddQuestionController

**构造函数**:
```python
def __init__(self, question_service, event_bus=None)
```

**方法**:

#### on_image_selected(image_path: str)
处理图片选择事件

**参数**:
- `image_path`: 图片路径

**返回**: None

---

#### on_ocr_completed(text: str) -> str
处理OCR识别完成事件

**参数**:
- `text`: 识别的文本

**返回**: 处理后的文本

---

#### save_question(data: Dict[str, Any]) -> Tuple[bool, str]
保存错题

**参数**:
- `data`: 题目数据字典，包含：
  - `subject`: 科目
  - `question_type`: 题型
  - `content`: 题目内容
  - `my_answer`: 我的答案
  - `answer`: 正确答案
  - `explanation`: 解析
  - `difficulty`: 难度 (1-5)
  - `image_path`: 图片路径（可选）

**返回**: `(成功标志, 消息)`

**示例**:
```python
data = {
    'subject': '数学',
    'question_type': '单选题',
    'content': '1+1=?',
    'my_answer': '3',
    'answer': '2',
    'explanation': '基础加法',
    'difficulty': 1,
    'image_path': '/path/to/image.jpg'
}

success, message = controller.save_question(data)
if success:
    print("保存成功")
else:
    print(f"保存失败: {message}")
```

## Dialog API

### AddQuestionDialog

**构造函数**:
```python
def __init__(self, controller, parent=None)
```

**组件**:
- `image_uploader`: ImageUploader实例
- `ocr_panel`: OCRPanel实例
- `question_form`: QuestionForm实例

**方法**:
- `exec()`: 显示对话框（继承自QDialog）
- `accept()`: 接受对话框（保存成功时调用）
- `reject()`: 拒绝对话框（取消时调用）

## 信号流程

### 完整的添加流程

1. **用户拖拽/选择图片**
   ```
   ImageUploader.image_selected(path)
   → Dialog._on_image_selected(path)
   → Controller.on_image_selected(path)
   → OCRPanel.recognize_image(path)
   ```

2. **OCR识别**
   ```
   OCRPanel.recognition_started()
   → OCRWorker.run() (后台线程)
   → OCRPanel.recognition_completed(text)
   → Dialog._on_ocr_completed(text)
   → Controller.on_ocr_completed(text)
   → QuestionForm.set_content(text)
   ```

3. **用户填写表单并保存**
   ```
   用户点击保存按钮
   → Dialog._on_save_clicked()
   → QuestionForm.validate()
   → QuestionForm.get_data()
   → Controller.save_question(data)
   → QuestionService.create_question(data)
   → EventBus.publish(QuestionAddedEvent) (可选)
   → Dialog.accept()
   ```

## 代码质量

### 行数统计
- `controller.py`: ~80行
- `dialog.py`: ~180行
- **总计**: ~260行（原始600+行，减少56%）

### 职责分离
- ✅ Dialog只负责UI组装
- ✅ Controller只负责业务逻辑
- ✅ 组件通过信号通信

### 可测试性
- ✅ Controller可使用mock服务测试
- ✅ Dialog可独立实例化
- ✅ 组件可单独测试

## 测试示例

### 测试Controller

```python
from unittest.mock import Mock
from mistake_book.ui.dialogs.add_question import AddQuestionController

def test_save_question():
    # Mock服务
    mock_service = Mock()
    mock_service.create_question.return_value = (True, "成功", 123)
    
    # 创建控制器
    controller = AddQuestionController(mock_service)
    
    # 测试保存
    data = {'content': '测试题目', 'answer': '测试答案'}
    success, message = controller.save_question(data)
    
    assert success is True
    mock_service.create_question.assert_called_once_with(data)
```

### 测试Dialog

```python
from PyQt6.QtWidgets import QApplication
from mistake_book.ui.dialogs.add_question import (
    AddQuestionController, 
    AddQuestionDialog
)

app = QApplication([])

# Mock控制器
mock_controller = Mock()
mock_controller.question_service = Mock()

# 创建对话框
dialog = AddQuestionDialog(mock_controller)

# 验证组件已创建
assert dialog.image_uploader is not None
assert dialog.ocr_panel is not None
assert dialog.question_form is not None
```

## 迁移指南

### 从旧版本迁移

**旧代码**:
```python
from mistake_book.ui.dialogs.add_dialog import AddQuestionDialog

dialog = AddQuestionDialog(question_service, parent)
dialog.exec()
```

**新代码**:
```python
from mistake_book.ui.dialogs.add_question import (
    AddQuestionController,
    AddQuestionDialog
)

controller = AddQuestionController(question_service)
dialog = AddQuestionDialog(controller, parent)
dialog.exec()
```

**或使用工厂**:
```python
from mistake_book.ui.factories import DialogFactory

factory = DialogFactory(services, event_bus)
dialog = factory.create_add_question_dialog(parent)
dialog.exec()
```

---

**文档版本**: 1.0  
**创建时间**: 2026-02-06
