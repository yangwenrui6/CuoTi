# 脚本工具说明

## 资源编译

### compile_resources.py
编译Qt资源文件（.ui和.qrc）为Python代码。

**用途**：
- 将Qt Designer设计的.ui文件编译为.py文件
- 将.qrc资源文件编译为Python模块

**运行**：
```bash
python mistake_book/scripts/compile_resources.py
```

## 应用打包

### build_exe.py
使用PyInstaller打包应用为可执行文件。

**用途**：
- 将Python应用打包为Windows/Linux/macOS可执行文件
- 包含所有依赖和资源

**运行**：
```bash
python mistake_book/scripts/build_exe.py
```

## OCR诊断

### check_ocr_status.py
OCR状态诊断工具，快速检查OCR功能是否正常。

**用途**：
- 检查Python和依赖版本
- 检查EasyOCR是否已安装
- 检查模型文件是否完整
- 检查磁盘空间是否充足
- 测试OCR引擎是否可用

**运行**：
```bash
python mistake_book/scripts/check_ocr_status.py
```

**输出示例**：
```
============================================================
OCR状态检查工具
============================================================

[1] Python版本
   版本: 3.14.0
   路径: E:\Python\python.exe

[2] PyTorch
   ✅ 已安装: 2.10.0+cpu

[3] EasyOCR
   ✅ 已安装: 1.7.2

[4] 模型文件
   ✅ 模型目录存在: C:\Users\用户名\.EasyOCR\model
   ✅ 检测模型: craft_mlt_25k.pth (67MB)
   ✅ 中文识别模型: zh_sim_g2.pth (21MB)
   ✅ 英文识别模型: english_g2.pth (40MB)

[5] 磁盘空间
   可用空间: 40.4GB
   ✅ 磁盘空间充足

[6] OCR引擎测试
   ✅ OCR引擎创建成功
   类型: EasyOCREngine
   可用: True
   已初始化: False
   说明：模型将在首次使用时加载（延迟加载）

============================================================
诊断总结
============================================================

如果所有检查都通过（✅），说明OCR功能可以正常使用。
```

**常见问题诊断**：

1. **模型未下载**
   ```
   ❌ 检测模型: craft_mlt_25k.pth (未下载)
   ```
   解决：首次使用时会自动下载

2. **临时文件存在**
   ```
   ⚠️  发现临时文件（可能是下载中断）:
      temp.zip (64.5MB)
   ```
   解决：删除临时文件后重新下载
   ```bash
   del "%USERPROFILE%\.EasyOCR\model\temp.zip"
   ```

3. **磁盘空间不足**
   ```
   ⚠️  磁盘空间不足，建议至少保留500MB
   ```
   解决：清理磁盘空间

4. **依赖未安装**
   ```
   ❌ EasyOCR: 未安装
   ```
   解决：安装依赖
   ```bash
   pip install easyocr
   ```

## 数据库迁移

### migrate_v1_to_v2.py
数据库版本升级迁移脚本（待实现）。

**用途**：
- 在应用版本升级时迁移数据库结构
- 保留用户数据

## 使用建议

1. **开发阶段**：
   - 修改.ui文件后运行`compile_resources.py`
   - 遇到OCR问题时运行`check_ocr_status.py`

2. **发布阶段**：
   - 运行`build_exe.py`打包应用
   - 测试打包后的可执行文件

3. **故障排查**：
   - 首先运行`check_ocr_status.py`诊断问题
   - 查看详细文档：`mistake_book/docs/ocr_status_and_solutions.md`

## 相关文档

- [OCR使用指南](../docs/OCR使用指南.md)
- [OCR快速入门](../docs/ocr_quick_start.md)
- [OCR状态诊断与解决方案](../docs/ocr_status_and_solutions.md)
- [开发环境搭建](../docs/dev_setup.md)
