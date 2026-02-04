# EasyOCR与PyQt6的DLL冲突问题修复

## 问题描述

在PyQt6应用程序中使用EasyOCR时，会遇到以下错误：

```
[WinError 1114] 动态链接库(DLL)初始化例程失败。
Error loading "E:\Python\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

### 症状

- ✅ 在命令行直接运行Python脚本时，EasyOCR可以正常工作
- ❌ 在PyQt6应用程序中，EasyOCR初始化失败
- ❌ 错误发生在torch库的DLL加载阶段

## 根本原因

**PyQt6和torch的DLL加载顺序冲突**

当PyQt6应用（QApplication）先创建后，再导入torch库时，会导致torch的DLL（c10.dll等）无法正确初始化。这是因为：

1. PyQt6在创建QApplication时会加载自己的DLL
2. 这些DLL可能与torch的DLL有依赖冲突
3. 如果torch在PyQt6之后加载，DLL初始化会失败

## 解决方案

### 核心原则

**在创建PyQt6应用之前先导入torch**

### 实现步骤

#### 1. 修改main.py

在导入PyQt6之前先导入torch：

```python
"""QApplication入口 + 全局异常捕获"""

import sys

# 重要：在导入PyQt6之前先导入torch
# 这可以避免PyQt6和torch的DLL冲突问题
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
except Exception:
    _TORCH_AVAILABLE = False

# 然后再导入PyQt6
from PyQt6.QtWidgets import QApplication
from mistake_book.ui.main_window import MainWindow
from mistake_book.utils.logger import setup_logger

logger = setup_logger()

# ... 其余代码
```

#### 2. 修改EasyOCREngine

在EasyOCR初始化时设置`verbose=False`，避免日志冲突：

```python
class EasyOCREngine(OCREngine):
    def __init__(self, langs: list = None):
        self.langs = langs or ['ch_sim', 'en']
        self.reader = None
        self._initialized = False
        
        try:
            import easyocr
            # 设置verbose=False避免日志冲突
            self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
            self._initialized = True
            logger.info(f"EasyOCR初始化成功 (语言: {self.langs})")
        except Exception as e:
            logger.error(f"EasyOCR初始化失败: {e}")
```

## 验证修复

### 测试脚本

```python
import sys

# 1. 先导入torch
import torch
print(f"torch版本: {torch.__version__}")

# 2. 再导入PyQt6
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)
print("PyQt6应用创建成功")

# 3. 然后导入EasyOCR
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
print("EasyOCR初始化成功")
```

### 预期输出

```
torch版本: 2.10.0+cpu
PyQt6应用创建成功
EasyOCR初始化成功
```

## 技术细节

### DLL加载顺序

1. **正确顺序**（✅ 可以工作）：
   ```
   torch导入 → torch DLL加载 → PyQt6导入 → PyQt6 DLL加载 → EasyOCR初始化
   ```

2. **错误顺序**（❌ 会失败）：
   ```
   PyQt6导入 → PyQt6 DLL加载 → torch导入 → torch DLL加载失败
   ```

### 为什么会冲突？

- PyQt6和torch都依赖一些系统DLL（如MSVC运行库）
- PyQt6先加载时，可能会锁定某些DLL版本
- torch后续尝试加载不同版本的DLL时会失败
- 先加载torch可以确保torch的DLL优先级更高

## 其他注意事项

### 1. verbose=False参数

EasyOCR的`verbose`参数控制日志输出。在应用程序中设置为`False`可以：
- 避免与应用程序的日志系统冲突
- 减少控制台输出
- 提高初始化速度

### 2. GPU参数

```python
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
```

- `gpu=False`：使用CPU模式，不需要CUDA
- 适合没有NVIDIA GPU的环境
- CPU模式速度较慢但更兼容

### 3. 语言包

```python
langs = ['ch_sim', 'en']  # 简体中文 + 英文
```

- `ch_sim`：简体中文
- `en`：英文
- 可以根据需要添加其他语言

## 相关问题

### Q: 为什么命令行可以用，程序中不行？

A: 命令行脚本通常不使用PyQt6，所以没有DLL冲突。程序中使用PyQt6后，必须注意导入顺序。

### Q: 可以在程序运行中动态导入torch吗？

A: 不推荐。最好在程序启动时就导入torch，确保DLL正确加载。

### Q: 其他GUI框架（如Tkinter）也有这个问题吗？

A: 可能有，但PyQt6的问题更明显。建议都采用"先导入torch"的策略。

### Q: 如果不想用EasyOCR怎么办？

A: 可以使用Tesseract，它不依赖torch，没有这个问题。参见 `tesseract_installation_guide.md`。

## 总结

### 问题

PyQt6和torch的DLL加载顺序冲突导致EasyOCR初始化失败。

### 解决方案

在`main.py`中，在导入PyQt6之前先导入torch。

### 效果

✅ EasyOCR可以在PyQt6应用程序中正常工作
✅ OCR功能完全可用
✅ 不需要安装额外的软件

## 相关文档

- `ocr_implementation.md` - OCR功能实现文档
- `ocr_status_and_solutions.md` - OCR状态和解决方案
- `tesseract_installation_guide.md` - Tesseract安装指南（备选方案）

---

**修复日期：** 2026-02-04
**影响版本：** Python 3.14, PyQt6, torch 2.10.0, EasyOCR 1.7.2
**状态：** ✅ 已解决
