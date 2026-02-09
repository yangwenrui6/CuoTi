# 错题本项目结构说明

## 📁 完整目录树

```
mistake_book/                          # 项目根目录
├── src/                               # 源代码（避免顶层污染）
│   └── mistake_book/                  # 主应用包（可import）
│       ├── __init__.py                # 包初始化，版本信息
│       ├── __main__.py                # 支持 python -m mistake_book 启动
│       ├── main.py                    # QApplication入口 + 异常全局捕获
│       ├── exceptions.py              # 自定义异常（DataError, OCRFailed等）
│       │
│       ├── config/                    # 配置管理
│       │   ├── __init__.py
│       │   ├── settings.py            # 动态配置（路径/主题/算法参数）
│       │   ├── constants.py           # 枚举/常量（掌握度等级、错误类型）
│       │   └── paths.py               # 跨平台路径生成（用platformdirs）
│       │
│       ├── core/                      # 业务逻辑核心（无GUI依赖！）
│       │   ├── __init__.py
│       │   ├── review_scheduler.py    # 间隔重复算法(SM-2) + 复习计划生成
│       │   ├── data_manager.py        # 业务层：封装增删改查+统计逻辑
│       │   ├── export_handler.py      # 导出PDF/Excel逻辑
│       │   └── import_parser.py       # CSV/图片批量导入解析
│       │
│       ├── database/                  # 数据持久层
│       │   ├── __init__.py
│       │   ├── models.py              # SQLAlchemy ORM模型（Question/Tag等）
│       │   ├── db_manager.py          # 连接池、事务、初始化、备份
│       │   └── migrations/            # （可选）Alembic迁移脚本
│       │
│       ├── services/                  # 外部能力封装 + 业务服务
│       │   ├── __init__.py
│       │   ├── question_service.py    # 错题业务服务（创建、更新、删除、查看详情）
│       │   ├── review_service.py      # 复习业务服务（获取待复习、处理结果、统计）
│       │   ├── ui_service.py          # UI业务服务（搜索、筛选、导航、统计）
│       │   ├── ocr_engine.py          # OCR接口（PaddleOCR/Tesseract适配器）
│       │   ├── notification.py        # 系统通知（复习提醒）
│       │   └── cloud_sync.py          # 云同步抽象（预留接口）
│       │
│       ├── ui/                        # 界面层（组件化架构）
│       │   ├── __init__.py
│       │   ├── components/            # 可复用UI组件
│       │   │   ├── __init__.py
│       │   │   ├── image_uploader.py  # 图片上传组件（拖拽+点击）
│       │   │   ├── ocr_panel.py       # OCR识别面板
│       │   │   ├── question_form.py   # 题目表单组件
│       │   │   ├── filter_panel.py    # 筛选面板组件
│       │   │   ├── statistics_panel.py # 统计面板组件
│       │   │   └── navigation_tree.py # 导航树组件
│       │   ├── dialogs/               # 对话框（Dialog-Controller分离）
│       │   │   ├── __init__.py
│       │   │   ├── add_question/      # 添加错题对话框
│       │   │   │   ├── __init__.py
│       │   │   │   ├── dialog.py      # UI组装器
│       │   │   │   └── controller.py  # 业务逻辑控制器
│       │   │   ├── detail/            # 详情对话框
│       │   │   │   ├── __init__.py
│       │   │   │   ├── dialog.py      # UI组装器
│       │   │   │   └── controller.py  # 业务逻辑控制器
│       │   │   ├── review/            # 复习对话框
│       │   │   │   ├── __init__.py
│       │   │   │   ├── dialog.py      # UI组装器
│       │   │   │   └── controller.py  # 业务逻辑控制器
│       │   │   ├── review_module_selector.py # 复习模块选择器
│       │   │   └── review_history_dialog.py  # 复习历史对话框
│       │   ├── main_window/           # 主窗口（MVC模式）
│       │   │   ├── __init__.py
│       │   │   ├── window.py          # 主窗口UI组装器
│       │   │   ├── controller.py      # 主窗口控制器
│       │   │   └── panels.py          # 面板工厂
│       │   ├── factories/             # 工厂模式
│       │   │   ├── __init__.py
│       │   │   └── dialog_factory.py  # 对话框工厂（依赖注入）
│       │   ├── events/                # 事件总线
│       │   │   ├── __init__.py
│       │   │   ├── event_bus.py       # 事件总线实现
│       │   │   └── events.py          # 事件类型定义
│       │   └── widgets/               # 自定义控件
│       │       ├── __init__.py
│       │       └── question_card.py   # 错题卡片组件（固定高度180px）
│       │
│       └── utils/                     # 通用工具
│           ├── __init__.py
│           ├── helpers.py             # 日期格式化/路径安全等
│           ├── validators.py          # 表单验证
│           ├── logger.py              # 统一日志配置（文件+控制台）
│           └── image_processor.py     # 截图压缩/OCR预处理
│
├── resources/                         # 原始资源（开发时）
│   ├── ui/                            # .ui文件（Qt Designer设计）
│   │   ├── main_window.ui             # 主窗口UI设计
│   │   ├── add_question_dialog.ui     # 添加错题对话框UI
│   │   └── ...
│   ├── images/                        # 原始图片/图标
│   ├── styles/                        # QSS样式表（支持亮色/暗色主题）
│   │   ├── light.qss                  # 亮色主题
│   │   └── dark.qss                   # 暗色主题
│   └── app.qrc                        # Qt资源清单（引用images/）
│

├── scripts/                           # 辅助脚本
│   ├── compile_resources.py           # 一键编译.ui/.qrc → resources/
│   ├── build_exe.py                   # PyInstaller打包配置
│   ├── check_ocr_status.py            # OCR状态诊断工具
│   └── migrate_v1_to_v2.py            # 数据库迁移脚本（版本升级用）
│
├── docs/                              # 文档
│   ├── README.md                      # 文档索引
│   ├── architecture.md                # 架构设计
│   ├── backend_services.md            # 后端服务架构
│   ├── database_design.md             # 数据库设计
│   ├── gui_design.md                  # GUI界面设计
│   ├── integration.md                 # 前后端集成说明
│   ├── refactoring_services.md        # 服务层重构文档
│   ├── ui_optimization.md             # UI层优化重构文档
│   ├── core_layer_analysis.md         # Core层使用情况分析
│   ├── data_flow_fix.md               # 数据流修复文档
│   ├── ui_refresh_fix.md              # UI刷新问题修复文档
│   ├── database_cache_fix.md          # 数据库缓存问题修复文档
│   ├── view_detail_feature.md         # 查看错题详情功能文档
│   ├── delete_question_feature.md     # 删除错题功能文档
│   ├── card_click_interaction.md      # 卡片点击交互优化
│   ├── view_state_persistence.md      # 视图状态持久化
│   ├── navigation_selection_persistence.md # 导航树选中状态持久化
│   ├── prevent_duplicate_save.md      # 防止重复保存
│   ├── ocr_implementation.md          # OCR功能完整实现
│   ├── ocr_simplification.md          # OCR引擎简化说明
│   ├── easyocr_pyqt6_fix.md           # EasyOCR与PyQt6冲突修复
│   ├── easyocr_dll_fix.md             # EasyOCR DLL错误修复
│   ├── chinese_path_fix.md            # 中文路径OCR识别修复
│   ├── auto_ocr_on_drop.md            # 拖拽图片自动OCR识别
│   ├── image_upload_and_preview.md    # 图片上传和预览功能
│   ├── image_loading_fix.md           # 图片加载中文路径修复
│   ├── ocr_lazy_loading.md            # OCR延迟加载优化
│   ├── move_models_to_other_drive.md  # 模型路径配置到其他盘符
│   ├── ocr_async_loading.md           # OCR异步加载优化
│   ├── ocr_status_notification.md     # OCR状态通知优化
│   ├── ocr_model_path_fix.md          # OCR模型路径修复
│   ├── ocr_recognition_fix.md         # OCR识别流程修复
│   ├── ocr_quick_start.md             # OCR功能快速入门
│   ├── ocr_status_and_solutions.md    # OCR状态诊断与解决方案
│   ├── OCR使用指南.md                 # OCR使用快速指南
│   ├── OCR功能总结.md                 # OCR功能完整总结
│   ├── 移动模型到D盘说明.md           # 移动模型到D盘操作说明
│   ├── tesseract_installation_guide.md # Tesseract安装指南
│   ├── user_manual.md                 # 用户指南
│   └── dev_setup.md                   # 开发环境搭建
│
├── dependencies/                      # 依赖配置文件
│   ├── README.md                     # 依赖说明文档
│   ├── requirements.txt              # 基础依赖（pyqt6, sqlalchemy...）
│   ├── requirements-dev.txt          # 开发依赖（black, flake8...）
│   └── pyproject.toml                # 项目构建配置
│
├── tests/                            # 测试文件
│   ├── test_ui/                      # UI层测试（重构后）
│   │   ├── __init__.py
│   │   ├── components/               # 组件测试
│   │   │   ├── test_image_uploader.py
│   │   │   ├── test_ocr_panel.py
│   │   │   ├── test_question_form.py
│   │   │   ├── test_filter_panel.py
│   │   │   ├── test_statistics_panel.py
│   │   │   └── test_navigation_tree.py
│   │   ├── dialogs/                  # 对话框测试
│   │   │   ├── test_add_question_controller.py
│   │   │   ├── test_add_question_dialog_integration.py
│   │   │   ├── test_detail_controller.py
│   │   │   ├── test_detail_dialog_integration.py
│   │   │   ├── test_review_controller.py
│   │   │   └── test_review_dialog_integration.py
│   │   ├── main_window/              # 主窗口测试
│   │   │   ├── test_controller.py
│   │   │   ├── test_panels.py
│   │   │   └── test_window_integration.py
│   │   ├── events/                   # 事件总线测试
│   │   │   └── test_event_bus.py
│   │   └── factories/                # 工厂测试
│   │       └── test_dialog_factory.py
│   ├── test_services/                # 服务层测试（OCR相关）
│   │   ├── __init__.py
│   │   ├── test_ocr_english_support.py
│   │   ├── test_ocr_recognition_improved.py
│   │   └── ...                       # 其他服务测试
│   ├── test_core/                    # 核心层测试
│   │   └── __init__.py
│   ├── test_database/                # 数据库层测试
│   │   └── __init__.py
│   ├── test_utils/                   # 工具层测试
│   │   ├── __init__.py
│   │   └── test_chinese_path.py      # 中文路径测试
│   ├── test_full_integration.py      # 集成测试
│   └── README.md                     # 测试说明文档
│
├── .gitignore                         # 忽略__pycache__/build/用户数据等
├── README.md                          # 项目说明
└── LICENSE                            # MIT许可证
```

## 📦 核心模块说明

### 1. config/ - 配置管理
- **settings.py**: 动态配置（主题、数据库路径、算法参数等）
- **constants.py**: 枚举常量（掌握度等级、题型、复习结果）
- **paths.py**: 跨平台路径管理（使用platformdirs）

### 2. core/ - 业务逻辑核心
> ⚠️ 重要：此层完全独立于GUI，可单独测试

- **review_scheduler.py**: SM-2间隔重复算法实现
- **data_manager.py**: 业务层数据管理（增删改查、统计）
- **export_handler.py**: 导出PDF/Excel功能
- **import_parser.py**: CSV/图片批量导入

### 3. database/ - 数据持久层
- **models.py**: SQLAlchemy ORM模型定义
  - Question（错题）
  - Tag（标签）
  - ReviewRecord（复习记录）
- **db_manager.py**: 数据库连接池、事务管理、备份恢复

### 4. services/ - 外部服务封装 + 业务服务层
> 💡 服务层封装业务逻辑，UI层通过服务层与核心层交互

- **question_service.py**: 错题业务服务
  - create_question(): 创建错题
  - update_question(): 更新错题
  - delete_question(): 删除错题（带确认）
  - get_question_detail(): 获取错题详情
  - recognize_image(): OCR图片识别
- **review_service.py**: 复习业务服务
  - get_due_questions(): 获取待复习错题
  - process_review_result(): 处理复习结果
  - get_review_statistics(): 获取复习统计
- **ui_service.py**: UI业务服务
  - get_all_questions(): 获取所有错题
  - search_questions(): 搜索错题（多字段）
  - filter_questions(): 筛选错题（多条件）
  - get_navigation_data(): 获取导航树数据
  - get_filter_options(): 获取筛选器选项
  - parse_filter_from_ui(): 解析UI筛选条件
  - get_statistics_summary(): 获取统计摘要
- **ocr_engine.py**: OCR引擎适配器
  - 支持EasyOCR（中英文混合识别）
  - 异步加载模型，不阻塞UI
  - 自定义模型路径（D:/EasyOCR）
  - 后台线程初始化
- **notification.py**: 系统通知服务
- **cloud_sync.py**: 云同步接口（预留）

### 5. ui/ - 界面层（组件化架构 + MVC模式）

#### 架构模式
- **组件化设计**: 可复用的UI组件（ImageUploader, OCRPanel, QuestionForm等）
- **Dialog-Controller分离**: 对话框只负责UI组装，Controller处理业务逻辑
- **工厂模式**: DialogFactory统一创建对话框，管理依赖注入
- **事件总线**: EventBus实现组件间解耦通信

#### 目录结构
- **components/**: 可复用UI组件
  - ImageUploader: 图片上传（拖拽+点击）
  - OCRPanel: OCR识别面板
  - QuestionForm: 题目表单
  - FilterPanel: 筛选面板
  - StatisticsPanel: 统计面板
  - NavigationTree: 导航树

- **dialogs/**: 对话框（Dialog-Controller分离）
  - add_question/: 添加错题对话框
    - dialog.py: UI组装器（使用组件）
    - controller.py: 业务逻辑（调用Service）
  - detail/: 详情对话框
    - dialog.py: UI组装器
    - controller.py: 业务逻辑
  - review/: 复习对话框
    - dialog.py: UI组装器
    - controller.py: 业务逻辑
  - review_module_selector.py: 复习模块选择器
  - review_history_dialog.py: 复习历史对话框

- **main_window/**: 主窗口（MVC模式）
  - window.py: 主窗口UI组装器
  - controller.py: 主窗口控制器
  - panels.py: 面板工厂（创建导航、卡片、筛选面板）

- **factories/**: 工厂模式
  - dialog_factory.py: 对话框工厂（依赖注入）

- **events/**: 事件总线
  - event_bus.py: 事件总线实现（发布-订阅模式）
  - events.py: 事件类型定义（QuestionAddedEvent等）

- **widgets/**: 自定义控件
  - question_card.py: 错题卡片（固定高度180px）

### 6. utils/ - 通用工具
- **logger.py**: 统一日志配置
- **helpers.py**: 日期格式化、路径安全等
- **validators.py**: 表单验证
- **image_processor.py**: 图片压缩、OCR预处理

## 📦 依赖管理 (dependencies/)

### requirements.txt - 基础依赖
运行应用所需的最小依赖包：
- **PyQt6**: GUI框架
- **SQLAlchemy**: 数据库ORM
- **platformdirs**: 跨平台路径管理
- **Pillow**: 图片处理
- **plyer**: 系统通知

### requirements-dev.txt - 开发依赖
开发和打包所需的工具：
- **black**: 代码格式化
- **flake8**: 代码检查
- **mypy**: 类型检查
- **PyInstaller**: 应用打包

### pyproject.toml - 项目配置
现代化的Python项目配置文件，包含：
- 项目元数据
- 依赖声明
- 构建系统配置
- 工具配置

详见 [dependencies/README.md](../dependencies/README.md)

## 📚 文档系统 (docs/)

所有项目文档集中在 `docs/` 目录：

### 架构与设计
- **README.md**: 文档索引和导航
- **architecture.md**: 整体架构设计说明
- **backend_services.md**: 后端服务架构详解
- **database_design.md**: 数据库表结构和ER图
- **gui_design.md**: GUI界面设计规范
- **integration.md**: 前后端集成流程
- **core_layer_analysis.md**: Core层使用分析

### 重构与优化
- **refactoring_services.md**: 服务层重构记录
- **ui_optimization.md**: UI层业务逻辑优化
- **data_flow_fix.md**: 数据流修复记录
- **ui_refresh_fix.md**: UI刷新问题修复
- **database_cache_fix.md**: 数据库缓存问题修复

### 错题管理功能
- **view_detail_feature.md**: 查看错题详情功能
- **delete_question_feature.md**: 删除错题功能
- **detail_dialog_ui_improvement.md**: 详情对话框UI优化
- **editable_answer_in_detail.md**: 详情对话框答案编辑功能
- **card_click_interaction.md**: 卡片点击交互优化
- **card_fixed_height.md**: 卡片固定高度优化
- **main_page_card_ui_improvement.md**: 主页面卡片UI优化
- **view_state_persistence.md**: 视图状态持久化
- **navigation_selection_persistence.md**: 导航树选中状态持久化
- **prevent_duplicate_save.md**: 防止重复保存

### 复习功能
- **review_refactoring.md**: 复习功能重构总览
- **review_module_selector.md**: 复习模块选择器实现
- **review_module_selector_fix.md**: 复习模块选择器修复

### OCR功能
- **ocr_implementation.md**: OCR功能完整实现
- **ocr_simplification.md**: OCR引擎简化说明
- **ocr_lazy_loading.md**: OCR延迟加载优化
- **ocr_async_loading.md**: OCR异步加载优化
- **ocr_status_notification.md**: OCR状态通知优化
- **ocr_quick_start.md**: OCR功能快速入门
- **ocr_status_and_solutions.md**: OCR状态诊断与解决方案
- **OCR使用指南.md**: OCR使用快速指南（中文）
- **OCR功能总结.md**: OCR功能完整总结（中文）

### OCR问题修复
- **easyocr_pyqt6_fix.md**: EasyOCR与PyQt6 DLL冲突修复
- **easyocr_dll_fix.md**: EasyOCR DLL错误修复
- **chinese_path_fix.md**: 中文路径OCR识别修复
- **ocr_model_path_fix.md**: OCR模型路径修复
- **ocr_recognition_fix.md**: OCR识别流程修复
- **ocr_recognition_improvement.md**: OCR识别改进
- **ocr_english_support_restored.md**: OCR英文支持恢复
- **ocr_model_download_issue.md**: OCR模型下载问题
- **ocr_ui_freeze_fix.md**: OCR UI冻结修复
- **OCR未响应问题已解决.md**: OCR未响应问题已解决（中文）
- **OCR模型下载问题已解决.md**: OCR模型下载问题已解决（中文）

### 图片处理
- **auto_ocr_on_drop.md**: 拖拽图片自动OCR识别
- **image_upload_and_preview.md**: 图片上传和预览功能
- **image_loading_fix.md**: 图片加载中文路径修复

### 模型管理
- **move_models_to_other_drive.md**: 模型路径配置到其他盘符
- **移动模型到D盘说明.md**: 移动模型到D盘操作说明（中文）

### 系统问题修复
- **app_startup_freeze_fix.md**: 应用启动冻结修复
- **qt_thread_safety_fix.md**: Qt线程安全问题修复
- **pytorch_pin_memory_warning_fix.md**: PyTorch pin_memory警告修复
- **应用启动未响应问题已解决.md**: 应用启动未响应问题已解决（中文）
- **Qt线程安全问题已解决.md**: Qt线程安全问题已解决（中文）

### 测试与工具
- **test_organization.md**: 测试组织结构
- **ocr_test_status.md**: OCR测试状态
- **frontend_check_summary.md**: 前端检查总结
- **tesseract_installation_guide.md**: Tesseract安装指南

### 用户文档
- **dev_setup.md**: 开发环境搭建指南
- **user_manual.md**: 用户使用手册

## 🎯 最新功能特性

### UI层重构（2026年2月）
1. **组件化架构**
   - 6个可复用UI组件（ImageUploader, OCRPanel, QuestionForm等）
   - Dialog-Controller分离，业务逻辑与UI解耦
   - 所有组件可独立实例化和测试

2. **工厂模式 + 依赖注入**
   - DialogFactory统一创建对话框
   - 自动注入服务依赖（QuestionService, ReviewService等）
   - 简化对话框创建流程

3. **事件总线**
   - EventBus实现发布-订阅模式
   - 组件间解耦通信
   - 支持QuestionAdded, QuestionUpdated, QuestionDeleted等事件

4. **测试覆盖**
   - 组件单元测试（11个测试文件）
   - Controller单元测试（3个测试文件）
   - 集成测试（3个测试文件）
   - EventBus和DialogFactory测试

### 复习功能（全新设计）
1. **模块选择器**
   - 左右分栏：科目列表（蓝色）+ 题型列表（绿色）
   - 实时统计每个模块的题目数量
   - 支持选择特定模块或全部复习
   - 新增"复习历史"功能（最近30题）
   - 清晰的视觉反馈和提示

2. **复习对话框**
   - 简洁的卡片式设计
   - 显示题目图片和内容
   - 答案折叠区（初始隐藏）
   - 掌握度按钮组（🔴生疏/🟡困难/🟢掌握/🔵熟练）
   - 自动记录复习历史
   - 完成后显示统计总结
   - 支持"继续复习"（重新打开模块选择器）

3. **复习历史**
   - 查看最近30次复习记录
   - 显示复习时间、科目、题型、掌握度
   - 支持直接复习历史题目
   - 智能去重（同一题目只保留最近一次）

### UI优化
1. **卡片固定高度**：所有错题卡片统一180px高度，视觉整齐
2. **详情对话框可编辑**：可直接编辑题目、答案、解析，退出时提示保存
3. **长文本滚动**：编辑框设置最大高度，超出部分自动滚动
4. **字体和对比度优化**：增大字体、提高颜色对比度，改善可读性

### OCR功能
1. **异步加载**：后台初始化，不阻塞UI启动
2. **中英文混合识别**：支持['ch_sim', 'en']
3. **自定义模型路径**：D:/EasyOCR
4. **拖拽自动识别**：拖拽图片到添加对话框自动OCR
5. **线程安全**：所有UI操作在主线程执行

## 🎯 设计原则

### 分层架构（UI重构后）
```
┌─────────────────────────────────┐
│   UI Layer (Components)         │  组件层（可复用UI组件）
├─────────────────────────────────┤
│   Dialog/Controller Layer       │  对话框层（UI组装 + 业务控制）
├─────────────────────────────────┤
│   Factory + EventBus            │  工厂模式 + 事件总线
├─────────────────────────────────┤
│   Service Layer                 │  服务层（业务逻辑封装）
├─────────────────────────────────┤
│   Core Business Logic           │  核心业务层（算法/数据管理）
├─────────────────────────────────┤
│   Database Layer (SQLAlchemy)   │  数据持久层（ORM模型）
└─────────────────────────────────┘
```

### 数据流向
```
UI Component → Dialog → Controller → Service → Core/DataManager → Database
     ↓           ↓          ↓            ↓           ↓                ↓
  用户交互    UI组装    业务控制    业务封装    业务逻辑         数据持久化
```

### UI层架构特点
1. **组件化**: 可复用的UI组件（ImageUploader, OCRPanel等）
2. **Dialog-Controller分离**: Dialog只负责UI，Controller处理业务
3. **依赖注入**: 通过DialogFactory注入服务依赖
4. **事件驱动**: EventBus实现组件间解耦通信
5. **工厂模式**: 统一创建对话框，管理依赖关系

### 关键特性
1. **业务逻辑与UI分离**: core/目录完全独立，可单独测试
2. **服务层封装**: UI通过Service层访问业务逻辑，降低耦合
3. **组件可复用**: UI组件可在多个对话框中复用
4. **依赖注入**: 通过构造函数注入依赖，便于测试和维护
5. **接口抽象**: OCR、云同步等使用抽象基类，易于扩展
6. **事件解耦**: 使用EventBus实现组件间通信，避免直接依赖

### 最佳实践
- ✅ UI组件只负责展示和用户交互，不包含业务逻辑
- ✅ Controller处理业务逻辑，调用Service层
- ✅ Dialog只负责UI组装，连接信号到Controller
- ✅ 使用依赖注入传递服务实例
- ✅ 使用EventBus实现组件间通信
- ✅ 异常处理在Service层统一处理
- ✅ 数据验证在Service层完成
- ✅ 组件保持独立，可单独测试

## 🚀 快速开始

### 安装依赖
```bash
pip install -r dependencies/requirements.txt
```

### 运行应用
```bash
python -m mistake_book
```

### 开发模式
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 编译资源
python scripts/compile_resources.py

# 打包应用
python scripts/build_exe.py
```

## 📝 数据库模型

### Question（错题）
- 基本信息：学科、题型、内容、答案
- 复习数据：掌握度、难度因子、下次复习时间
- 关联：标签（多对多）、复习记录（一对多）

### Tag（标签）
- 名称、颜色
- 关联：错题（多对多）

### ReviewRecord（复习记录）
- 复习时间、结果、耗时
- 关联：错题（多对一）

## 🔧 技术栈

- **GUI框架**: PyQt6
- **数据库**: SQLite + SQLAlchemy ORM
- **复习算法**: SM-2间隔重复算法
- **路径管理**: platformdirs（跨平台）
- **OCR引擎**: PaddleOCR / Tesseract（可选）
- **测试框架**: pytest
- **打包工具**: PyInstaller

## 📄 许可证

MIT License
