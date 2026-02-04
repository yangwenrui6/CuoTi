# 复习历史可视化与Bug修复

## 问题描述

### 问题1：复习完成显示0道题
用户反馈复习完成后，总结页面显示"本次复习了 0 道题目"。

### 问题2：缺少历史记录可视化
复习历史功能缺少可视化界面，用户无法查看详细的复习记录。

## 问题分析

### Bug原因
在`ReviewDialog.on_mastery_selected()`方法中，只有当`process_review_result()`返回成功时，才会将题目添加到`reviewed_questions`列表。如果保存失败，题目不会被记录，导致总结时显示0道题。

```python
# 原有代码（有问题）
if success:
    self.reviewed_questions.append({...})  # 只在成功时添加
    self.current_index += 1
    self.load_question()
else:
    # 失败时没有添加到列表
    self.current_index += 1
    self.load_question()
```

## 解决方案

### 1. 修复复习计数Bug

#### 修改逻辑
无论保存是否成功，都先将题目添加到`reviewed_questions`列表，确保用户的复习行为被记录。

```python
def on_mastery_selected(self, result: ReviewResult):
    """选择掌握度"""
    question = self.questions[self.current_index]
    question_id = question.get('id')
    
    # 先记录已复习的题目（无论保存是否成功）
    self.reviewed_questions.append({
        'question': question,
        'result': result,
        'updates': {}
    })
    
    # 调用服务更新题目状态
    success, message, updates = self.review_service.process_review_result(
        question_id, result
    )
    
    if success:
        # 更新记录中的updates
        self.reviewed_questions[-1]['updates'] = updates
    
    # 进入下一题
    self.current_index += 1
    self.load_question()
```

#### 优势
- ✅ 确保用户的复习行为被正确统计
- ✅ 即使数据库保存失败，用户也能看到复习总结
- ✅ 提升用户体验，避免"白复习"的感觉

### 2. 实现复习历史可视化

#### 新增ReviewHistoryDialog
创建专门的复习历史对话框，以表格形式展示复习记录。

**文件**: `src/mistake_book/ui/dialogs/review_history_dialog.py`

#### 功能特性
1. **表格展示**：清晰的列表视图
2. **详细信息**：显示6列关键信息
3. **颜色标记**：不同掌握度用不同颜色
4. **时间排序**：按复习时间倒序显示
5. **数量限制**：显示最近30条记录
6. **实时刷新**：支持手动刷新数据

#### 表格列设计

| 列名 | 内容 | 样式 |
|------|------|------|
| 复习时间 | YYYY-MM-DD HH:MM | 居中 |
| 科目 | 数学、英语等 | 居中 |
| 题型 | 选择题、填空题等 | 居中 |
| 题目摘要 | 前50字+... | 左对齐，自动拉伸 |
| 掌握度 | 🔴生疏/🟡困难/🟢掌握/🔵熟练 | 居中，彩色加粗 |
| 下次复习 | YYYY-MM-DD | 居中，显示是否到期 |

#### 掌握度颜色映射
```python
mastery_map = {
    ReviewResult.AGAIN.value: ("🔴 生疏", QColor(231, 76, 60)),   # 红色
    ReviewResult.HARD.value: ("🟡 困难", QColor(243, 156, 18)),   # 橙色
    ReviewResult.GOOD.value: ("🟢 掌握", QColor(39, 174, 96)),    # 绿色
    ReviewResult.EASY.value: ("🔵 熟练", QColor(52, 152, 219))    # 蓝色
}
```

#### UI设计
```
┌─────────────────────────────────────────────────┐
│           📊 复习历史记录                        │
│     显示最近30次复习记录（按时间倒序）            │
├─────────────────────────────────────────────────┤
│ 复习时间 │ 科目 │ 题型 │ 题目摘要 │ 掌握度 │ 下次复习 │
├─────────────────────────────────────────────────┤
│ 2026-02-04 15:30 │ 数学 │ 选择题 │ 求函数... │ 🟢掌握 │ 2026-02-10 │
│ 2026-02-04 15:28 │ 英语 │ 填空题 │ The... │ 🔴生疏 │ 2026-02-05 (已到期) │
│ ...                                              │
└─────────────────────────────────────────────────┘
│                    [🔄 刷新]  [关闭]              │
└─────────────────────────────────────────────────┘
```

### 3. 集成到模块选择器

#### 添加"查看历史"按钮
在模块选择器底部添加橙色的"📊 查看历史"按钮。

```python
# 查看历史按钮
history_btn = QPushButton("📊 查看历史")
history_btn.setStyleSheet("""
    QPushButton {
        background-color: #e67e22;  # 橙色
        color: white;
        ...
    }
    QPushButton:hover {
        background-color: #d35400;
    }
""")
history_btn.clicked.connect(self.show_history)
```

#### 按钮布局
```
┌─────────────────────────────────────────┐
│  [📊 查看历史] [📖 复习全部] [🚀 开始复习] [取消]  │
└─────────────────────────────────────────┘
```

#### show_history()方法
```python
def show_history(self):
    """显示复习历史"""
    from mistake_book.ui.dialogs.review_history_dialog import ReviewHistoryDialog
    
    dialog = ReviewHistoryDialog(self.review_service, self)
    dialog.exec()
```

## 技术实现

### 数据查询
使用SQLAlchemy的join查询，同时获取复习记录和题目信息：

```python
records = (
    session.query(ReviewRecord, Question)
    .join(Question, ReviewRecord.question_id == Question.id)
    .order_by(ReviewRecord.review_date.desc())
    .limit(30)
    .all()
)
```

### 表格填充
遍历查询结果，为每一行设置6列数据：

```python
for record, question in records:
    row = self.table.rowCount()
    self.table.insertRow(row)
    
    # 设置各列数据
    self.table.setItem(row, 0, time_item)      # 复习时间
    self.table.setItem(row, 1, subject_item)   # 科目
    self.table.setItem(row, 2, type_item)      # 题型
    self.table.setItem(row, 3, summary_item)   # 题目摘要
    self.table.setItem(row, 4, mastery_item)   # 掌握度（彩色）
    self.table.setItem(row, 5, next_item)      # 下次复习
```

### 样式设置
- **表格边框**：2px实线，圆角8px
- **表头**：深灰色背景，白色文字，加粗
- **选中行**：蓝色背景，白色文字
- **网格线**：浅灰色
- **禁止编辑**：只读模式

## 用户体验改进

### 使用流程
1. 用户点击"开始复习"
2. 在模块选择器中，点击"📊 查看历史"
3. 弹出复习历史对话框
4. 查看最近30次复习记录
5. 可以点击"🔄 刷新"更新数据
6. 关闭对话框返回模块选择器

### 视觉反馈
- **颜色区分**：不同掌握度用不同颜色，一目了然
- **到期提示**：已到期的题目显示"(已到期)"
- **时间格式**：统一的日期时间格式
- **摘要截断**：长题目自动截断，保持整洁

### 信息完整性
- ✅ 复习时间：精确到分钟
- ✅ 题目信息：科目、题型、内容摘要
- ✅ 复习结果：掌握度评价
- ✅ 下次复习：计划复习时间

## 相关文件

### 新增文件
- `src/mistake_book/ui/dialogs/review_history_dialog.py` - 复习历史对话框

### 修改文件
- `src/mistake_book/ui/dialogs/review_dialog_new.py`
  - 修改：`on_mastery_selected()` - 先记录再保存
  
- `src/mistake_book/ui/dialogs/review_module_selector.py`
  - 新增：`show_history()` - 显示历史对话框
  - 修改：`init_ui()` - 添加"查看历史"按钮
  
- `src/mistake_book/ui/dialogs/__init__.py`
  - 导出：`ReviewHistoryDialog`

## 测试验证

### 测试步骤
1. 添加多个错题
2. 进行复习，选择不同的掌握度
3. 复习完成后，检查总结页面是否正确显示复习数量
4. 返回主界面，再次点击"开始复习"
5. 点击"📊 查看历史"按钮
6. 确认历史记录正确显示
7. 检查颜色、时间、内容是否正确
8. 点击"🔄 刷新"，确认数据更新

### 边界情况
- ✅ 无复习记录：表格为空，不报错
- ✅ 少于30条：显示所有记录
- ✅ 超过30条：只显示最近30条
- ✅ 数据库错误：显示友好的错误提示

## 优势总结

### Bug修复
1. **准确统计**：确保复习数量正确显示
2. **容错处理**：即使保存失败也能看到总结
3. **用户体验**：避免"白复习"的挫败感

### 历史可视化
1. **直观展示**：表格形式清晰易读
2. **信息丰富**：6列关键信息一览无余
3. **颜色标记**：快速识别掌握程度
4. **实时更新**：支持手动刷新
5. **易于访问**：一键打开历史记录

## 更新日期
2026年2月4日
