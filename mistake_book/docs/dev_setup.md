# 开发环境搭建

## 环境要求

- Python 3.9+
- PyQt6
- SQLAlchemy

## 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd mistake_book
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements-dev.txt
```

4. 运行应用
```bash
python -m mistake_book
```

## 开发工具

- 代码格式化: `black src/`
- 代码检查: `flake8 src/`
- 运行测试: `pytest tests/`
- 编译资源: `python scripts/compile_resources.py`
