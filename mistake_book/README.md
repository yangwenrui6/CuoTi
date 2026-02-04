# 错题本 - 智能错题管理系统

基于 PyQt6 和 SQLite 的桌面错题管理应用，支持间隔重复算法、OCR识别、数据导入导出等功能。

## 📖 文档导航

- **[⚡ 快速开始](QUICKSTART.md)** - 5分钟快速部署
- **[📦 部署指南](DEPLOYMENT.md)** - 完整部署文档
- **[👨‍💻 开发指南](docs/dev_setup.md)** - 开发环境搭建
- **[📚 用户手册](docs/user_manual.md)** - 功能使用说明

## ✨ 功能特性

- 📝 **错题录入** - 支持文字、图片，拖拽上传
- 🧠 **智能复习** - SM-2间隔重复算法，科学安排复习
- 🏷️ **标签分类** - 灵活的标签系统，多维度筛选
- 📊 **学习统计** - 可视化学习进度和掌握度
- 📤 **数据导出** - 支持PDF/Excel格式导出
- 🔍 **OCR识别** - 图片文字识别，快速录入
- 🎨 **主题切换** - 亮色/暗色主题，高对比度模式
- ♿ **无障碍** - 字体缩放、键盘快捷键、屏幕阅读器支持

## 🖼️ 界面预览

### 主界面 - 三栏布局
- **左栏**: 科目/标签树形导航
- **中栏**: 错题卡片流（带掌握度色标）
- **右栏**: 筛选面板 + 统计小部件

### 复习模式 - 全屏卡片式
- 答案折叠/展开
- 四档评价：生疏/困难/掌握/熟练
- 键盘快捷键支持（1-4、ESC）

详细界面设计见 [GUI设计文档](docs/gui_design.md)

## 🚀 快速开始

> 💡 **提示**: 完整部署指南请查看 [DEPLOYMENT.md](DEPLOYMENT.md)

### 方法一：一键安装（推荐）

**Windows:**
```cmd
# 1. 克隆项目
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi\mistake_book

# 2. 运行安装脚本
install.bat

# 3. 启动应用
python run.py
```

**macOS/Linux:**
```bash
# 1. 克隆项目
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi/mistake_book

# 2. 运行安装脚本
chmod +x install.sh
./install.sh

# 3. 启动应用
python run.py
```

### 方法二：手动安装

```bash
# 1. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r dependencies/requirements.txt

# 3. 运行应用
python run.py
```

### 启用OCR功能（可选）

```bash
# 安装OCR依赖
pip install easyocr

# 首次使用会自动下载模型（约200MB）
```

详细说明见：[OCR使用指南](docs/OCR使用指南.md)

## 📋 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **内存**: 最低 2GB RAM，推荐 4GB+
- **磁盘空间**: 最低 500MB，推荐 2GB+（包含OCR模型）

核心依赖：PyQt6, SQLAlchemy, platformdirs, Pillow

详细要求见：[部署指南](DEPLOYMENT.md#系统要求)

## 📚 文档

### 部署文档
- **[⚡ 快速开始](QUICKSTART.md)** - 5分钟快速部署 ⭐ 推荐
- **[📦 部署指南](DEPLOYMENT.md)** - 完整部署文档
- **[🔧 常见问题](DEPLOYMENT.md#常见问题)** - 问题排查

### 用户文档
- [用户手册](docs/user_manual.md) - 功能使用说明
- [OCR使用指南](docs/OCR使用指南.md) - OCR功能详解
- [GUI设计](docs/gui_design.md) - 界面设计说明

### 开发文档
- [开发指南](docs/dev_setup.md) - 开发环境搭建
- [架构文档](docs/architecture.md) - 项目架构和设计原则
- [项目结构](PROJECT_STRUCTURE.md) - 完整的目录结构说明
- [数据库设计](docs/database_design.md) - 数据库表结构

### 更新日志
- [CHANGELOG](docs/CHANGELOG.md) - 版本更新记录
- [最近更新](docs/recent_updates_summary.md) - 最新功能
- [最近更新总结](docs/recent_updates_summary.md) - 最新功能和改进 ⭐ 推荐

### 设计文档
- [GUI设计](docs/gui_design.md) - 界面设计说明和交互流程
- [架构文档](docs/architecture.md) - 项目架构和设计原则
- [项目结构](PROJECT_STRUCTURE.md) - 完整的目录结构说明
- [数据库设计](docs/database_design.md) - 数据库表结构和ER图

### 开发文档
- [开发指南](docs/dev_setup.md) - 开发环境搭建
- [文档索引](docs/README.md) - 所有文档的完整索引

## 🎯 核心功能

### 1. SM-2间隔重复算法

基于艾宾浩斯遗忘曲线，智能计算下次复习时间：
- 首次复习：1天后
- 第二次：6天后
- 之后根据掌握度动态调整

### 2. 三栏布局设计

清晰的信息架构，高效的浏览体验：
- 左侧导航快速筛选
- 中间卡片流展示错题
- 右侧统计实时反馈

### 3. 掌握度色标系统

直观的视觉反馈：
- 🔴 红色：生疏
- 🟡 橙色：学习中
- 🟢 绿色：掌握
- 🔵 蓝色：熟练

### 4. 无障碍设计

包容性设计，人人可用：
- 高对比度模式
- 字体缩放（Ctrl +/-）
- 完整的键盘快捷键
- 屏幕阅读器支持

## ⌨️ 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + N` | 添加错题 |
| `Ctrl + R` | 开始复习 |
| `Ctrl + E` | 导出数据 |
| `Ctrl + +` | 放大字体 |
| `Ctrl + -` | 缩小字体 |
| `ESC` | 退出复习模式 |
| `1-4` | 复习结果快捷键 |

## 🏗️ 项目结构

```
mistake_book/
├── src/mistake_book/      # 源代码
│   ├── config/           # 配置管理
│   ├── core/             # 业务逻辑（无GUI依赖）
│   ├── database/         # 数据持久层
│   ├── services/         # 外部服务
│   ├── ui/               # 界面层（MVVM）
│   └── utils/            # 工具函数
├── resources/            # 资源文件
├── tests/                # 测试
├── docs/                 # 文档
└── scripts/              # 辅助脚本
```

详见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🔧 开发

### 代码格式化
```bash
black src/
```

### 编译资源
```bash
python scripts/compile_resources.py
```

### 打包应用
```bash
python scripts/build_exe.py
```

## 🛠️ 技术栈

- **GUI框架**: PyQt6
- **数据库**: SQLite + SQLAlchemy ORM
- **复习算法**: SM-2间隔重复算法
- **路径管理**: platformdirs（跨平台）
- **OCR引擎**: PaddleOCR / Tesseract（可选）
- **测试框架**: pytest
- **打包工具**: PyInstaller

## 📦 可选功能

### OCR识别（可选）
```bash
pip install paddleocr  # 推荐，中文支持好
# 或
pip install pytesseract
```

### 导出功能（可选）
```bash
pip install reportlab openpyxl
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 💡 设计理念

1. **分层架构** - 业务逻辑与UI分离，易于测试和维护
2. **MVVM模式** - 数据绑定，响应式更新
3. **无障碍优先** - 包容性设计，人人可用
4. **科学复习** - 基于认知科学的间隔重复算法

## 📞 支持

- 查看文档：[docs/](docs/)
- 提交问题：GitHub Issues
- 邮件联系：your.email@example.com

---

**开始使用**: `python run.py` 🚀
