# 测试文件组织说明

## 📁 测试目录结构

```
tests/
├── test_services/              # 服务层测试
│   ├── __init__.py
│   ├── test_ocr_simple.py      # OCR基础功能测试
│   ├── test_ocr_complete.py    # OCR完整流程测试
│   ├── test_ocr_full_flow.py   # OCR全流程测试
│   ├── test_ocr_thread.py      # OCR后台线程测试
│   ├── test_ocr_with_image.py  # OCR图片识别测试
│   ├── test_chinese_only_model.py  # 中文模型测试
│   ├── test_with_existing_models.py  # 已有模型测试
│   ├── test_config_check.py    # OCR配置检查
│   ├── test_async_loading.py   # 异步加载测试
│   ├── test_lazy_loading.py    # 延迟加载测试
│   └── test_recognition_flow.py  # 识别流程测试
│
├── test_ui/                    # UI层测试
│   ├── __init__.py
│   ├── test_add_dialog.py      # 添加错题对话框测试
│   ├── test_image_loading.py   # 图片加载测试
│   └── test_cursor_warning.py  # 光标警告测试
│
├── test_core/                  # 核心层测试
│   └── __init__.py
│   # TODO: 添加核心业务逻辑测试
│   # - test_review_scheduler.py  # 复习调度算法测试
│   # - test_data_manager.py      # 数据管理测试
│
├── test_database/              # 数据库层测试
│   └── __init__.py
│   # TODO: 添加数据库测试
│   # - test_models.py            # ORM模型测试
│   # - test_db_manager.py        # 数据库管理测试
│
├── test_utils/                 # 工具层测试
│   ├── __init__.py
│   └── test_chinese_path.py    # 中文路径处理测试
│
├── test_full_integration.py    # 集成测试（完整流程）
└── README.md                   # 本文件
```

## 🎯 测试分类说明

### 1. test_services/ - 服务层测试

测试各种服务的功能，主要是OCR相关服务：

- **OCR基础测试**：测试OCR引擎的基本功能
- **OCR配置测试**：测试OCR配置和模型加载
- **OCR性能测试**：测试异步加载、延迟加载等优化
- **OCR识别测试**：测试实际的图片识别功能

### 2. test_ui/ - UI层测试

测试用户界面组件：

- **对话框测试**：测试各种对话框的功能
- **图片加载测试**：测试图片上传和预览
- **交互测试**：测试用户交互逻辑

### 3. test_core/ - 核心层测试

测试核心业务逻辑（独立于UI）：

- **复习算法测试**：测试SM-2间隔重复算法
- **数据管理测试**：测试业务层数据操作
- **导入导出测试**：测试数据导入导出功能

### 4. test_database/ - 数据库层测试

测试数据持久化：

- **ORM模型测试**：测试数据模型定义
- **数据库操作测试**：测试CRUD操作
- **事务测试**：测试事务管理

### 5. test_utils/ - 工具层测试

测试通用工具函数：

- **路径处理测试**：测试中文路径处理
- **图片处理测试**：测试图片压缩、转换
- **验证器测试**：测试表单验证

### 6. test_full_integration.py - 集成测试

测试完整的用户流程，从UI到数据库的端到端测试。

## 🚀 运行测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定模块的测试

```bash
# 只运行服务层测试
pytest tests/test_services/

# 只运行UI层测试
pytest tests/test_ui/

# 只运行核心层测试
pytest tests/test_core/

# 只运行数据库层测试
pytest tests/test_database/

# 只运行工具层测试
pytest tests/test_utils/
```

### 运行单个测试文件

```bash
pytest tests/test_services/test_ocr_simple.py
```

### 运行特定测试函数

```bash
pytest tests/test_services/test_ocr_simple.py::test_ocr_basic
```

### 显示详细输出

```bash
pytest tests/ -v
```

### 显示打印输出

```bash
pytest tests/ -s
```

### 生成覆盖率报告

```bash
pytest tests/ --cov=src/mistake_book --cov-report=html
```

## 📝 测试编写规范

### 1. 文件命名

- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 测试类以 `Test` 开头

### 2. 测试组织

```python
"""模块功能测试"""

import pytest
from mistake_book.services import SomeService


class TestSomeService:
    """SomeService测试类"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.service = SomeService()
    
    def teardown_method(self):
        """每个测试方法后执行"""
        pass
    
    def test_basic_function(self):
        """测试基本功能"""
        result = self.service.do_something()
        assert result is not None
    
    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ValueError):
            self.service.do_invalid_thing()
```

### 3. 测试数据

- 使用 `pytest.fixture` 创建测试数据
- 测试数据应该独立，不依赖外部状态
- 使用临时文件和数据库进行测试

### 4. 断言

```python
# 基本断言
assert result == expected

# 异常断言
with pytest.raises(ValueError):
    function_that_raises()

# 近似相等（浮点数）
assert result == pytest.approx(3.14, rel=1e-2)
```

## 🔧 测试工具

### pytest

主要测试框架，提供：
- 测试发现和运行
- 断言增强
- Fixture机制
- 参数化测试

### pytest-qt

PyQt6应用测试工具：
- 模拟用户交互
- 测试信号槽
- 测试对话框

### pytest-cov

代码覆盖率工具：
- 生成覆盖率报告
- 识别未测试代码

## 📊 测试覆盖率目标

- **核心层（core/）**：>80% 覆盖率
- **服务层（services/）**：>70% 覆盖率
- **数据库层（database/）**：>80% 覆盖率
- **UI层（ui/）**：>50% 覆盖率（UI测试较复杂）
- **工具层（utils/）**：>80% 覆盖率

## 🎯 测试优先级

### P0 - 必须测试
- 核心业务逻辑（复习算法、数据管理）
- 数据库操作（CRUD、事务）
- 关键服务（OCR、导入导出）

### P1 - 应该测试
- UI交互逻辑
- 工具函数
- 错误处理

### P2 - 可选测试
- UI样式
- 日志输出
- 性能测试

## 📚 相关文档

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-qt文档](https://pytest-qt.readthedocs.io/)
- [项目架构文档](../docs/architecture.md)
- [开发环境搭建](../docs/dev_setup.md)
