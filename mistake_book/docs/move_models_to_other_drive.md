# 将EasyOCR模型移到其他盘

## 问题

EasyOCR默认将模型文件保存在C盘用户目录：
```
C:\Users\你的用户名\.EasyOCR\model\
```

模型文件约100-200MB，如果C盘空间不足，可以将模型移到其他盘。

## 解决方案

### 方案1：设置环境变量（推荐）

EasyOCR支持通过环境变量 `EASYOCR_MODULE_PATH` 自定义模型存储位置。

#### 步骤1：创建新的模型目录

在其他盘创建目录，例如：
```
D:\EasyOCR\model\
```

#### 步骤2：移动现有模型文件（如果有）

如果已经下载过模型，可以移动过去：
```cmd
# 创建目标目录
mkdir D:\EasyOCR\model

# 移动模型文件
move C:\Users\你的用户名\.EasyOCR\model\*.pth D:\EasyOCR\model\
```

#### 步骤3：设置环境变量

**方法A：永久设置（推荐）**

1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"用户变量"中点击"新建"
5. 变量名：`EASYOCR_MODULE_PATH`
6. 变量值：`D:\EasyOCR`
7. 点击"确定"保存

**方法B：临时设置（仅当前会话）**

在运行程序前设置：
```cmd
set EASYOCR_MODULE_PATH=D:\EasyOCR
python mistake_book/run.py
```

**方法C：在代码中设置**

修改 `mistake_book/src/mistake_book/main.py`，在导入torch之前添加：
```python
import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
```

#### 步骤4：验证

运行诊断工具：
```bash
python mistake_book/scripts/check_ocr_status.py
```

应该显示新的模型目录：
```
[4] 模型文件
   ✅ 模型目录存在: D:\EasyOCR\model
```

### 方案2：修改OCR引擎代码

直接在代码中指定模型路径。

修改 `mistake_book/src/mistake_book/services/ocr_engine.py`：

```python
def _lazy_init(self):
    """延迟初始化 - 只在第一次使用时才加载模型"""
    if self._init_attempted:
        return
    
    self._init_attempted = True
    
    try:
        import easyocr
        
        # 自定义模型路径
        model_storage_directory = 'D:/EasyOCR/model'
        
        logger.info("正在初始化EasyOCR...")
        logger.info(f"模型存储路径: {model_storage_directory}")
        
        self.reader = easyocr.Reader(
            self.langs, 
            gpu=False, 
            verbose=False,
            model_storage_directory=model_storage_directory  # 指定模型路径
        )
        self._initialized = True
        logger.info(f"✅ EasyOCR初始化成功 (语言: {self.langs})")
    except Exception as e:
        logger.error(f"❌ EasyOCR初始化失败: {e}")
```

## PyTorch缓存

PyTorch也会在C盘缓存一些文件，可以通过环境变量修改：

### 设置PyTorch缓存目录

**永久设置：**

1. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
2. 新建用户变量：
   - 变量名：`TORCH_HOME`
   - 变量值：`D:\PyTorch`

**临时设置：**
```cmd
set TORCH_HOME=D:\PyTorch
```

**在代码中设置：**

在 `mistake_book/src/mistake_book/main.py` 中添加：
```python
import os
os.environ['TORCH_HOME'] = 'D:/PyTorch'
```

## 完整配置示例

### 修改 main.py（推荐）

```python
"""应用程序入口"""

import sys
import os

# ===== 配置模型存储路径（在导入任何库之前） =====
# 将EasyOCR模型移到D盘
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
# 将PyTorch缓存移到D盘
os.environ['TORCH_HOME'] = 'D:/PyTorch'

# ===== 重要：先导入torch，避免与PyQt6的DLL冲突 =====
try:
    import torch
except ImportError:
    pass

# 然后才导入PyQt6
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# ... 其余代码
```

## 验证配置

### 1. 检查环境变量

```cmd
echo %EASYOCR_MODULE_PATH%
echo %TORCH_HOME%
```

应该显示：
```
D:\EasyOCR
D:\PyTorch
```

### 2. 运行诊断工具

```bash
python mistake_book/scripts/check_ocr_status.py
```

### 3. 测试OCR功能

启动程序并拖拽图片测试OCR识别。

## 空间占用

### EasyOCR模型文件

- 检测模型：`craft_mlt_25k.pth` - 约67MB
- 中文识别：`zh_sim_g2.pth` - 约21MB
- 英文识别：`english_g2.pth` - 约40MB
- **总计**：约130MB

### PyTorch缓存

- 根据使用情况，可能占用几百MB

### 建议

- 至少预留500MB空间
- 定期清理不需要的模型文件

## 清理C盘旧文件

配置完成后，可以删除C盘的旧文件：

```cmd
# 删除EasyOCR旧模型
rmdir /s /q "%USERPROFILE%\.EasyOCR"

# 删除PyTorch旧缓存（可选）
rmdir /s /q "%USERPROFILE%\.cache\torch"
```

## 常见问题

### Q1: 设置环境变量后不生效？

A: 需要重启命令行或IDE，或者重启电脑。

### Q2: 模型还是下载到C盘？

A: 检查：
1. 环境变量是否正确设置
2. 是否重启了命令行
3. 是否在代码中设置了环境变量

### Q3: 如何确认模型路径？

A: 在代码中添加日志：
```python
import os
print(f"EASYOCR_MODULE_PATH: {os.environ.get('EASYOCR_MODULE_PATH', '未设置')}")
```

### Q4: 可以使用网络路径吗？

A: 不建议。网络路径可能导致性能问题和权限问题。

## 推荐配置

### 最简单的方法

修改 `mistake_book/src/mistake_book/main.py`，在文件开头添加：

```python
import os

# 配置模型存储路径（根据你的实际情况修改）
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
os.environ['TORCH_HOME'] = 'D:/PyTorch'
```

这样不需要手动设置系统环境变量，程序会自动使用指定路径。

## 总结

- ✅ **推荐方案**：在 `main.py` 中设置环境变量
- ✅ **优点**：简单、不需要修改系统设置、便于分发
- ✅ **效果**：模型和缓存都保存在D盘，节省C盘空间

---

**文档版本：** 1.0  
**更新日期：** 2026-02-04  
**适用版本：** EasyOCR 1.7.2+, PyTorch 2.10.0+
