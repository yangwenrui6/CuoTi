# 错题本 - 部署指南

## 📋 目录
- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [开发者指南](#开发者指南)

---

## 🚀 快速开始

### 方法一：一键安装（推荐）

#### Windows用户
1. 双击运行 `install.bat`
2. 等待安装完成
3. 运行 `run.py` 启动应用

#### macOS/Linux用户
```bash
chmod +x install.sh
./install.sh
python run.py
```

### 方法二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi/mistake_book

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows激活
venv\Scripts\activate

# macOS/Linux激活
source venv/bin/activate

# 3. 安装依赖
pip install -r dependencies/requirements.txt

# 4. 运行应用
python run.py
```

---

## 💻 系统要求

### 基础要求
- **Python**: 3.9 或更高版本
- **操作系统**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **内存**: 最低 2GB RAM，推荐 4GB+
- **磁盘空间**: 最低 500MB，推荐 2GB+（包含OCR模型）

### Python依赖
核心依赖（自动安装）：
- PyQt6 >= 6.4.0
- SQLAlchemy >= 2.0.0
- Pillow >= 9.0.0
- platformdirs >= 3.0.0

OCR功能（可选）：
- easyocr >= 1.6.0
- torch >= 2.0.0
- torchvision >= 0.15.0

---

## 📦 安装步骤

### 步骤1：安装Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.9+安装包
3. 安装时勾选 "Add Python to PATH"
4. 验证安装：
   ```cmd
   python --version
   ```

#### macOS
```bash
# 使用Homebrew
brew install python@3.9

# 验证安装
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.9 python3-pip python3-venv

# 验证安装
python3 --version
```

### 步骤2：获取项目

#### 方式A：从GitHub克隆（推荐）
```bash
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi/mistake_book
```

#### 方式B：下载ZIP包
1. 访问 https://github.com/yangwenrui6/CuoTi
2. 点击 "Code" -> "Download ZIP"
3. 解压到本地目录
4. 进入 `mistake_book` 文件夹

### 步骤3：创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# 验证虚拟环境
which python  # macOS/Linux
where python  # Windows
```

### 步骤4：安装依赖

```bash
# 安装基础依赖
pip install -r dependencies/requirements.txt

# 如果需要OCR功能（可选）
pip install easyocr torch torchvision

# 验证安装
pip list
```

### 步骤5：运行应用

```bash
# 方式1：使用run.py
python run.py

# 方式2：作为模块运行
python -m mistake_book

# 方式3：直接运行主文件
python src/mistake_book/main.py
```

---

## ⚙️ 配置说明

### OCR模型配置

#### 默认配置
OCR模型默认保存在用户目录：
- Windows: `C:\Users\<用户名>\.EasyOCR\`
- macOS: `~/.EasyOCR/`
- Linux: `~/.EasyOCR/`

#### 自定义模型路径
如果C盘空间不足，可以配置到其他盘符：

**Windows:**
```cmd
# 方式1：使用脚本（推荐）
scripts\move_models_to_d_drive.bat

# 方式2：手动设置环境变量
setx EASYOCR_MODULE_PATH "D:\EasyOCR"
```

**macOS/Linux:**
```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
export EASYOCR_MODULE_PATH="/path/to/models"

# 重新加载配置
source ~/.bashrc
```

详细说明见：[移动模型到D盘说明](docs/移动模型到D盘说明.md)

### 数据库配置

数据库文件自动创建在：
- Windows: `C:\Users\<用户名>\AppData\Local\mistake_book\`
- macOS: `~/Library/Application Support/mistake_book/`
- Linux: `~/.local/share/mistake_book/`

### 日志配置

日志文件位置：
- Windows: `C:\Users\<用户名>\AppData\Local\mistake_book\logs\`
- macOS: `~/Library/Logs/mistake_book/`
- Linux: `~/.local/share/mistake_book/logs/`

---

## 🔧 常见问题

### 1. 安装依赖失败

**问题**: `pip install` 报错

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r dependencies/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果还是失败，逐个安装
pip install PyQt6
pip install SQLAlchemy
pip install Pillow
pip install platformdirs
```

### 2. OCR功能不可用

**问题**: 拖拽图片后没有识别文字

**解决方案**:
```bash
# 1. 检查OCR状态
python scripts/check_ocr_status.py

# 2. 安装EasyOCR
pip install easyocr

# 3. 首次使用会自动下载模型（约200MB）
# 请耐心等待，可以查看日志了解进度
```

详细说明见：[OCR使用指南](docs/OCR使用指南.md)

### 3. 启动报错：ModuleNotFoundError

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 确认虚拟环境已激活
# 重新安装依赖
pip install -r dependencies/requirements.txt

# 检查Python路径
python -c "import sys; print(sys.executable)"
```

### 4. 中文路径问题

**问题**: 图片路径包含中文时无法加载

**解决方案**:
- 已修复，支持中文路径
- 如果仍有问题，请更新到最新版本

### 5. Windows Defender误报

**问题**: 安装时被Windows Defender拦截

**解决方案**:
1. 这是正常现象，项目是开源的，代码可审查
2. 添加信任：Windows安全中心 -> 病毒和威胁防护 -> 管理设置 -> 添加排除项
3. 或者使用虚拟环境安装

### 6. 数据库锁定错误

**问题**: `database is locked`

**解决方案**:
```bash
# 关闭所有应用实例
# 删除锁文件
# Windows:
del %LOCALAPPDATA%\mistake_book\*.db-journal

# macOS/Linux:
rm ~/Library/Application\ Support/mistake_book/*.db-journal
```

---

## 👨‍💻 开发者指南

### 开发环境搭建

```bash
# 1. 克隆项目
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi/mistake_book

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3. 安装开发依赖
pip install -r dependencies/requirements.txt
pip install -r dependencies/requirements-dev.txt

# 4. 运行测试
pytest tests/

# 5. 代码格式化
black src/

# 6. 代码检查
flake8 src/
```

### 项目结构

```
mistake_book/
├── src/mistake_book/      # 源代码
│   ├── config/           # 配置管理
│   ├── core/             # 业务逻辑
│   ├── database/         # 数据库层
│   ├── services/         # 服务层
│   ├── ui/               # 界面层（UI重构后）
│   │   ├── components/   # 可复用UI组件
│   │   ├── dialogs/      # 对话框（Dialog-Controller分离）
│   │   ├── main_window/  # 主窗口（MVC模式）
│   │   ├── factories/    # 工厂模式
│   │   ├── events/       # 事件总线
│   │   └── widgets/      # 自定义控件
│   └── utils/            # 工具函数
├── tests/                # 测试文件（UI重构后新增大量测试）
│   ├── test_ui/          # UI层测试
│   │   ├── components/   # 组件测试
│   │   ├── dialogs/      # 对话框测试
│   │   ├── main_window/  # 主窗口测试
│   │   ├── events/       # 事件总线测试
│   │   └── factories/    # 工厂测试
│   ├── test_services/    # 服务层测试
│   ├── test_core/        # 核心层测试
│   └── test_database/    # 数据库层测试
├── docs/                 # 文档
├── resources/            # 资源文件
├── scripts/              # 辅助脚本
└── dependencies/         # 依赖配置
```

详细说明见：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

### 编译资源

```bash
# 编译UI和资源文件
python scripts/compile_resources.py
```

### 打包应用

```bash
# 使用PyInstaller打包
python scripts/build_exe.py

# 生成的可执行文件在 dist/ 目录
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行UI层测试（UI重构后新增）
pytest tests/test_ui/

# 运行组件测试
pytest tests/test_ui/components/

# 运行对话框测试
pytest tests/test_ui/dialogs/

# 运行主窗口测试
pytest tests/test_ui/main_window/

# 运行事件总线测试
pytest tests/test_ui/events/

# 运行服务层测试
pytest tests/test_services/

# 生成覆盖率报告
pytest --cov=src tests/

# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html tests/
```

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写文档字符串
- 添加单元测试

详细说明见：[开发指南](docs/dev_setup.md)

---

## 📚 相关文档

### 用户文档
- [用户手册](docs/user_manual.md) - 功能使用说明
- [OCR使用指南](docs/OCR使用指南.md) - OCR功能详解
- [常见问题](docs/README.md) - 问题解答

### 开发文档
- [架构设计](docs/architecture.md) - 系统架构
- [数据库设计](docs/database_design.md) - 数据库结构
- [API文档](docs/backend_services.md) - 服务接口

### 更新日志
- [CHANGELOG](docs/CHANGELOG.md) - 版本更新记录
- [最近更新](docs/recent_updates_summary.md) - 最新功能

---

## 🆘 获取帮助

### 问题反馈
- GitHub Issues: https://github.com/yangwenrui6/CuoTi/issues
- 邮箱: [项目维护者邮箱]

### 贡献代码
欢迎提交Pull Request！请先阅读 [贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**最后更新**: 2026年2月9日（UI重构后更新）

**版本**: v2.0.0 - UI重构版本

**主要更新**:
- ✅ UI层组件化架构
- ✅ Dialog-Controller分离
- ✅ 工厂模式 + 依赖注入
- ✅ 事件总线实现
- ✅ 复习历史功能
- ✅ 完整的测试覆盖
