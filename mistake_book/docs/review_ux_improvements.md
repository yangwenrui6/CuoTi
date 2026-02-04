# 复习用户体验改进

## 改进内容

### 1. 复习完成后返回模块选择器
**需求**：用户希望复习完成后能够快速开始下一轮复习，而不是返回主页面。

#### 实现方案

##### 添加信号机制
在`ReviewDialog`中添加`review_completed`信号：
```python
class ReviewDialog(QDialog):
    # 信号：复习完成，请求返回模块选择器
    review_completed = pyqtSignal()
```

##### 修改总结页面按钮
将原来的单个"关闭"按钮改为两个按钮：

```
┌─────────────────────────────────────┐
│         🎉 复习完成！                │
│    本次复习了 X 道题目               │
│                                     │
│    🔴 生疏：X 题                    │
│    🟡 困难：X 题                    │
│    🟢 掌握：X 题                    │
│    🔵 熟练：X 题                    │
│                                     │
│  [🔄 继续复习]  [🏠 返回主页]       │
└─────────────────────────────────────┘
```

**按钮功能**：
- **🔄 继续复习**（绿色）：发出`review_completed`信号，关闭对话框，重新打开模块选择器
- **🏠 返回主页**（蓝色）：关闭对话框，返回主页面

##### 主窗口处理
在`on_module_selected_for_review()`中连接信号：
```python
dialog = ReviewDialog(all_questions, self.review_service, self)
# 连接继续复习信号
dialog.review_completed.connect(self.start_review)
dialog.exec()
```

当用户点击"继续复习"时：
1. `ReviewDialog`发出`review_completed`信号
2. 主窗口接收信号，调用`self.start_review()`
3. 重新打开模块选择器
4. 用户可以选择新的模块继续复习

#### 用户流程
```
开始复习 → 选择模块 → 复习题目 → 完成总结
                ↑                      ↓
                └──── 点击"继续复习" ────┘
```

### 2. 复习历史表格字体颜色优化
**需求**：复习历史表格的文字颜色需要改为黑色，提高可读性。

#### 修改前
表格项没有明确设置颜色，可能继承父级样式，导致颜色不一致。

#### 修改后
在表格样式中明确设置黑色字体：
```python
self.table.setStyleSheet("""
    QTableWidget {
        color: #2c3e50;  # 深灰色（接近黑色）
    }
    QTableWidget::item {
        color: #2c3e50;  # 深灰色（接近黑色）
    }
    QTableWidget::item:selected {
        color: white;    # 选中时白色
    }
""")
```

**颜色说明**：
- 使用`#2c3e50`（深灰色）而不是纯黑色`#000000`
- 深灰色更柔和，减少视觉疲劳
- 选中时变为白色，保持良好对比度

#### 特殊列保持彩色
掌握度列仍然使用彩色标记，通过代码单独设置：
```python
mastery_item.setForeground(mastery_color)  # 红/橙/绿/蓝
```

这样既保证了整体可读性，又保留了掌握度的视觉区分。

## 技术实现

### 文件修改

#### 1. review_dialog_new.py
```python
# 添加信号
class ReviewDialog(QDialog):
    review_completed = pyqtSignal()

# 修改总结页面
def show_summary(self):
    # ... 统计信息 ...
    
    # 按钮区域
    button_layout = QHBoxLayout()
    
    # 继续复习按钮
    continue_btn = QPushButton("🔄 继续复习")
    continue_btn.clicked.connect(self.on_continue_review)
    button_layout.addWidget(continue_btn)
    
    # 返回主页按钮
    home_btn = QPushButton("🏠 返回主页")
    home_btn.clicked.connect(self.accept)
    button_layout.addWidget(home_btn)

# 新增方法
def on_continue_review(self):
    """继续复习 - 返回模块选择器"""
    self.review_completed.emit()
    self.accept()
```

#### 2. main_window.py
```python
def on_module_selected_for_review(self, subject: str, question_type: str):
    # ... 获取题目 ...
    
    # 创建复习对话框
    dialog = ReviewDialog(all_questions, self.review_service, self)
    
    # 连接继续复习信号
    dialog.review_completed.connect(self.start_review)
    
    dialog.exec()
```

#### 3. review_history_dialog.py
```python
# 表格样式
self.table.setStyleSheet("""
    QTableWidget {
        color: #2c3e50;
    }
    QTableWidget::item {
        color: #2c3e50;
    }
    QTableWidget::item:selected {
        color: white;
    }
""")
```

## 用户体验提升

### 1. 连续复习流程
**改进前**：
- 复习完成 → 关闭 → 返回主页 → 点击"开始复习" → 选择模块 → 开始复习

**改进后**：
- 复习完成 → 点击"继续复习" → 选择模块 → 开始复习

**优势**：
- ✅ 减少3个步骤
- ✅ 提高复习效率
- ✅ 保持用户专注度
- ✅ 符合用户心理预期

### 2. 灵活选择
用户可以根据需求选择：
- **继续复习**：适合想要多轮复习的用户
- **返回主页**：适合想要休息或查看其他内容的用户

### 3. 视觉清晰
- **按钮颜色区分**：绿色（继续）vs 蓝色（返回）
- **图标辅助**：🔄（循环）vs 🏠（主页）
- **文字明确**：清楚表达按钮功能

### 4. 历史记录可读性
- **统一字体颜色**：深灰色，易于阅读
- **保留彩色标记**：掌握度列仍然彩色，快速识别
- **高对比度**：选中时白色文字，清晰可见

## 测试验证

### 测试场景1：继续复习
1. 开始复习，选择一个模块
2. 完成所有题目
3. 在总结页面点击"🔄 继续复习"
4. 确认模块选择器重新打开
5. 选择另一个模块
6. 确认可以正常复习

### 测试场景2：返回主页
1. 开始复习，选择一个模块
2. 完成所有题目
3. 在总结页面点击"🏠 返回主页"
4. 确认返回主页面
5. 确认数据已刷新

### 测试场景3：历史记录显示
1. 完成几次复习
2. 打开模块选择器
3. 点击"📊 查看历史"
4. 确认表格文字为深灰色（黑色）
5. 确认掌握度列仍然是彩色
6. 选中一行，确认文字变为白色

## 相关文件

### 修改的文件
- `src/mistake_book/ui/dialogs/review_dialog_new.py`
  - 添加：`review_completed`信号
  - 修改：`show_summary()` - 两个按钮
  - 新增：`on_continue_review()` - 发出信号

- `src/mistake_book/ui/main_window.py`
  - 修改：`on_module_selected_for_review()` - 连接信号

- `src/mistake_book/ui/dialogs/review_history_dialog.py`
  - 修改：表格样式 - 添加字体颜色

## 优势总结

### 用户体验
1. **流程优化**：减少操作步骤，提高效率
2. **灵活选择**：提供两种选项，满足不同需求
3. **视觉清晰**：颜色、图标、文字三重提示
4. **可读性强**：黑色字体，清晰易读

### 技术实现
1. **信号机制**：解耦对话框和主窗口
2. **样式统一**：明确设置颜色，避免继承问题
3. **代码简洁**：逻辑清晰，易于维护

## 更新日期
2026年2月4日
