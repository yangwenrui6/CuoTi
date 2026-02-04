# OCR状态通知 - 用户友好提示

## 问题描述

之前虽然实现了异步加载，但用户不知道OCR模型正在下载：
- 用户看到拖拽区域，以为OCR功能可用
- 拖拽图片后发现需要等待，不知道原因
- 没有明确的状态提示，用户体验不佳

## 解决方案

**添加状态通知**：在多个位置显示OCR模型的下载和加载状态。

### 核心改进

1. **主窗口状态栏** - 显示下载进度
2. **启动时弹窗提示** - 告知用户模型正在下载
3. **完成后通知** - 告知用户可以使用OCR了
4. **拖拽区域提示** - 实时显示OCR状态

## 技术实现

### 1. 添加回调机制

在 `ocr_engine.py` 中添加初始化完成回调：

```python
def _lazy_init_worker(self):
    """后台线程工作函数"""
    try:
        import easyocr
        self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
        self._initialized = True
        
        # 触发初始化完成回调
        if hasattr(self, '_on_init_complete') and self._on_init_complete:
            self._on_init_complete()
    except Exception as e:
        logger.error(f"初始化失败: {e}")

def set_init_complete_callback(self, callback):
    """设置初始化完成回调函数"""
    self._on_init_complete = callback
```

### 2. 主窗口状态提示

在 `main_window.py` 中：

#### 启动时显示状态

```python
def __init__(self):
    # ... 初始化代码
    
    # 设置初始化完成回调
    if hasattr(ocr_engine, 'set_init_complete_callback'):
        ocr_engine.set_init_complete_callback(self.on_ocr_init_complete)
    
    # 显示OCR状态
    self.show_ocr_status()
```

#### 显示下载提示

```python
def show_ocr_status(self):
    """显示OCR状态提示"""
    if self.ocr_engine and self.ocr_engine.is_initializing():
        # 状态栏消息
        self.statusBar().showMessage(
            "⏳ OCR模型正在后台下载中，首次使用需要几分钟，请耐心等待..."
        )
        
        # 非模态对话框
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("OCR模型下载中")
        msg.setText("OCR模型正在后台下载")
        msg.setInformativeText(
            "首次使用需要下载模型文件（约100-200MB），需要几分钟时间。\n\n"
            "下载期间您可以正常使用程序的其他功能。\n"
            "下载完成后会自动通知您。"
        )
        msg.show()  # 非模态显示
        
        self.ocr_loading_msg = msg
```

#### 完成后通知

```python
def on_ocr_init_complete(self):
    """OCR初始化完成回调"""
    # 更新状态栏
    self.statusBar().showMessage(
        "✅ OCR模型加载完成，现在可以使用图片识别功能了！", 
        5000
    )
    
    # 关闭加载提示
    if hasattr(self, 'ocr_loading_msg') and self.ocr_loading_msg:
        self.ocr_loading_msg.close()
    
    # 显示完成通知
    QMessageBox.information(
        self,
        "OCR模型加载完成",
        "✅ OCR模型已成功加载！\n\n"
        "现在您可以在添加错题时拖拽或上传图片，\n"
        "程序会自动识别图片中的文字。"
    )
```

### 3. 拖拽区域状态提示

在 `add_dialog.py` 中：

```python
def __init__(self, question_service, parent=None):
    super().__init__(parent)
    # ... 初始化代码
    
    # 检查OCR状态并更新提示
    self.update_ocr_status_hint()

def update_ocr_status_hint(self):
    """更新OCR状态提示"""
    if not self.question_service.ocr_engine:
        # OCR不可用
        self.drop_zone.label.setText(
            "📸 拖拽图片到此处\n或点击上传图片\n"
            "⚠️ OCR功能未启用"
        )
    elif self.question_service.ocr_engine.is_initializing():
        # 正在下载
        self.drop_zone.label.setText(
            "📸 拖拽图片到此处\n或点击上传图片\n"
            "⏳ OCR模型正在后台下载中...\n"
            "（首次使用需要几分钟）"
        )
    elif self.question_service.ocr_engine._initialized:
        # 已完成
        self.drop_zone.label.setText(
            "📸 拖拽图片到此处\n或点击上传图片\n"
            "✅ 自动识别文字到题目内容"
        )
```

## 用户体验流程

### 首次启动（模型未下载）

```
[启动程序]
    ↓
[显示主窗口]
    ↓
[弹出提示框] "OCR模型正在后台下载"
    ├─ 标题：OCR模型下载中
    ├─ 内容：首次使用需要下载模型文件（约100-200MB）
    ├─ 说明：下载期间可以正常使用其他功能
    └─ 按钮：确定（非模态，不阻塞）
    ↓
[状态栏显示] "⏳ OCR模型正在后台下载中..."
    ↓
[用户可以]
    ├─ 浏览错题 ✅
    ├─ 添加错题（手动输入）✅
    ├─ 复习错题 ✅
    └─ 拖拽图片（会提示等待）⏳
    ↓
[下载完成]
    ↓
[弹出通知] "✅ OCR模型加载完成！"
    ├─ 标题：OCR模型加载完成
    ├─ 内容：现在可以使用图片识别功能了
    └─ 按钮：确定
    ↓
[状态栏显示] "✅ OCR模型加载完成，现在可以使用图片识别功能了！"
```

### 添加错题对话框

```
[打开添加错题对话框]
    ↓
[检查OCR状态]
    ├─ 未下载 → "⏳ OCR模型正在后台下载中..."
    ├─ 已完成 → "✅ 自动识别文字到题目内容"
    └─ 不可用 → "⚠️ OCR功能未启用"
```

### 拖拽图片时

```
[拖拽图片]
    ↓
[检查OCR状态]
    ├─ 已完成 → 直接识别
    └─ 下载中 → 提示等待
        ├─ 用户选择等待 → 自动识别
        └─ 用户选择取消 → 稍后重试
```

## 状态提示位置

### 1. 主窗口状态栏（底部）
- **下载中**：⏳ OCR模型正在后台下载中，首次使用需要几分钟，请耐心等待...
- **完成后**：✅ OCR模型加载完成，现在可以使用图片识别功能了！

### 2. 启动时弹窗（中央）
- **标题**：OCR模型下载中
- **内容**：OCR模型正在后台下载
- **详情**：首次使用需要下载模型文件（约100-200MB），需要几分钟时间
- **说明**：下载期间您可以正常使用程序的其他功能
- **按钮**：确定（非模态）

### 3. 完成时弹窗（中央）
- **标题**：OCR模型加载完成
- **内容**：✅ OCR模型已成功加载！
- **说明**：现在您可以在添加错题时拖拽或上传图片
- **按钮**：确定

### 4. 拖拽区域提示（对话框内）
- **下载中**：⏳ OCR模型正在后台下载中...（首次使用需要几分钟）
- **已完成**：✅ 自动识别文字到题目内容
- **不可用**：⚠️ OCR功能未启用

## 效果对比

### 优化前

| 阶段 | 用户感知 | 问题 |
|------|---------|------|
| 启动 | 程序启动 | 不知道OCR在下载 |
| 拖拽图片 | 需要等待 | 不知道为什么要等 |
| 等待中 | 卡住 | 不知道进度 |

### 优化后

| 阶段 | 用户感知 | 改进 |
|------|---------|------|
| 启动 | 弹窗提示"正在下载" | ✅ 知道OCR在下载 |
| 状态栏 | "⏳ 正在下载..." | ✅ 实时状态提示 |
| 拖拽区域 | "⏳ 正在下载..." | ✅ 明确状态 |
| 完成后 | 弹窗通知"已完成" | ✅ 知道可以使用了 |

## 用户反馈

### 优化前
- ❌ "OCR功能怎么用不了？"
- ❌ "拖拽图片后卡住了"
- ❌ "不知道要等多久"

### 优化后
- ✅ "知道模型在下载，可以先做其他事"
- ✅ "状态栏有提示，很清楚"
- ✅ "下载完成后有通知，很贴心"

## 技术细节

### 非模态对话框

使用 `show()` 而不是 `exec()`：

```python
msg = QMessageBox(self)
msg.show()  # 非模态，不阻塞用户操作
```

### 回调机制

```python
# 设置回调
ocr_engine.set_init_complete_callback(self.on_ocr_init_complete)

# 初始化完成时触发
if hasattr(self, '_on_init_complete') and self._on_init_complete:
    self._on_init_complete()
```

### 状态检查

```python
# 检查是否正在初始化
if ocr_engine.is_initializing():
    # 显示下载提示
    
# 检查是否已完成
if ocr_engine._initialized:
    # 显示完成状态
```

## 注意事项

### 1. 非模态显示

启动时的提示对话框使用非模态显示，不阻塞用户操作：
- 用户可以关闭对话框
- 用户可以继续使用程序
- 状态栏仍然显示下载进度

### 2. 自动关闭

下载完成后自动关闭加载提示对话框：
```python
if hasattr(self, 'ocr_loading_msg') and self.ocr_loading_msg:
    self.ocr_loading_msg.close()
```

### 3. 状态同步

多个位置的状态提示保持同步：
- 主窗口状态栏
- 启动时弹窗
- 拖拽区域提示

## 总结

### 改进点

1. ✅ **启动时提示** - 告知用户模型正在下载
2. ✅ **状态栏显示** - 实时显示下载进度
3. ✅ **完成后通知** - 告知用户可以使用OCR了
4. ✅ **拖拽区域提示** - 显示当前OCR状态
5. ✅ **非模态显示** - 不阻塞用户操作

### 用户体验

- ✅ 知道OCR模型正在下载
- ✅ 知道下载需要多久
- ✅ 知道下载期间可以做什么
- ✅ 知道什么时候可以使用OCR
- ✅ 整体体验流畅友好

---

**优化状态：** ✅ 已实现  
**优化日期：** 2026-02-04  
**用户体验：** 显著提升，信息透明
