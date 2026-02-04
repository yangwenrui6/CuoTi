# 图片加载中文路径修复

## 问题描述

用户反馈：拖拽图片后显示"无法加载图片"或"无法加载OCR引擎"

## 问题分析

### 根本原因

**QPixmap在Windows上不支持中文路径！**

```python
# 原来的代码
pixmap = QPixmap(path)  # 如果path包含中文，pixmap.isNull() == True
```

当图片路径包含中文字符时（例如：`D:/测试/图片.png` 或 `C:/Users/用户/Documents/image.jpg`），`QPixmap` 无法正确加载图片，返回一个空的 pixmap 对象。

### 问题表现

1. **图片预览失败**
   - 拖拽图片后，预览区域不显示图片
   - 提示"无法加载图片"

2. **OCR识别无法触发**
   - 因为图片加载失败，`current_image_path` 被设为 `None`
   - OCR识别逻辑检测到路径为空，不执行识别
   - 用户看到"无法加载OCR引擎"的提示

3. **用户困惑**
   - 图片文件本身是正常的
   - 只是因为路径包含中文就无法使用
   - 错误提示不够明确

## 解决方案

### 1. 使用PIL加载图片

PIL (Pillow) 库在所有平台上都完美支持中文路径：

```python
from PIL import Image
import numpy as np
from PyQt6.QtGui import QImage, QPixmap

# 使用PIL读取图片
pil_image = Image.open(path)  # 支持中文路径！

# 转换为RGB模式
if pil_image.mode != 'RGB':
    pil_image = pil_image.convert('RGB')

# 转换为numpy数组
img_array = np.array(pil_image)

# 转换为QImage
height, width, channel = img_array.shape
bytes_per_line = 3 * width
q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

# 转换为QPixmap
pixmap = QPixmap.fromImage(q_image)
```

### 2. 增强错误处理

在 `load_image` 方法中添加 try-except：

```python
def load_image(self, path: str):
    """加载图片预览"""
    try:
        self.current_image_path = path
        
        # 使用PIL加载图片，避免QPixmap的中文路径问题
        from PIL import Image
        import numpy as np
        from PyQt6.QtGui import QImage
        
        # ... 加载逻辑 ...
        
        self.label.setText("✅ 图片已加载")
        
    except Exception as e:
        # 图片加载失败
        logger.error(f"图片加载失败: {e}")
        self.label.setText(f"❌ 图片加载失败\n{str(e)}")
        self.current_image_path = None  # 重要：设为None，防止后续OCR尝试
```

### 3. 优化事件处理

确保只有在图片成功加载后才触发OCR：

```python
def on_image_dropped(self, path: str):
    """图片拖拽事件 - 自动触发OCR识别"""
    self.image_path = path
    self.ocr_btn.setEnabled(True)
    
    # 使用QTimer延迟检查，确保load_image已执行完毕
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(200, self._check_and_run_ocr)

def _check_and_run_ocr(self):
    """检查图片是否加载成功，然后运行OCR"""
    if self.drop_zone.current_image_path:
        # 图片加载成功，触发OCR
        self.auto_run_ocr()
    else:
        # 图片加载失败，不触发OCR
        self.ocr_btn.setEnabled(False)
```

### 4. 统一处理所有加载入口

修改 `select_image` 和 `dropEvent` 方法：

```python
def select_image(self):
    """选择图片文件"""
    file_path, _ = QFileDialog.getOpenFileName(...)
    
    if file_path:
        # 先尝试加载图片
        self.load_image(file_path)
        # 只有加载成功才发送信号
        if self.current_image_path:
            self.image_dropped.emit(file_path)

def dropEvent(self, event: QDropEvent):
    """拖拽放下"""
    urls = event.mimeData().urls()
    if urls:
        file_path = urls[0].toLocalFile()
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # 先尝试加载图片
            self.load_image(file_path)
            # 只有加载成功才发送信号
            if self.current_image_path:
                self.image_dropped.emit(file_path)
        else:
            self.label.setText("❌ 不支持的文件格式\n请选择图片文件")
```

## 技术细节

### QPixmap vs PIL

| 特性 | QPixmap | PIL (Pillow) |
|------|---------|--------------|
| 中文路径支持 | ❌ Windows不支持 | ✅ 完美支持 |
| 性能 | 快速 | 稍慢 |
| 依赖 | PyQt6内置 | 需要安装 |
| 用途 | Qt界面显示 | 图像处理 |

### 转换流程

```
PIL Image → numpy array → QImage → QPixmap
```

1. **PIL Image**: 支持中文路径，加载图片
2. **numpy array**: 中间格式，便于处理
3. **QImage**: Qt的图像格式
4. **QPixmap**: Qt的显示格式

### 注意事项

1. **颜色模式转换**
   ```python
   if pil_image.mode != 'RGB':
       pil_image = pil_image.convert('RGB')
   ```
   - PNG可能是RGBA模式（带透明通道）
   - 需要转换为RGB才能正确显示

2. **内存管理**
   ```python
   q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
   ```
   - `img_array.data` 是numpy数组的内存指针
   - 确保numpy数组在QImage使用期间不被释放

3. **字节对齐**
   ```python
   bytes_per_line = 3 * width  # RGB每像素3字节
   ```
   - 正确计算每行字节数
   - 避免图像显示错位

## 测试验证

创建了测试脚本 `tests/test_image_loading.py`：

```bash
python mistake_book/tests/test_image_loading.py
```

测试内容：
1. QPixmap加载中文路径（预期失败）
2. PIL加载中文路径（预期成功）
3. PIL转QPixmap（预期成功）

## 用户体验改进

### 修复前

1. 拖拽包含中文路径的图片
2. 图片预览区域空白
3. 提示"无法加载OCR引擎"（误导性）
4. 用户不知道是什么问题

### 修复后

1. 拖拽包含中文路径的图片
2. 图片正常显示预览
3. 自动触发OCR识别
4. 如果加载失败，显示明确的错误信息

## 相关问题

### OCR识别也有中文路径问题

在 `ocr_engine.py` 中，我们已经使用PIL解决了这个问题：

```python
def recognize(self, image_path: Path) -> str:
    # 使用numpy数组而不是文件路径，避免中文路径问题
    import numpy as np
    from PIL import Image
    
    # 读取图片为numpy数组
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # 执行OCR识别（传入numpy数组而不是路径）
    result = self.reader.readtext(img_array)
```

这样OCR引擎也能正确处理中文路径的图片。

## 相关文件

- `src/mistake_book/ui/dialogs/add_dialog.py` - 添加对话框（图片加载）
- `src/mistake_book/services/ocr_engine.py` - OCR引擎（识别中文路径图片）
- `tests/test_image_loading.py` - 图片加载测试脚本
- `docs/chinese_path_fix.md` - OCR中文路径修复文档

## 最佳实践

### 在PyQt6中处理中文路径

1. **文件读取**: 使用Python标准库或PIL，不要直接用Qt的文件API
2. **图片加载**: 使用PIL加载后转换为QPixmap
3. **文件对话框**: QFileDialog返回的路径可以直接用于Python标准库

### 跨平台兼容性

```python
# ✅ 推荐：使用pathlib
from pathlib import Path
path = Path(file_path)

# ✅ 推荐：使用PIL
from PIL import Image
img = Image.open(path)

# ❌ 避免：直接用QPixmap加载可能包含中文的路径
pixmap = QPixmap(str(path))  # Windows上可能失败
```

## 总结

本次修复解决了图片加载中文路径的问题：

1. ✅ 使用PIL替代QPixmap加载图片
2. ✅ 增强错误处理和用户提示
3. ✅ 确保只有加载成功才触发OCR
4. ✅ 统一处理所有加载入口
5. ✅ 提供清晰的错误信息

用户现在可以正常使用包含中文路径的图片进行OCR识别了！
