# UI可复用组件

本目录包含可在多个对话框中复用的UI组件。

## 组件列表

### 1. ImageUploader - 图片上传组件

**功能**: 支持拖拽和点击上传图片，提供预览功能

**使用示例**:
```python
from mistake_book.ui.components import ImageUploader

# 创建组件
uploader = ImageUploader()

# 连接信号
uploader.image_selected.connect(lambda path: print(f"选择了图片: {path}"))
uploader.image_cleared.connect(lambda: print("图片已清空"))

# 获取图片路径
image_path = uploader.get_image_path()

# 清空图片
uploader.clear()

# 设置提示文字
uploader.set_hint_text("自定义提示文字")
```

**信号**:
- `image_selected(str)`: 图片选择完成，参数为图片路径
- `image_cleared()`: 图片已清空

**方法**:
- `get_image_path() -> Optional[str]`: 获取当前图片路径
- `set_image(path: str) -> bool`: 设置图片（用于编辑场景）
- `clear()`: 清空图片
- `set_hint_text(text: str)`: 设置提示文字

---

### 2. OCRPanel - OCR识别面板

**功能**: 封装OCR识别功能的UI交互

**使用示例**:
```python
from mistake_book.ui.components import OCRPanel

# 创建组件（需要传入question_service）
ocr_panel = OCRPanel(question_service)

# 连接信号
ocr_panel.recognition_started.connect(lambda: print("开始识别"))
ocr_panel.recognition_completed.connect(lambda text: print(f"识别完成: {text}"))
ocr_panel.recognition_failed.connect(lambda msg: print(f"识别失败: {msg}"))

# 识别图片
ocr_panel.recognize_image("/path/to/image.jpg")

# 设置状态
ocr_panel.set_status("自定义状态")

# 检查是否正在识别
is_busy = ocr_panel.is_recognizing()
```

**信号**:
- `recognition_started()`: 开始识别
- `recognition_completed(str)`: 识别完成，参数为识别的文本
- `recognition_failed(str)`: 识别失败，参数为错误信息

**方法**:
- `recognize_image(image_path: str)`: 识别图片
- `set_status(status: str)`: 设置状态文本
- `is_recognizing() -> bool`: 是否正在识别

---

### 3. QuestionForm - 题目表单组件

**功能**: 封装题目信息的所有输入字段

**使用示例**:
```python
from mistake_book.ui.components import QuestionForm

# 创建组件
form = QuestionForm()

# 连接信号
form.data_changed.connect(lambda: print("数据已变化"))

# 获取表单数据
data = form.get_data()
# 返回: {
#     'subject': str,
#     'question_type': str,
#     'content': str,
#     'my_answer': str,
#     'answer': str,
#     'explanation': str,
#     'difficulty': int (1-5)
# }

# 设置表单数据（用于编辑）
form.set_data({
    'subject': '数学',
    'question_type': '单选题',
    'content': '题目内容',
    'answer': '正确答案',
    'difficulty': 3
})

# 验证表单
valid, error_msg = form.validate()
if not valid:
    print(f"验证失败: {error_msg}")

# 清空表单
form.clear()

# 设置题目内容（用于OCR识别后填充）
form.set_content("OCR识别的文本")

# 聚焦到题目内容输入框
form.focus_content()
```

**信号**:
- `data_changed()`: 表单数据变化

**方法**:
- `get_data() -> Dict[str, Any]`: 获取表单数据
- `set_data(data: Dict[str, Any])`: 设置表单数据
- `validate() -> Tuple[bool, str]`: 验证表单数据
- `clear()`: 清空表单
- `set_content(text: str)`: 设置题目内容
- `focus_content()`: 聚焦到题目内容输入框

---

## 设计原则

### 1. 单一职责
每个组件只负责一个功能模块，不超过200行代码。

### 2. 信号接口
组件通过信号暴露状态变化，便于集成和测试。

### 3. 可复用性
组件可以在多个对话框中使用，不依赖特定的父组件。

### 4. 依赖注入
需要服务的组件通过构造函数接收服务实例，便于测试。

---

## 完整示例：组合使用

```python
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGroupBox
from mistake_book.ui.components import ImageUploader, OCRPanel, QuestionForm

class MyDialog(QDialog):
    def __init__(self, question_service, parent=None):
        super().__init__(parent)
        
        # 创建组件
        self.image_uploader = ImageUploader()
        self.ocr_panel = OCRPanel(question_service)
        self.question_form = QuestionForm()
        
        # 连接信号
        self.image_uploader.image_selected.connect(
            self.ocr_panel.recognize_image
        )
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

---

**文档版本**: 1.0  
**创建时间**: 2026-02-06
