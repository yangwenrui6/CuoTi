# 将EasyOCR模型移动到D盘 - 快速指南

## 为什么要移动？

EasyOCR默认将模型保存在C盘：
```
C:\Users\你的用户名\.EasyOCR\model\
```

模型文件约130MB，如果C盘空间不足，可以移到D盘。

## ✅ 已完成的配置

程序已经配置好使用D盘路径，你只需要：

### 方法1：自动移动（推荐）

运行批处理脚本：
```cmd
mistake_book\scripts\move_models_to_d_drive.bat
```

脚本会自动：
1. 检查C盘是否有模型文件
2. 将模型复制到D盘
3. 询问是否删除C盘旧文件

### 方法2：手动移动

如果已经下载过模型，手动移动：

```cmd
# 1. 创建D盘目录
mkdir D:\EasyOCR\model

# 2. 复制模型文件
xcopy "%USERPROFILE%\.EasyOCR\*" "D:\EasyOCR\" /E /I /Y

# 3. 删除C盘旧文件（可选）
rmdir /s /q "%USERPROFILE%\.EasyOCR"
```

### 方法3：首次使用自动下载

如果还没下载过模型，直接启动程序：
```cmd
python mistake_book/run.py
```

拖拽图片时会自动下载到D盘。

## 验证配置

### 1. 启动程序测试

```cmd
python mistake_book/run.py
```

拖拽图片，首次使用会下载模型到D盘。

### 2. 检查D盘目录

下载完成后，检查：
```
D:\EasyOCR\model\
├── craft_mlt_25k.pth      (67MB)
├── zh_sim_g2.pth          (21MB)
└── english_g2.pth         (40MB)
```

### 3. 清理C盘

确认D盘模型可用后，删除C盘旧文件：
```cmd
rmdir /s /q "%USERPROFILE%\.EasyOCR"
```

## 修改路径

如果想使用其他盘（如E盘），修改 `mistake_book/src/mistake_book/main.py`：

```python
# 将EasyOCR模型和PyTorch缓存移到E盘
os.environ['EASYOCR_MODULE_PATH'] = 'E:/EasyOCR'
os.environ['TORCH_HOME'] = 'E:/PyTorch'
```

## 空间占用

- **EasyOCR模型**：约130MB
- **PyTorch缓存**：约100-500MB
- **建议预留**：至少500MB

## 常见问题

### Q: 移动后程序找不到模型？

A: 确认：
1. `main.py` 中的路径配置正确
2. D盘目录存在：`D:\EasyOCR\model\`
3. 模型文件已复制到D盘

### Q: 还是下载到C盘？

A: 可能原因：
1. 使用了旧版本的代码（更新代码）
2. 环境变量被其他程序覆盖
3. 检查 `main.py` 中的配置

### Q: 可以删除C盘旧文件吗？

A: 可以！确认D盘模型可用后，删除C盘旧文件：
```cmd
rmdir /s /q "%USERPROFILE%\.EasyOCR"
```

### Q: PyTorch也占用C盘空间？

A: 是的。PyTorch缓存也在C盘，已配置移到D盘：
```
D:\PyTorch\
```

## 总结

✅ **已完成**：程序已配置使用D盘路径  
✅ **下一步**：运行移动脚本或直接使用程序  
✅ **效果**：节省C盘空间约200-500MB

---

**更新日期：** 2026-02-04  
**配置文件：** `mistake_book/src/mistake_book/main.py`
