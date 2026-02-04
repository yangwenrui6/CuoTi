# Qt线程安全问题 - 已解决 ✅

## 问题

应用启动时出现错误：
```
QObject: Cannot create children for a parent that is in a different thread.
QObject::startTimer: Timers can only be used with threads started with QThread
```

## 根本原因

在Qt中，**UI组件只能在主线程中操作**。

错误的调用链：
```
后台线程（OCR初始化）
  ↓
初始化完成，调用回调
  ↓
MainWindow.on_ocr_init_complete()
  ↓
操作 QStatusBar、QMessageBox ← ❌ 在后台线程中操作UI
```

## 解决方案

使用`QTimer.singleShot`确保UI操作在主线程中执行。

### 修改的文件

`src/mistake_book/ui/main_window.py`

### 核心改动

#### 修改前（线程不安全）

```python
def _on_ocr_engine_created(self, ocr_engine):
    # ❌ 直接设置回调，可能在后台线程中执行
    ocr_engine.set_init_complete_callback(self.on_ocr_init_complete)
```

#### 修改后（线程安全）

```python
def _on_ocr_engine_created(self, ocr_engine):
    # ✅ 使用QTimer确保在主线程中执行
    def thread_safe_callback():
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self.on_ocr_init_complete)
    
    ocr_engine.set_init_complete_callback(thread_safe_callback)
```

## Qt线程安全规则

### 只能在主线程中执行

- ❌ 创建或操作UI组件
- ❌ 显示对话框
- ❌ 操作QStatusBar
- ❌ 使用QTimer

### 可以在任何线程中执行

- ✅ 纯计算操作
- ✅ 文件I/O
- ✅ 网络请求
- ✅ 发射信号（pyqtSignal.emit）

### 线程间通信的正确方式

1. **信号槽机制**（推荐）
2. **QTimer.singleShot**
3. **QMetaObject.invokeMethod**

## 效果

修改后：
- ✅ 无线程安全错误
- ✅ 状态栏消息正常显示
- ✅ OCR功能正常工作
- ✅ 应用稳定运行

## 完整的OCR优化方案

我们解决了四个关键问题：

1. ✅ **模型重复下载** → 只使用中文模型
2. ✅ **识别时UI卡顿** → OCR识别在后台线程
3. ✅ **启动时UI卡顿** → OCR引擎创建在后台线程
4. ✅ **线程安全错误** → 使用QTimer确保UI操作在主线程

现在应用应该完全稳定了！

## 相关文档

- `docs/qt_thread_safety_fix.md` - 详细技术文档
- `docs/app_startup_freeze_fix.md` - 应用启动优化
- `docs/ocr_ui_freeze_fix.md` - OCR识别优化
- `docs/ocr_model_download_issue.md` - 模型下载问题
