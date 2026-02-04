# OCR模型路径修复

## 问题描述

虽然在`main.py`中设置了环境变量`EASYOCR_MODULE_PATH`，但EasyOCR仍然使用默认路径（C盘）下载模型。

## 根本原因

EasyOCR的`Reader`初始化时没有传入`model_storage_directory`参数，导致环境变量被忽略。

## 解决方案

在创建`Reader`时显式传入`model_storage_directory`参数。

### 修改前

```python
self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
```

### 修改后

```python
import os
from pathlib import Path

# 获取模型存储路径（优先使用环境变量）
model_storage_directory = os.environ.get('EASYOCR_MODULE_PATH')
if model_storage_directory:
    # 确保路径存在
    model_path = Path(model_storage_directory)
    model_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"使用自定义模型路径: {model_storage_directory}")
    
    self.reader = easyocr.Reader(
        self.langs, 
        gpu=False, 
        verbose=False,
        model_storage_directory=model_storage_directory
    )
else:
    logger.info("使用默认模型路径")
    self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
```

## 验证

### 1. 检查环境变量

```python
import os
print(os.environ.get('EASYOCR_MODULE_PATH'))
# 应该输出: D:/EasyOCR
```

### 2. 检查模型文件

```bash
dir D:\EasyOCR\model
```

应该看到：
- craft_mlt_25k.pth (83MB) - 检测模型
- zh_sim_g2.pth (21MB) - 中文识别模型

### 3. 运行诊断工具

```bash
python mistake_book/scripts/check_ocr_status.py
```

应该显示：
```
[4] 模型文件
   ℹ️  自定义路径: D:\EasyOCR
   ✅ 模型目录存在: D:\EasyOCR\model
   ✅ 检测模型: craft_mlt_25k.pth (83MB)
   ✅ 中文识别模型: zh_sim_g2.pth (21MB)
```

## 清理旧文件

修复后，可以删除C盘的旧模型文件：

```cmd
rmdir /s /q "%USERPROFILE%\.EasyOCR"
```

## 注意事项

1. **环境变量必须在导入easyocr之前设置**
   - 在`main.py`中已正确设置

2. **路径格式**
   - Windows: `D:/EasyOCR` 或 `D:\\EasyOCR`
   - 推荐使用正斜杠 `/`

3. **权限问题**
   - 确保对目标目录有写权限

## 相关文件

- `mistake_book/src/mistake_book/main.py` - 设置环境变量
- `mistake_book/src/mistake_book/services/ocr_engine.py` - 使用环境变量
- `mistake_book/scripts/check_ocr_status.py` - 诊断工具

---

**修复日期：** 2026-02-04  
**状态：** ✅ 已修复
