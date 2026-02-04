# 复习模块选择器修复

## 问题描述
点击"开始复习"按钮后没有反应，对话框不关闭，也没有显示复习提示。

## 问题原因
在`ReviewModuleSelectorDialog.on_start_review()`方法中：
1. 发出了`module_selected`信号
2. 但是没有调用`self.accept()`关闭对话框
3. 导致对话框一直打开，信号虽然发出但主窗口无法继续执行

## 解决方案

### 修改前
```python
def on_start_review(self):
    """开始复习选定的模块"""
    if not self.selected_subject or not self.selected_question_type:
        QMessageBox.warning(self, "提示", "请先选择科目和题型")
        return
    
    # 发出信号
    self.module_selected.emit(self.selected_subject, self.selected_question_type)
    # 缺少 self.accept()
```

### 修改后
```python
def on_start_review(self):
    """开始复习选定的模块"""
    if not self.selected_subject or not self.selected_question_type:
        QMessageBox.warning(self, "提示", "请先选择科目和题型")
        return
    
    print(f"发出信号：{self.selected_subject}, {self.selected_question_type}")  # 调试信息
    
    # 发出信号
    self.module_selected.emit(self.selected_subject, self.selected_question_type)
    
    # 关闭对话框
    self.accept()  # ← 添加这一行
```

## 其他优化

### 主窗口调试信息
在`main_window.py`的`on_module_selected_for_review()`方法中添加了日志：
```python
logger.info(f"选择的模块：科目={subject}, 题型={question_type}")
logger.info(f"筛选条件：{filters}")
logger.info(f"找到 {len(all_questions)} 道题目")
```

### 临时使用所有题目
暂时不考虑"到期时间"，直接获取所有符合条件的题目：
```python
# 获取待复习题目（暂时获取所有题目，不考虑到期时间）
all_questions = self.data_manager.search_questions(filters)
```

这样可以确保有题目可以复习，方便测试功能。

## 测试步骤

1. 点击工具栏"开始复习"按钮
2. 在模块选择对话框中选择科目
3. 选择题型
4. 点击"开始复习"按钮
5. 对话框应该关闭
6. 显示提示信息框："准备复习：xxx - xxx，共 n 道题目"

## 预期行为

### 正常流程
```
用户点击"开始复习"
    ↓
显示模块选择对话框
    ↓
用户选择科目和题型
    ↓
用户点击"开始复习"
    ↓
发出module_selected信号
    ↓
对话框关闭（accept）
    ↓
主窗口接收信号
    ↓
显示复习提示信息
```

### 异常处理
1. 如果没有选择科目和题型，显示警告
2. 如果选择的模块没有题目，显示提示
3. 如果用户点击"取消"，对话框关闭但不执行复习

## 修改文件
- `src/mistake_book/ui/dialogs/review_module_selector.py`
  - `on_start_review()` - 添加`self.accept()`
  - 添加调试打印信息

- `src/mistake_book/ui/main_window.py`
  - `on_module_selected_for_review()` - 添加日志
  - 暂时使用所有题目而非到期题目

## 后续工作
1. 实现新的复习对话框
2. 恢复使用到期题目筛选
3. 移除调试打印信息
4. 完善错误处理

## 总结
问题的根本原因是忘记调用`self.accept()`关闭对话框。PyQt的对话框需要显式调用`accept()`或`reject()`来关闭，否则会一直保持打开状态。虽然信号已经发出，但由于对话框没有关闭，用户体验很差，看起来像是"没有反应"。
