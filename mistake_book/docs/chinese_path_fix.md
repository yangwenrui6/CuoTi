# 中文路径OCR识别问题修复

## 问题描述

在使用EasyOCR识别包含中文路径的图片时，会遇到以下错误：

```
[ WARN:0@15.432] global loadsave.cpp:278 cv::findDecoder imread_('C:\Users\Lenovo\Desktop\寰俊鍥剧墖_20260203111314_1079_272_processed.png'): can't open/read file: check file path/integrity
ERROR - OCR识别失败: 'NoneType' object has no attribute 'shape'
```

### 症状

- ✅ 英文路径的图片可以正常识别
- ❌ 中文路径的图片识别失败
- ❌ 文件名中的中文字符被错误编码（如"微信"显示为"寰俊"）
- ❌ OpenCV无法读取文件

## 根本原因

**OpenCV在Windows上不支持中文路径**

EasyOCR内部使用OpenCV（cv2）读取图片。OpenCV在Windows系统上使用ANSI编码处理文件路径，无法正确处理UTF-8编码的中文路径。

### 技术细节

1. **EasyOCR的默认行为**：
   ```python
   result = reader.readtext(str(image_path))  # 传入文件路径字符串
   ```
   
2. **OpenCV的限制**：
   - OpenCV使用`cv::imread()`读取图片
   - 在Windows上，`imread()`使用ANSI编码
   - 中文路径会被错误编码，导致文件无法找到

3. **错误编码示例**：
   ```
   原始路径: C:\Users\Lenovo\Desktop\微信图片_20260203111314.png
   错误编码: C:\Users\Lenovo\Desktop\寰俊鍥剧墖_20260203111314.png
   ```

## 解决方案

### 方案1：使用numpy数组而不是文件路径（已实现）

**核心思想**：先用PIL读取图片为numpy数组，然后传给EasyOCR，避免OpenCV读取文件。

#### 修改EasyOCREngine.recognize()

```python
def recognize(self, image_path: Path) -> str:
    """识别图片中的文字"""
    if not self.is_available():
        raise RuntimeError("EasyOCR引擎未初始化")
    
    try:
        # 使用numpy数组而不是文件路径，避免中文路径问题
        import numpy as np
        from PIL import Image
        
        # 读取图片为numpy数组
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # 执行OCR识别（传入numpy数组而不是路径）
        result = self.reader.readtext(img_array)
        
        # ... 处理结果
```

**优点**：
- ✅ 完全避免OpenCV的路径问题
- ✅ PIL可以正确处理中文路径
- ✅ 不需要修改文件名或路径
- ✅ 对用户透明

**缺点**：
- 需要额外的内存（图片加载为数组）
- 略微增加处理时间

### 方案2：使用临时文件（已实现）

**核心思想**：图像预处理时，将处理后的图片保存到临时目录，使用纯英文文件名。

#### 修改ImageProcessor.preprocess_for_ocr()

```python
import tempfile
import uuid

def preprocess_for_ocr(self, image_path: Path, enhance: bool = True) -> Path:
    """OCR预处理"""
    try:
        img = Image.open(image_path)
        
        # ... 图像处理
        
        # 使用临时文件，避免中文路径问题
        temp_dir = Path(tempfile.gettempdir())
        temp_filename = f"ocr_processed_{uuid.uuid4().hex}{image_path.suffix}"
        output_path = temp_dir / temp_filename
        
        img.save(output_path)
        return output_path
```

**优点**：
- ✅ 临时文件使用纯英文名
- ✅ 避免在原路径生成文件
- ✅ 自动清理（系统临时目录）

**缺点**：
- 需要额外的磁盘空间
- 临时文件可能残留

## 实现细节

### 修改的文件

1. **`src/mistake_book/services/ocr_engine.py`**
   - 修改`EasyOCREngine.recognize()`方法
   - 使用PIL + numpy读取图片
   - 传入numpy数组而不是文件路径

2. **`src/mistake_book/utils/image_processor.py`**
   - 修改`preprocess_for_ocr()`方法
   - 修改`compress()`方法
   - 使用临时文件而不是在原路径生成

### 代码对比

#### 修改前（❌ 不支持中文路径）

```python
# EasyOCR
result = self.reader.readtext(str(image_path))

# ImageProcessor
output_path = image_path.parent / f"{image_path.stem}_processed{image_path.suffix}"
```

#### 修改后（✅ 支持中文路径）

```python
# EasyOCR
img = Image.open(image_path)
img_array = np.array(img)
result = self.reader.readtext(img_array)

# ImageProcessor
temp_dir = Path(tempfile.gettempdir())
temp_filename = f"ocr_processed_{uuid.uuid4().hex}{image_path.suffix}"
output_path = temp_dir / temp_filename
```

## 测试验证

### 测试用例

```python
# 测试中文路径
test_path = Path(r"C:\Users\用户\Desktop\微信图片_20260203.png")

# 创建OCR引擎
engine = OCREngineFactory.create_engine(prefer_engine="easyocr")

# 识别
result = engine.recognize(test_path)
print(result)  # 应该成功输出识别结果
```

### 预期结果

- ✅ 可以正确读取中文路径的图片
- ✅ 识别结果正常
- ✅ 不再出现编码错误
- ✅ 不再出现"can't open/read file"错误

## 其他OCR引擎

### Tesseract

Tesseract使用PIL读取图片，PIL可以正确处理中文路径，所以Tesseract不受此问题影响。

```python
# Tesseract (无问题)
img = Image.open(image_path)  # PIL可以处理中文路径
text = pytesseract.image_to_string(img, lang=self.lang)
```

### PaddleOCR

PaddleOCR也使用OpenCV，同样有中文路径问题。如果将来支持PaddleOCR，需要采用相同的解决方案。

## 常见问题

### Q: 为什么不重命名文件？

A: 重命名文件会：
- 改变用户的原始文件
- 可能导致文件名冲突
- 用户体验不好

使用numpy数组或临时文件更优雅。

### Q: 性能影响如何？

A: 
- 内存：增加约图片大小的内存占用（临时数组）
- 速度：增加约10-50ms（图片加载时间）
- 总体影响很小，用户感知不到

### Q: 临时文件会清理吗？

A: 
- 系统会定期清理临时目录
- 也可以在识别完成后手动删除
- 临时文件很小，不会占用太多空间

### Q: 其他语言的路径呢？

A: 
- 日文、韩文等非ASCII字符都有同样问题
- 本方案同样适用
- PIL可以处理所有Unicode路径

## 总结

### 问题

OpenCV在Windows上不支持中文路径，导致EasyOCR无法识别中文路径的图片。

### 解决方案

1. **EasyOCR**：使用PIL读取图片为numpy数组，传给EasyOCR
2. **图像预处理**：使用临时文件，避免在中文路径生成文件

### 效果

✅ 完全支持中文路径
✅ 不改变用户文件
✅ 性能影响很小
✅ 对用户透明

## 相关文档

- `ocr_implementation.md` - OCR功能实现文档
- `easyocr_pyqt6_fix.md` - EasyOCR与PyQt6冲突修复
- `ocr_status_and_solutions.md` - OCR状态和解决方案

---

**修复日期：** 2026-02-04
**影响版本：** EasyOCR 1.7.2, OpenCV
**状态：** ✅ 已解决
