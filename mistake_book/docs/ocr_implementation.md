# OCR功能实现文档

## 修改日期
2026-02-03

## 功能概述
实现了完整的OCR(光学字符识别)功能,支持从图片中自动识别文字,大幅提升错题录入效率。

## 架构设计

### 1. 分层架构

```
UI层 (AddQuestionDialog)
    ↓
服务层 (QuestionService)
    ↓
OCR引擎层 (OCREngine接口)
    ↓
具体实现 (PaddleOCR / Tesseract)
```

### 2. 核心组件

#### OCREngine (抽象基类)
- 定义OCR引擎接口
- `recognize()`: 识别图片文字
- `is_available()`: 检查引擎是否可用

#### PaddleOCREngine (推荐)
- 基于百度PaddleOCR
- 中文识别准确率高
- 支持角度分类和倾斜校正
- 可离线使用

#### TesseractEngine (备选)
- 基于Google Tesseract
- 完全开源免费
- 需要单独安装程序

#### OCREngineFactory (工厂类)
- 自动选择可用的OCR引擎
- 支持优先级配置
- 优雅降级机制

## 功能特性

### 1. 图像预处理 (ImageProcessor)

**基础处理:**
- 灰度化: 减少颜色干扰
- 对比度增强: 提高文字清晰度
- 锐化: 增强边缘
- 去噪: 去除图片噪点

**高级处理:**
- 自动旋转: 根据EXIF信息
- 智能裁剪: 去除白边
- 图片压缩: 减小文件大小

### 2. 识别策略

**重试机制:**
1. 第一次尝试: 使用预处理
2. 第二次尝试: 不预处理(原图识别)
3. 提高识别成功率

**置信度过滤:**
- 只保留置信度 > 0.5 的结果
- 减少误识别

### 3. 用户体验

**拖拽上传:**
- 支持拖拽图片到指定区域
- 自动显示图片预览
- 支持多种格式(PNG, JPG, JPEG, BMP)

**OCR按钮:**
- 拖入图片后自动启用
- 点击后显示"识别中..."
- 识别完成显示结果统计

**错误处理:**
- 友好的错误提示
- 提供安装指南
- 给出改进建议

## 使用流程

### 用户操作流程
1. 打开"添加错题"对话框
2. 拖拽题目图片到上传区域
3. 点击"🔍 OCR识别"按钮
4. 等待识别完成(显示"识别中...")
5. 识别结果自动填充到"题目内容"
6. 用户可以手动编辑识别结果
7. 点击"保存"保存错题

### 技术流程
1. `AddQuestionDialog.on_image_dropped()` - 接收图片
2. `AddQuestionDialog.run_ocr()` - 触发识别
3. `QuestionService.recognize_image_with_retry()` - 服务层处理
4. `ImageProcessor.preprocess_for_ocr()` - 图像预处理
5. `OCREngine.recognize()` - 执行识别
6. 返回识别结果到UI层

## 安装配置

### 方式1: PaddleOCR (推荐)

**安装:**
```bash
pip install paddleocr paddlepaddle
```

**优点:**
- 中文识别准确率高
- 支持倾斜校正
- 可离线使用
- 首次使用自动下载模型

**注意:**
- 首次使用需要网络下载模型(约8MB)
- 模型会缓存到本地

### 方式2: Tesseract

**安装Python包:**
```bash
pip install pytesseract
```

**安装Tesseract程序:**
- Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- Mac: `brew install tesseract tesseract-lang`

**优点:**
- 完全开源免费
- 支持多语言

**缺点:**
- 中文识别不如PaddleOCR
- 需要单独安装程序

### 无OCR依赖
如果不安装OCR依赖:
- 程序正常运行
- OCR按钮显示但不可用
- 点击时提示安装依赖
- 可以手动输入题目内容

## 代码示例

### 初始化OCR引擎
```python
from mistake_book.services.ocr_engine import OCREngineFactory

# 自动选择可用引擎(优先PaddleOCR)
ocr_engine = OCREngineFactory.create_engine(prefer_engine="paddleocr")

if ocr_engine:
    print("OCR引擎初始化成功")
else:
    print("OCR引擎不可用")
```

### 使用OCR识别
```python
from pathlib import Path

# 通过QuestionService使用
success, message, text = question_service.recognize_image_with_retry(
    Path("question.jpg")
)

if success:
    print(f"识别成功: {text}")
else:
    print(f"识别失败: {message}")
```

### 图像预处理
```python
from mistake_book.utils.image_processor import ImageProcessor

processor = ImageProcessor()

# 预处理图片
processed_path = processor.preprocess_for_ocr(
    Path("question.jpg"),
    enhance=True
)

# 压缩图片
compressed_path = processor.compress(
    Path("question.jpg"),
    max_size=1024,
    quality=85
)
```

## 性能优化

### 1. 延迟加载
- OCR引擎只在需要时初始化
- 减少程序启动时间
- 降低内存占用

### 2. 临时文件清理
- 预处理后的图片自动删除
- 避免磁盘空间浪费

### 3. 日志记录
- 记录识别过程
- 便于调试和优化

## 错误处理

### 1. OCR引擎不可用
```
OCR功能未启用

请安装依赖:
pip install paddleocr

或者:
pip install pytesseract
```

### 2. 识别失败
```
未能识别出文字

建议:
1. 确保图片清晰
2. 文字对比度足够
3. 尝试重新拍照
```

### 3. 引擎错误
```
OCR识别失败

错误信息:
[具体错误信息]
```

## 扩展功能

### 未来可以添加:

1. **异步识别**
   - 使用QThread后台识别
   - 不阻塞UI界面
   - 显示进度条

2. **批量识别**
   - 一次拖入多张图片
   - 自动识别所有图片
   - 合并识别结果

3. **智能分段**
   - 自动识别题目、答案、解析
   - 使用关键词分割
   - 自动填充到对应字段

4. **数学公式识别**
   - 集成LaTeX OCR
   - 识别数学符号
   - 转换为可编辑格式

5. **手写识别**
   - 支持手写题目
   - 训练自定义模型
   - 提高手写准确率

6. **云端OCR**
   - 集成百度/腾讯/阿里云API
   - 更高识别准确率
   - 需要API密钥

## 相关文件

### 核心文件
- `src/mistake_book/services/ocr_engine.py` - OCR引擎实现
- `src/mistake_book/services/question_service.py` - 服务层集成
- `src/mistake_book/utils/image_processor.py` - 图像预处理
- `src/mistake_book/ui/dialogs/add_dialog.py` - UI集成

### 配置文件
- `dependencies/requirements.txt` - 依赖声明

### 文档
- `docs/ocr_implementation.md` - 本文档

## 测试建议

### 测试场景

1. **清晰打印文字**
   - 预期: 识别准确率 > 95%

2. **手写文字**
   - 预期: 识别准确率 > 70%

3. **倾斜图片**
   - 预期: 自动校正后识别

4. **低对比度图片**
   - 预期: 预处理后识别

5. **无OCR依赖**
   - 预期: 友好提示,不崩溃

### 性能测试

- 单张图片识别时间: < 3秒
- 内存占用: < 500MB
- 首次启动时间: < 2秒(延迟加载)

## 常见问题

### Q: 为什么识别不准确?
A: 
1. 确保图片清晰,文字对比度高
2. 避免图片倾斜或模糊
3. 尝试重新拍照
4. 使用PaddleOCR而不是Tesseract

### Q: 首次使用很慢?
A: PaddleOCR首次使用需要下载模型(约8MB),之后会缓存到本地

### Q: 如何切换OCR引擎?
A: 修改 `main_window.py` 中的 `prefer_engine` 参数:
```python
ocr_engine = OCREngineFactory.create_engine(prefer_engine="tesseract")
```

### Q: 可以不安装OCR吗?
A: 可以,程序会正常运行,只是OCR功能不可用,需要手动输入题目内容

## 总结

OCR功能的实现遵循了项目的分层架构:
- UI层只负责交互
- 服务层处理业务逻辑
- 工具层提供图像处理
- 引擎层封装OCR实现

通过工厂模式和抽象接口,实现了:
- 多引擎支持
- 优雅降级
- 易于扩展

用户体验方面:
- 操作简单(拖拽+点击)
- 反馈及时(进度提示)
- 错误友好(详细说明)
