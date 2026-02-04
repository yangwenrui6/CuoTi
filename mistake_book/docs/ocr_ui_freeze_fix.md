# OCR识别导致UI未响应问题修复

## 问题描述

模型加载完成之后，执行OCR识别时会出现UI未响应的情况。

## 问题原因

OCR识别操作（`recognize_image_with_retry`）在主线程（UI线程）中同步执行，导致：
1. 模型加载时阻塞UI（几秒到几分钟）
2. 图片识别时阻塞UI（1-3秒）
3. 用户无法操作界面，感觉程序"卡死"

## 解决方案

将OCR识别操作移到后台线程（QThread）中执行，避免阻塞UI线程。

### 修改的文件

`src/mistake_book/ui/dialogs/add_dialog.py`

### 修改内容

#### 1. 自动OCR识别（拖拽图片后）

**修改前**：
```python
def _do_actual_recognition(self):
    """实际执行OCR识别"""
    # 在主线程中同步执行，会阻塞UI
    success, message, recognized_text = self.question_service.recognize_image_with_retry(
        Path(self.image_path)
    )
    # ... 处理结果
```

**修改后**：
```python
def _do_actual_recognition(self):
    """实际执行OCR识别 - 在后台线程中执行"""
    from PyQt6.QtCore import QThread, pyqtSignal
    
    class OCRWorker(QThread):
        """OCR识别工作线程"""
        finished = pyqtSignal(bool, str, str)
        
        def __init__(self, question_service, image_path):
            super().__init__()
            self.question_service = question_service
            self.image_path = image_path
        
        def run(self):
            """在后台线程中执行OCR识别"""
            try:
                success, message, recognized_text = self.question_service.recognize_image_with_retry(
                    Path(self.image_path)
                )
                self.finished.emit(success, message, recognized_text or "")
            except Exception as e:
                self.finished.emit(False, f"识别出错：{str(e)}", "")
    
    # 创建并启动工作线程
    self.ocr_worker = OCRWorker(self.question_service, self.image_path)
    self.ocr_worker.finished.connect(self._on_ocr_finished)
    self.ocr_worker.start()

def _on_ocr_finished(self, success: bool, message: str, recognized_text: str):
    """OCR识别完成回调 - 在主线程中更新UI"""
    # ... 更新UI
```

#### 2. 手动OCR识别（点击按钮）

同样的修改方式，将 `run_ocr` 方法改为使用后台线程。

## 技术细节

### QThread工作原理

1. **创建工作线程**：继承 `QThread`，在 `run()` 方法中执行耗时操作
2. **信号通信**：使用 `pyqtSignal` 在线程间传递数据
3. **线程安全**：
   - 后台线程：执行OCR识别（耗时操作）
   - 主线程：更新UI（通过信号槽机制）

### 优点

1. ✅ UI保持响应，用户可以随时操作
2. ✅ 显示"识别中..."提示，用户体验更好
3. ✅ 可以在识别过程中取消或执行其他操作
4. ✅ 避免"程序未响应"的假象

### 注意事项

1. **线程安全**：不要在后台线程中直接操作UI组件
2. **信号槽**：使用信号槽机制在线程间通信
3. **异常处理**：后台线程中的异常需要捕获并通过信号传递

## 测试验证

### 测试场景

1. 拖拽图片后自动识别
2. 点击"重新识别"按钮
3. 识别过程中操作其他UI元素

### 预期结果

- ✅ UI始终保持响应
- ✅ 可以在识别过程中操作其他控件
- ✅ 识别完成后自动填充结果
- ✅ 识别失败时显示友好提示

## 相关文档

- `docs/ocr_async_loading.md` - OCR异步加载方案
- `docs/ocr_lazy_loading.md` - OCR延迟加载方案
- `docs/ocr_model_download_issue.md` - 模型下载问题

## 后续优化建议

1. **进度显示**：显示识别进度条
2. **取消功能**：允许用户取消正在进行的识别
3. **批量识别**：支持同时识别多张图片
4. **缓存结果**：缓存已识别的图片结果
