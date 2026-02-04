# 复习历史功能

## 功能概述
在复习模块选择器中添加"复习历史"选项，允许用户快速复习最近复习过的30道题目。

## 功能特性

### 1. 复习历史选项
- 位置：模块选择器的科目列表顶部
- 显示：🕒 复习历史 (最近30题)
- 主题：紫色（#9b59b6）
- 自动限制：最多显示最近复习的30道题目

### 2. 复习记录保存
每次复习完成后，系统会自动保存复习记录到数据库：
- 题目ID
- 复习时间
- 复习结果（生疏/困难/掌握/熟练）
- 耗时（可选）

### 3. 智能去重
获取复习历史时，如果同一题目被多次复习，只保留最近的一次记录。

## 技术实现

### 数据库模型
使用现有的`ReviewRecord`表：
```python
class ReviewRecord(Base):
    """复习记录"""
    __tablename__ = "review_records"
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    review_date = Column(DateTime, default=datetime.now)
    result = Column(Integer)  # ReviewResult枚举值
    time_spent = Column(Integer)  # 耗时（秒）
    
    question = relationship("Question", back_populates="reviews")
```

### ReviewService新增方法

#### 1. get_recently_reviewed_questions()
```python
def get_recently_reviewed_questions(self, limit: int = 30) -> List[Dict[str, Any]]:
    """
    获取最近复习的题目
    
    Args:
        limit: 返回的题目数量限制（默认30）
    
    Returns:
        最近复习的题目列表（按复习时间倒序）
    """
```

**实现逻辑**：
1. 查询ReviewRecord表，按review_date倒序
2. 去重：每个题目只保留最近的一次复习记录
3. 限制数量：最多返回30道题
4. 返回完整的题目信息

#### 2. _save_review_record()
```python
def _save_review_record(
    self, 
    question_id: int, 
    result: ReviewResult, 
    time_spent: Optional[int] = None
):
    """
    保存复习记录
    
    Args:
        question_id: 题目ID
        result: 复习结果
        time_spent: 耗时（秒）
    """
```

**调用时机**：
在`process_review_result()`方法中，更新题目数据成功后自动调用。

### 模块选择器更新

#### 1. 构造函数修改
```python
def __init__(self, data_manager, review_service, parent=None):
    # 新增review_service参数
    self.review_service = review_service
    self.is_review_history: bool = False  # 标记是否选择了复习历史
```

#### 2. UI布局
在科目列表顶部添加：
```
┌─────────────────────────┐
│ 🕒 复习历史 (最近30题)   │  ← 特殊项（紫色）
│ ─────────────────────── │  ← 分隔线
│ 数学 (50题)             │
│ 英语 (30题)             │
│ ...                     │
└─────────────────────────┘
```

#### 3. 选择处理
```python
def on_subject_selected(self, item: QListWidgetItem):
    # 检查是否是复习历史
    if item.data(Qt.ItemDataRole.UserRole) == "REVIEW_HISTORY":
        self.is_review_history = True
        # 禁用题型列表
        # 直接启用开始按钮
```

#### 4. 信号发送
选择复习历史时，发送特殊标记：
```python
self.module_selected.emit("REVIEW_HISTORY", "")
```

### 主窗口处理

#### on_module_selected_for_review()修改
```python
def on_module_selected_for_review(self, subject: str, question_type: str):
    # 检查是否选择了复习历史
    if subject == "REVIEW_HISTORY":
        # 获取最近复习的30道题
        recent_questions = self.review_service.get_recently_reviewed_questions(30)
        
        if not recent_questions:
            QMessageBox.information(self, "提示", "暂无复习历史")
            return
        
        # 创建复习对话框
        dialog = ReviewDialog(recent_questions, self.review_service, self)
        dialog.exec()
        return
    
    # 原有的模块选择逻辑...
```

## 用户体验

### 使用流程
1. 用户点击"开始复习"
2. 在模块选择器中，看到顶部的"🕒 复习历史 (最近30题)"
3. 点击该选项
4. 提示显示："✅ 已选择：复习历史（最近复习的30道题）"（紫色背景）
5. 点击"🚀 开始复习"
6. 进入复习对话框，显示最近复习的30道题

### 视觉设计
- **颜色主题**：紫色（#9b59b6）
- **图标**：🕒（时钟）
- **背景色**：浅紫色（#f3e5f5）
- **位置**：列表顶部，优先级最高

### 提示信息
- 选择后：`✅ 已选择：复习历史（最近复习的30道题）`
- 无历史：`暂无复习历史`

## 数据管理

### 自动清理（可选）
如果需要限制数据库大小，可以添加定期清理逻辑：
- 保留最近3个月的复习记录
- 或保留每个题目最近10次复习记录

### 统计分析（未来扩展）
基于复习记录，可以实现：
- 复习频率统计
- 掌握度变化趋势
- 薄弱知识点分析
- 复习效率评估

## 相关文件

### 修改的文件
- `src/mistake_book/services/review_service.py`
  - 新增：`get_recently_reviewed_questions()`
  - 新增：`_save_review_record()`
  - 修改：`process_review_result()`

- `src/mistake_book/ui/dialogs/review_module_selector.py`
  - 修改：`__init__()` - 添加review_service参数
  - 修改：`init_ui()` - 添加复习历史选项
  - 修改：`on_subject_selected()` - 处理复习历史选择
  - 修改：`on_start_review()` - 发送特殊标记

- `src/mistake_book/ui/main_window.py`
  - 修改：`start_review()` - 传递review_service
  - 修改：`on_module_selected_for_review()` - 处理复习历史

### 使用的数据库表
- `review_records` - 复习记录表（已存在）
- `questions` - 题目表（已存在）

## 测试验证

### 测试步骤
1. 添加多个错题
2. 进行几次复习，选择不同的掌握度
3. 点击"开始复习"
4. 选择"🕒 复习历史 (最近30题)"
5. 确认显示最近复习的题目
6. 再次复习这些题目
7. 确认复习记录正确保存

### 边界情况
- ✅ 无复习历史：显示提示"暂无复习历史"
- ✅ 少于30题：显示所有已复习的题目
- ✅ 超过30题：只显示最近30题
- ✅ 同一题目多次复习：只保留最近一次

## 优势

1. **快速复习**：无需筛选，直接复习最近的题目
2. **巩固记忆**：重复复习有助于加深印象
3. **方便追踪**：了解自己最近复习了哪些内容
4. **智能去重**：避免重复显示同一题目

## 更新日期
2026年2月4日
