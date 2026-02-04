# 防止重复保存

## 修改日期
2026-02-03

## 问题描述
在添加错题对话框中,用户点击"保存"按钮后,如果对话框没有立即关闭,用户可以继续点击保存按钮,导致同一道题目被重复保存到数据库中。

## 问题原因
保存按钮在整个保存过程中一直处于可用状态,没有任何防护机制阻止用户重复点击。

## 解决方案

### 1. 保存按钮引用
将保存按钮保存为实例变量,以便在保存过程中控制其状态:

```python
# 修改前
save_btn = QPushButton("💾 保存")
save_btn.clicked.connect(self.save_question)

# 修改后
self.save_btn = QPushButton("💾 保存")
self.save_btn.clicked.connect(self.save_question)
```

### 2. 保存时禁用按钮
在 `save_question()` 方法开始时立即禁用按钮:

```python
def save_question(self):
    # 禁用保存按钮,防止重复点击
    self.save_btn.setEnabled(False)
    self.save_btn.setText("保存中...")
    
    # ... 保存逻辑 ...
```

### 3. 失败时恢复按钮
如果验证失败或保存失败,恢复按钮状态:

```python
# 验证失败
if not question_data["content"]:
    QMessageBox.warning(self, "验证失败", "题目内容不能为空")
    self.save_btn.setEnabled(True)
    self.save_btn.setText("💾 保存")
    return

# 保存失败
if not success:
    QMessageBox.warning(self, "保存失败", message)
    self.save_btn.setEnabled(True)
    self.save_btn.setText("💾 保存")
```

### 4. 成功时关闭对话框
保存成功时直接关闭对话框,不需要恢复按钮:

```python
if success:
    self.accept()  # 对话框关闭,按钮状态无需恢复
```

## 完整流程

### 正常保存流程
1. 用户点击"💾 保存"按钮
2. 按钮立即变为"保存中..."并禁用
3. 验证数据
4. 保存到数据库
5. 对话框关闭(通过 `self.accept()`)
6. 主窗口刷新列表

### 验证失败流程
1. 用户点击"💾 保存"按钮
2. 按钮立即变为"保存中..."并禁用
3. 验证失败,显示错误提示
4. 按钮恢复为"💾 保存"并启用
5. 用户可以修改后重新保存

### 保存失败流程
1. 用户点击"💾 保存"按钮
2. 按钮立即变为"保存中..."并禁用
3. 验证通过
4. 保存到数据库失败
5. 显示错误提示
6. 按钮恢复为"💾 保存"并启用
7. 用户可以重试

## 用户体验改进

### 修改前
- ❌ 可以重复点击保存按钮
- ❌ 可能导致重复数据
- ❌ 没有视觉反馈表示正在保存

### 修改后
- ✅ 点击后按钮立即禁用
- ✅ 按钮文字变为"保存中...",提供视觉反馈
- ✅ 防止重复保存
- ✅ 失败时可以重试

## 技术细节

### 按钮状态管理
```python
# 禁用按钮
self.save_btn.setEnabled(False)
self.save_btn.setText("保存中...")

# 恢复按钮
self.save_btn.setEnabled(True)
self.save_btn.setText("💾 保存")
```

### 为什么成功时不需要恢复
当 `self.accept()` 被调用时,对话框会关闭并销毁,所以不需要恢复按钮状态。只有在对话框继续显示的情况下(验证失败或保存失败)才需要恢复。

## 相关文件
- `src/mistake_book/ui/dialogs/add_dialog.py`

## 测试场景

### 场景1: 快速连续点击
1. 填写题目信息
2. 快速连续点击保存按钮3次
3. 验证: 只保存一次,数据库中只有一条记录

### 场景2: 验证失败后重试
1. 不填写题目内容
2. 点击保存
3. 看到"题目内容不能为空"提示
4. 验证: 按钮恢复可用状态
5. 填写内容后可以再次保存

### 场景3: 保存失败后重试
1. 填写题目信息
2. 模拟数据库错误
3. 点击保存
4. 看到保存失败提示
5. 验证: 按钮恢复可用状态
6. 可以重试保存
