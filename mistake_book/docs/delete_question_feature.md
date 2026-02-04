# 删除错题功能实现文档

## 📋 功能概述

删除错题功能允许用户从错题本中永久删除不需要的错题。该功能遵循项目的分层架构，通过服务层封装业务逻辑，UI层只负责用户交互和展示。

## 🏗️ 架构设计

### 分层结构

```
UI Layer (QuestionCard)
    ↓ delete_requested 信号
UI Layer (MainWindow)
    ↓ 确认对话框
Service Layer (QuestionService)
    ↓ delete_question()
Core Layer (DataManager)
    ↓ delete_question()
Database Layer (db_manager)
    ↓ 数据库删除操作
```

### 数据流向

1. **用户操作**: 用户点击错题卡片上的"🗑️ 删除"按钮
2. **信号发射**: QuestionCard 发射 `delete_requested` 信号
3. **确认对话框**: MainWindow 显示确认对话框，防止误删
4. **服务调用**: 用户确认后，调用 `QuestionService.delete_question()`
5. **业务处理**: QuestionService 调用 `DataManager.delete_question()`
6. **数据删除**: DataManager 通过数据库管理器删除记录
7. **UI更新**: 删除成功后刷新错题列表

## 📁 涉及文件

### 1. 服务层 - `src/mistake_book/services/question_service.py`

**方法**: `delete_question(question_id: int) -> tuple[bool, str]`

```python
def delete_question(self, question_id: int) -> tuple[bool, str]:
    """
    删除错题
    
    Args:
        question_id: 题目ID
    
    Returns:
        (成功标志, 消息)
    """
    try:
        success = self.data_manager.delete_question(question_id)
        if success:
            return True, "删除成功"
        else:
            return False, "题目不存在"
    except Exception as e:
        return False, f"删除失败: {str(e)}"
```

**职责**:
- 调用 DataManager 执行删除操作
- 统一异常处理
- 返回标准化的结果格式

### 2. UI组件 - `src/mistake_book/ui/widgets/question_card.py`

**新增信号**: `delete_requested = pyqtSignal(dict)`

**新增按钮**: 删除按钮

```python
# 删除按钮
delete_btn = QPushButton("🗑️ 删除")
delete_btn.setFixedSize(70, 30)
delete_btn.setStyleSheet("""
    QPushButton {
        background-color: #e74c3c;  # 红色，表示危险操作
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 9pt;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #c0392b;
    }
    QPushButton:pressed {
        background-color: #a93226;
    }
""")
delete_btn.clicked.connect(self.on_delete_clicked)
```

**新增方法**: `on_delete_clicked()`

```python
def on_delete_clicked(self):
    """删除按钮点击事件"""
    self.delete_requested.emit(self.question_data)
```

**职责**:
- 提供删除按钮UI
- 发射删除请求信号
- 不包含业务逻辑

### 3. 主窗口 - `src/mistake_book/ui/main_window.py`

**信号连接**: 在 `display_questions()` 方法中

```python
card.delete_requested.connect(lambda q=question: self.on_delete_question(q))
```

**新增方法**: `on_delete_question(question)`

```python
def on_delete_question(self, question):
    """删除错题事件"""
    from PyQt6.QtWidgets import QMessageBox
    
    # 确认对话框
    reply = QMessageBox.question(
        self,
        "确认删除",
        f"确定要删除这道错题吗？\n\n科目：{question.get('subject', '')}\n题型：{question.get('question_type', '')}\n\n此操作不可恢复！",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        # 调用服务删除
        success, message = self.question_service.delete_question(question['id'])
        
        if success:
            # 删除成功，刷新列表
            self.load_questions()
            self.statusBar().showMessage("错题已删除", 3000)
        else:
            # 显示错误
            QMessageBox.warning(self, "删除失败", message)
```

**职责**:
- 显示确认对话框（防止误删）
- 调用 QuestionService 执行删除
- 处理删除结果（刷新列表或显示错误）
- 更新状态栏提示

## 🎨 UI设计

### 删除按钮样式

- **颜色**: 红色 (#e74c3c)，表示危险操作
- **图标**: 🗑️ 垃圾桶表情符号
- **位置**: 错题卡片右侧操作区，"查看"按钮下方
- **尺寸**: 70x30 像素
- **交互**: 悬停变深红色，点击更深

### 确认对话框

- **标题**: "确认删除"
- **内容**: 显示要删除的错题基本信息（科目、题型）
- **警告**: "此操作不可恢复！"
- **按钮**: "是" 和 "否"，默认选中"否"

### 用户反馈

- **成功**: 状态栏显示"错题已删除"（3秒）
- **失败**: 弹出警告对话框显示错误信息
- **刷新**: 删除成功后自动刷新错题列表

## 🔒 安全考虑

### 1. 二次确认

使用 `QMessageBox.question()` 显示确认对话框，防止用户误操作。

### 2. 默认选项

确认对话框默认选中"否"，需要用户主动点击"是"才能删除。

### 3. 明确提示

对话框中明确提示"此操作不可恢复"，让用户了解操作的严重性。

### 4. 异常处理

服务层捕获所有异常，确保删除失败时不会导致程序崩溃。

### 5. 事务保护

DataManager 使用数据库事务，确保删除操作的原子性。

## 🔄 完整流程示例

### 正常删除流程

```
1. 用户点击"🗑️ 删除"按钮
   ↓
2. QuestionCard 发射 delete_requested 信号
   ↓
3. MainWindow 接收信号，显示确认对话框
   ↓
4. 用户点击"是"确认删除
   ↓
5. MainWindow 调用 question_service.delete_question(id)
   ↓
6. QuestionService 调用 data_manager.delete_question(id)
   ↓
7. DataManager 执行数据库删除操作
   ↓
8. 返回成功结果
   ↓
9. MainWindow 刷新错题列表
   ↓
10. 状态栏显示"错题已删除"
```

### 取消删除流程

```
1. 用户点击"🗑️ 删除"按钮
   ↓
2. QuestionCard 发射 delete_requested 信号
   ↓
3. MainWindow 接收信号，显示确认对话框
   ↓
4. 用户点击"否"取消删除
   ↓
5. 对话框关闭，不执行任何操作
```

### 删除失败流程

```
1-6. (同正常流程)
   ↓
7. DataManager 执行删除时发生异常
   ↓
8. QuestionService 捕获异常，返回失败结果
   ↓
9. MainWindow 显示错误对话框
   ↓
10. 用户点击"确定"关闭对话框
```

## 🧪 测试要点

### 功能测试

1. ✅ 点击删除按钮能正常显示确认对话框
2. ✅ 确认对话框显示正确的错题信息
3. ✅ 点击"是"能成功删除错题
4. ✅ 点击"否"能取消删除操作
5. ✅ 删除成功后列表自动刷新
6. ✅ 删除成功后状态栏显示提示
7. ✅ 删除不存在的题目显示错误提示

### UI测试

1. ✅ 删除按钮样式正确（红色）
2. ✅ 删除按钮位置合理（查看按钮下方）
3. ✅ 悬停效果正常
4. ✅ 确认对话框布局清晰
5. ✅ 错误提示对话框显示正常

### 异常测试

1. ✅ 数据库连接失败时的错误处理
2. ✅ 删除操作异常时的错误处理
3. ✅ 并发删除的处理

## 📊 数据库影响

### 删除操作

```sql
DELETE FROM questions WHERE id = ?
```

### 级联删除

根据数据库设计，删除错题时应该：
- 删除关联的标签关系（question_tags表）
- 删除关联的复习记录（review_records表）

这些通过外键的 `ON DELETE CASCADE` 自动处理。

## 🎯 最佳实践

### 1. 分层清晰

- UI层只负责展示和用户交互
- 业务逻辑封装在Service层
- 数据操作封装在DataManager层

### 2. 信号驱动

使用Qt信号机制实现组件间通信，降低耦合度。

### 3. 用户友好

- 提供二次确认，防止误删
- 明确的操作反馈
- 清晰的错误提示

### 4. 异常安全

- 所有异常在Service层统一处理
- 返回标准化的结果格式
- 确保UI不会因异常崩溃

### 5. 依赖注入

通过构造函数注入服务依赖，便于测试和维护。

## 🔮 未来扩展

### 1. 软删除

可以考虑实现软删除（标记为已删除而不是物理删除），支持恢复功能。

### 2. 批量删除

支持选中多个错题进行批量删除。

### 3. 删除历史

记录删除操作的历史，便于审计和恢复。

### 4. 回收站

实现回收站功能，删除的错题先进入回收站，一段时间后才真正删除。

### 5. 权限控制

如果支持多用户，需要添加权限检查，确保用户只能删除自己的错题。

## 📝 总结

删除错题功能严格遵循项目的分层架构：

- **UI层**: 提供删除按钮和确认对话框
- **Service层**: 封装删除业务逻辑和异常处理
- **Core层**: 执行数据删除操作
- **Database层**: 处理数据库事务

通过信号机制实现组件解耦，通过确认对话框保证操作安全，通过异常处理确保系统稳定。整个实现简洁、清晰、易于维护。
