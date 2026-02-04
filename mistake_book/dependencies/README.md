# 依赖配置文件

本目录包含项目的所有依赖配置文件。

## 📦 文件说明

### requirements.txt
**基础运行依赖** - 运行应用所需的最小依赖包

包含：
- PyQt6 >= 6.4.0 (GUI框架)
- SQLAlchemy >= 2.0.0 (数据库ORM)
- platformdirs >= 3.0.0 (跨平台路径管理)
- Pillow >= 10.0.0 (图片处理)
- plyer >= 2.1.0 (系统通知)

**安装命令：**
```bash
pip install -r requirements.txt
```

### requirements-dev.txt
**开发依赖** - 开发和打包所需的额外工具

包含：
- black (代码格式化)
- flake8 (代码检查)
- mypy (类型检查)
- PyInstaller (应用打包)

**安装命令：**
```bash
pip install -r requirements-dev.txt
```

### pyproject.toml
**项目配置文件** - 现代化的Python项目配置

包含：
- 项目元数据（名称、版本、作者等）
- 依赖声明
- 构建系统配置
- 工具配置（black等）

## 🚀 快速开始

### 普通用户
只需要安装基础依赖：
```bash
pip install -r requirements.txt
```

### 开发者
安装完整开发环境：
```bash
pip install -r requirements-dev.txt
```

## 📝 可选依赖

### OCR功能
如果需要OCR识别功能，可以安装：

**PaddleOCR（推荐）：**
```bash
pip install paddleocr
```

**Tesseract：**
```bash
pip install pytesseract
```

### 导出功能
如果需要导出PDF/Excel功能：

```bash
pip install reportlab openpyxl
```

## 🔄 更新依赖

### 更新所有包到最新版本
```bash
pip install --upgrade -r requirements.txt
```

### 查看已安装的包
```bash
pip list
```

### 导出当前环境的依赖
```bash
pip freeze > installed_packages.txt
```

## ⚠️ 注意事项

1. **虚拟环境**：建议在虚拟环境中安装依赖
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Python版本**：需要Python 3.9或更高版本

3. **依赖冲突**：如果遇到依赖冲突，尝试：
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

## 📚 相关文档

- [安装指南](../README.md) - 完整的安装说明
- [项目结构](../PROJECT_STRUCTURE.md) - 项目目录结构
