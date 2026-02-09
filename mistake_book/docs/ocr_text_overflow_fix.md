# OCR文本溢出修复

## 问题描述
在添加错题对话框中，当OCR识别的文本内容较长时，题目内容文本框会溢出，导致显示不正常。

## 问题原因
1. `QuestionForm` 组件中的 `_content_edit` QTextEdit 只设置了最小高度（100px），没有设置最大高度限制
2. 没有启用自动换行功能
3. `AddQuestionDialog` 对话框没有滚动功能，当内容过多时无法查看

## 解决方案

### 1. 修复 QuestionForm 组件
**文件**: `src/mistake_book/ui/components/question_form.py`

为题目内容文本框添加：
- `setMaximumHeight(200)`: 限制最大高度为200px
- `setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)`: 启用自动换行

```python
# 题目内容
layout.addWidget(QLabel("题目内容:"))
self._content_edit = QTextEdit()
self._content_edit.setPlaceholderText("输入题目内容...")
self._content_edit.setMinimumHeight(100)
self._content_edit.setMaximumHeight(200)  # 新增：限制最大高度
self._content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # 新增：自动换行
layout.addWidget(self._content_edit)
```

### 2. 为 AddQuestionDialog 添加滚动功能
**文件**: `src/mistake_book/ui/dialogs/add_question/dialog.py`

添加 `QScrollArea` 包裹对话框内容：
- 图片上传区域和表单区域放在滚动区域内
- 底部按钮固定在对话框底部，不随内容滚动
- 禁用水平滚动条，只保留垂直滚动

```python
def _init_ui(self):
    """初始化UI布局"""
    main_layout = QVBoxLayout(self)
    
    # 创建滚动区域
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    # 滚动区域内容容器
    scroll_content = QWidget()
    content_layout = QVBoxLayout(scroll_content)
    
    # ... 添加图片上传区域和表单区域到 content_layout
    
    # 设置滚动区域内容
    scroll_area.setWidget(scroll_content)
    main_layout.addWidget(scroll_area)
    
    # 按钮（固定在底部，不滚动）
    self._add_buttons(main_layout)
```

## 效果
- ✅ 题目内容文本框高度限制在100-200px之间
- ✅ 长文本自动换行，不会横向溢出
- ✅ 文本框内容超出时显示垂直滚动条
- ✅ 对话框整体内容过多时可以滚动查看
- ✅ 底部保存/取消按钮始终可见

## 测试
1. 启动应用程序：`python run.py`
2. 点击"添加错题"按钮
3. 上传图片并触发OCR识别
4. 验证识别的文本正确显示在题目内容框中
5. 验证长文本自动换行且不溢出
6. 验证对话框可以正常滚动

## 相关文件
- `src/mistake_book/ui/components/question_form.py`
- `src/mistake_book/ui/dialogs/add_question/dialog.py`

## 日期
2026-02-09
