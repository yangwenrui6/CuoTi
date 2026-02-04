# 卡片点击交互优化

## 修改日期
2026-02-03

## 修改内容

### 1. 删除查看按钮
- **位置**: `src/mistake_book/ui/widgets/question_card.py`
- **修改**: 删除了"👁️ 查看"按钮及其相关代码
- **原因**: 简化UI,减少操作步骤

### 2. 优化卡片信号
- **修改前**: 
  - `clicked` 信号: 点击卡片区域
  - `view_detail` 信号: 点击查看按钮
  - `delete_requested` 信号: 点击删除按钮

- **修改后**:
  - `clicked` 信号: 点击卡片直接查看详情
  - `delete_requested` 信号: 点击删除按钮

### 3. 更新主窗口交互
- **位置**: `src/mistake_book/ui/main_window.py`
- **修改**: 
  - 删除了 `on_card_clicked()` 方法
  - 将 `card.clicked` 信号直接连接到 `on_view_detail()` 方法
  - 点击卡片任意位置(除删除按钮外)即可查看详情

## 用户体验改进

### 修改前
1. 用户看到错题卡片
2. 需要找到并点击"查看"按钮
3. 打开详情对话框

### 修改后
1. 用户看到错题卡片
2. 直接点击卡片任意位置
3. 立即打开详情对话框

## 技术实现

### QuestionCard 类
```python
class QuestionCard(QWidget):
    clicked = pyqtSignal(dict)  # 点击信号(查看详情)
    delete_requested = pyqtSignal(dict)  # 删除请求信号
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 点击卡片查看详情"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.question_data)
```

### MainWindow 连接
```python
def display_questions(self, questions):
    for question in questions:
        card = QuestionCard(question)
        # 点击卡片查看详情
        card.clicked.connect(lambda q=question: self.on_view_detail(q))
        # 删除按钮
        card.delete_requested.connect(lambda q=question: self.on_delete_question(q))
```

## 注意事项

1. **删除按钮独立**: 删除按钮点击事件不会触发卡片的查看详情功能
2. **视觉反馈**: 卡片保留hover效果,提示用户可点击
3. **无障碍**: 整个卡片区域都可点击,增大了点击目标面积

## 相关文件
- `src/mistake_book/ui/widgets/question_card.py`
- `src/mistake_book/ui/main_window.py`
