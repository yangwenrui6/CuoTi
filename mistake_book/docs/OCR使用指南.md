# OCR功能使用指南

## 快速开始

### 1. 启动程序

```bash
python mistake_book/run.py
```

程序会快速启动（约1秒），日志显示：
```
✅ OCR引擎已准备就绪（将在首次使用时加载模型）
```

### 2. 使用OCR识别

1. 点击"添加错题"按钮
2. 拖拽图片到上传区域，或点击"选择图片"按钮
3. 等待OCR自动识别（首次使用需要5-10秒或更长）
4. 识别结果会自动填充到"题目内容"

### 3. 首次使用注意

**首次使用时**，如果模型文件还没下载，会自动从网络下载：
- 下载大小：约100-200MB
- 下载时间：2-5分钟（取决于网络速度）
- 只需下载一次，后续使用不需要重新下载

**请确保**：
- 网络连接稳定
- 不要在下载过程中关闭程序
- 耐心等待下载完成

## 常见问题

### Q: 为什么首次使用要等很久？

A: 首次使用时需要：
1. 下载模型文件（如果还没下载）：2-5分钟
2. 加载模型到内存：5-10秒

后续使用会很快（1-2秒）。

### Q: 如何确认OCR功能可用？

A: 运行诊断工具：
```bash
python check_ocr_status.py
```

如果显示"✅ OCR引擎创建成功"，说明可用。

### Q: 识别失败怎么办？

A: 常见原因和解决方案：

1. **网络问题** - 检查网络连接，或手动下载模型
2. **模型未下载** - 首次使用时会自动下载
3. **模型损坏** - 删除 `C:\Users\你的用户名\.EasyOCR` 目录后重试

详细解决方案请查看：`mistake_book/docs/ocr_status_and_solutions.md`

## 手动下载模型（可选）

如果网络不稳定，可以手动下载模型：

1. 下载文件：
   - 检测模型：https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.zip
   - 中文识别：https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/zh_sim_g2.zip

2. 解压到：
   - **默认路径**：`C:\Users\你的用户名\.EasyOCR\model\`
   - **D盘路径**：`D:\EasyOCR\model\`（程序已配置使用D盘）

3. 重新启动程序

## 💾 节省C盘空间

程序已配置将模型保存到D盘，节省C盘空间。

### 模型存储位置

- **默认**：`C:\Users\你的用户名\.EasyOCR\` (约130MB)
- **已配置**：`D:\EasyOCR\` (约130MB)

### 如何移动现有模型

如果已经下载过模型到C盘，可以移动到D盘：

**方法1：运行移动脚本**
```bash
mistake_book\scripts\move_models_to_d_drive.bat
```

**方法2：手动移动**
```cmd
# 复制到D盘
xcopy "%USERPROFILE%\.EasyOCR\*" "D:\EasyOCR\" /E /I /Y

# 删除C盘旧文件
rmdir /s /q "%USERPROFILE%\.EasyOCR"
```

详细说明：[移动模型到D盘说明.md](../移动模型到D盘说明.md)

## 诊断工具

### 检查OCR状态

```bash
python check_ocr_status.py
```

会检查：
- Python和依赖版本
- 模型文件是否完整
- 磁盘空间是否充足
- OCR引擎是否可用

### 测试延迟加载

```bash
python test_lazy_loading.py
```

验证延迟加载是否正常工作。

## 详细文档

- [OCR功能快速入门](mistake_book/docs/ocr_quick_start.md) - 详细使用指南
- [OCR状态诊断与解决方案](mistake_book/docs/ocr_status_and_solutions.md) - 问题排查
- [OCR延迟加载优化](mistake_book/docs/ocr_lazy_loading.md) - 技术实现

## 性能提升

- **启动速度**：从6-11秒降低到0.6秒（提升10-18倍）
- **内存占用**：不使用OCR时不占用内存（节省1-2GB）
- **首次使用**：需要等待模型加载（5-10秒）
- **后续使用**：识别速度快（1-2秒）

---

**版本：** 1.0  
**更新日期：** 2026-02-04
