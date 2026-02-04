# Qt线程安全问题修复

## 问题描述

应用启动时出现以下错误：

```
QObject: Cannot create children for a parent that is in a different thread.
(Parent is QStatusBar(0x26685288830), parent's thread is QThread(0x266845ff700), 
current thread is QThread(0x26684d4b550))

QObject::startTimer: Timers can only be used with threads started with QThread
```

## 问题原因

在Qt中，**UI组件只能在主线程中操作**。错误发生的原因：

1. OCR引擎在后台线程中初始化
2. 初始化完成后，从后台线程调用回调函数
3. 回调函数中尝试操作UI组件（QStatusBar、QMessageBox）
4. 违反了Qt的线程安全规则

## 错误的调用链

```
后台线程（OCR初始化）
  ↓
_lazy_init_worker() 完成
  ↓
调用 _on_init_complete() 回调
  ↓
MainWindow.on_ocr_init_complete()
  ↓
操作 QStatusBar、QMessageBox ← ❌ 错误！在后台线程中操作UI
```

## 解决方案

使用Qt的线程安全机制，确保UI操作在主线程中执行。

### 方法1：使用QTimer.singleShot

```python
def _on_ocr_engine_created(self, ocr_engine):
    if ocr_engine:
        # 设置回调时，使用QTimer确保在主线程中执行
        def thread_safe_callback():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.on_ocr_init_complete)
        
        ocr_engine.set_init_complete_callback(thread_safe_callback)
```

### 方法2：使用信号槽机制

```python
class MainWindow(QMainWindow):
    ocr_ready_signal = pyqtSignal()  # 定义信号
    
    def __init__(self):
        # 连接信号到槽
        self.ocr_ready_signal.connect(self.on_ocr_init_complete)
    
    def _on_ocr_engine_created(self, ocr_engine):
        # 设置回调时，发射信号
        def thread_safe_callback():
            self.ocr_ready_signal.emit()
        
        ocr_engine.set_init_complete_callback(thread_safe_callback)
```

## 修改的文件

`src/mistake_book/ui/main_window.py`

### 修改内容

#### 1. 简化show_ocr_status方法

移除了弹窗提示，只保留状态栏消息：

```python
def show_ocr_status(self):
    """显示OCR状态提示"""
    if not self.ocr_engine:
        return
    
    if hasattr(self.ocr_engine, 'is_initializing') and self.ocr_engine.is_initializing():
        # 只显示状态栏消息，不创建对话框
        self.statusBar().showMessage("⏳ OCR模型正在后台加载中...")
        logger.info("OCR模型正在后台加载中...")
```

#### 2. 使用线程安全的回调包装器

```python
def _on_ocr_engine_created(self, ocr_engine):
    if ocr_engine:
        # 创建线程安全的回调包装器
        def thread_safe_callback():
            from PyQt6.QtCore import QTimer
            # 使用QTimer.singleShot确保在主线程中执行
            QTimer.singleShot(0, self.on_ocr_init_complete)
        
        ocr_engine.set_init_complete_callback(thread_safe_callback)
```

## Qt线程安全规则

### 可以在任何线程中执行的操作

- ✅ 纯计算操作
- ✅ 文件I/O
- ✅ 网络请求
- ✅ 数据库操作
- ✅ 发射信号（pyqtSignal.emit）

### 只能在主线程中执行的操作

- ❌ 创建或操作UI组件（QWidget、QLabel、QPushButton等）
- ❌ 操作QApplication
- ❌ 使用QTimer（除非在对应线程中创建）
- ❌ 显示对话框（QMessageBox、QDialog等）

### 线程间通信的正确方式

1. **信号槽机制**（推荐）
   ```python
   # 后台线程
   self.finished.emit(result)
   
   # 主线程
   worker.finished.connect(self.on_finished)
   ```

2. **QTimer.singleShot**
   ```python
   # 后台线程
   QTimer.singleShot(0, lambda: self.update_ui(result))
   ```

3. **QMetaObject.invokeMethod**
   ```python
   # 后台线程
   QMetaObject.invokeMethod(
       self,
       "update_ui",
       Qt.ConnectionType.QueuedConnection,
       Q_ARG(str, result)
   )
   ```

## 测试验证

### 测试步骤

1. 启动应用
2. 观察控制台是否有线程错误
3. 等待OCR初始化完成
4. 检查状态栏消息是否正常显示
5. 测试OCR功能是否正常

### 预期结果

- ✅ 无线程安全错误
- ✅ 状态栏消息正常显示
- ✅ OCR功能正常工作
- ✅ 应用稳定运行

## 常见Qt线程错误

### 错误1：在后台线程中创建UI组件

```python
# ❌ 错误
class Worker(QThread):
    def run(self):
        msg = QMessageBox()  # 错误！
        msg.show()
```

### 错误2：在后台线程中操作UI组件

```python
# ❌ 错误
class Worker(QThread):
    def run(self):
        self.parent().statusBar().showMessage("Done")  # 错误！
```

### 错误3：在后台线程中使用QTimer

```python
# ❌ 错误
class Worker(QThread):
    def run(self):
        QTimer.singleShot(1000, self.do_something)  # 错误！
```

## 正确的模式

### 模式1：使用信号槽

```python
class Worker(QThread):
    result_ready = pyqtSignal(str)
    
    def run(self):
        result = self.do_work()
        self.result_ready.emit(result)  # ✅ 正确

class MainWindow(QMainWindow):
    def __init__(self):
        self.worker = Worker()
        self.worker.result_ready.connect(self.on_result)  # ✅ 正确
    
    def on_result(self, result):
        self.statusBar().showMessage(result)  # ✅ 在主线程中执行
```

### 模式2：使用QTimer

```python
class Worker(QThread):
    def run(self):
        result = self.do_work()
        # ✅ 使用QTimer确保在主线程中执行
        QTimer.singleShot(0, lambda: self.parent().update_ui(result))
```

## 相关文档

- Qt官方文档：[Thread Support in Qt](https://doc.qt.io/qt-6/threads.html)
- Qt官方文档：[Threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html)
- `docs/app_startup_freeze_fix.md` - 应用启动优化
- `docs/ocr_ui_freeze_fix.md` - OCR识别优化
