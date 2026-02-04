# 测试文件组织重构

## 📋 重构说明

将所有测试文件按照模块分类，组织到对应的子目录中，使测试结构更清晰、更易维护。

## 🎯 重构目标

1. **清晰的目录结构**：按照源代码的模块结构组织测试
2. **易于查找**：快速定位特定模块的测试
3. **便于维护**：新增测试时知道应该放在哪里
4. **符合规范**：遵循Python测试的最佳实践

## 📁 新的测试目录结构

```
tests/
├── test_services/              # 服务层测试（11个文件）
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
├── test_ui/                    # UI层测试（3个文件）
│   ├── __init__.py
│   ├── test_add_dialog.py      # 添加错题对话框测试
│   ├── test_image_loading.py   # 图片加载测试
│   └── test_cursor_warning.py  # 光标警告测试
│
├── test_core/                  # 核心层测试
│   └── __init__.py
│   # TODO: 添加核心业务逻辑测试
│
├── test_database/              # 数据库层测试
│   └── __init__.py
│   # TODO: 添加数据库测试
│
├── test_utils/                 # 工具层测试（1个文件）
│   ├── __init__.py
│   └── test_chinese_path.py    # 中文路径处理测试
│
├── test_full_integration.py    # 集成测试（完整流程）
└── README.md                   # 测试说明文档
```

## 🔄 文件移动记录

### test_services/ - 服务层测试

从 `tests/` 根目录移动到 `tests/test_services/`：

- ✅ test_ocr_simple.py
- ✅ test_ocr_complete.py
- ✅ test_ocr_full_flow.py
- ✅ test_ocr_thread.py
- ✅ test_ocr_with_image.py
- ✅ test_chinese_only_model.py
- ✅ test_with_existing_models.py
- ✅ test_config_check.py
- ✅ test_async_loading.py
- ✅ test_lazy_loading.py
- ✅ test_recognition_flow.py

### test_ui/ - UI层测试

从 `tests/` 根目录移动到 `tests/test_ui/`：

- ✅ test_add_dialog.py
- ✅ test_image_loading.py
- ✅ test_cursor_warning.py

### test_utils/ - 工具层测试

已存在于 `tests/test_utils/`：

- ✅ test_chinese_path.py

### 保留在根目录

- ✅ test_full_integration.py（集成测试）
- ✅ README.md（测试说明）

## 📝 创建的文件

### __init__.py 文件

为每个测试子目录创建了 `__init__.py`：

- ✅ test_services/__init__.py
- ✅ test_ui/__init__.py
- ✅ test_core/__init__.py
- ✅ test_database/__init__.py
- ✅ test_utils/__init__.py

### 文档文件

- ✅ tests/README.md - 测试说明文档
- ✅ docs/test_organization.md - 本文档

### 辅助脚本

- ✅ scripts/organize_tests.py - 测试文件组织脚本

## 🚀 运行测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定模块的测试

```bash
# 服务层测试
pytest tests/test_services/

# UI层测试
pytest tests/test_ui/

# 工具层测试
pytest tests/test_utils/
```

### 运行单个测试文件

```bash
pytest tests/test_services/test_ocr_simple.py
```

## 📊 测试统计

### 按模块分类

| 模块 | 测试文件数 | 说明 |
|------|-----------|------|
| test_services | 11 | 服务层测试，主要是OCR相关 |
| test_ui | 3 | UI层测试，对话框和交互 |
| test_core | 0 | 核心层测试（待添加） |
| test_database | 0 | 数据库层测试（待添加） |
| test_utils | 1 | 工具层测试 |
| 集成测试 | 1 | 完整流程测试 |
| **总计** | **16** | |

### 测试覆盖情况

- ✅ **OCR服务**：完整覆盖（11个测试文件）
- ✅ **UI交互**：基本覆盖（3个测试文件）
- ✅ **工具函数**：部分覆盖（1个测试文件）
- ⚠️ **核心业务**：待添加
- ⚠️ **数据库操作**：待添加

## 🎯 后续工作

### 需要添加的测试

#### test_core/ - 核心层测试

- [ ] test_review_scheduler.py - 复习调度算法测试
- [ ] test_data_manager.py - 数据管理测试
- [ ] test_export_handler.py - 导出功能测试
- [ ] test_import_parser.py - 导入功能测试

#### test_database/ - 数据库层测试

- [ ] test_models.py - ORM模型测试
- [ ] test_db_manager.py - 数据库管理测试
- [ ] test_transactions.py - 事务测试

#### test_services/ - 服务层测试（补充）

- [ ] test_question_service.py - 错题服务测试
- [ ] test_review_service.py - 复习服务测试
- [ ] test_ui_service.py - UI服务测试
- [ ] test_notification.py - 通知服务测试

#### test_ui/ - UI层测试（补充）

- [ ] test_main_window.py - 主窗口测试
- [ ] test_review_dialog.py - 复习对话框测试
- [ ] test_detail_dialog.py - 详情对话框测试
- [ ] test_question_card.py - 错题卡片测试

## 📚 参考文档

- [tests/README.md](../tests/README.md) - 测试说明文档
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - 项目结构说明
- [pytest官方文档](https://docs.pytest.org/)

## ✅ 重构完成

测试文件已成功组织到对应的子目录中，结构清晰，易于维护。

**重构时间**：2026-02-04  
**重构工具**：scripts/organize_tests.py  
**影响范围**：tests/ 目录结构
