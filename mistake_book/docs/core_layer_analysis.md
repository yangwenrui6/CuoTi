# Core 层使用情况分析

## 📊 分析概述

本文档分析 `core/` 层（业务逻辑核心层）的使用情况，识别已使用和未使用的模块。

## 📁 Core 层模块列表

Core 层包含以下模块：

1. **review_scheduler.py** - SM-2 间隔重复算法
2. **data_manager.py** - 数据管理业务层
3. **export_handler.py** - 导出 PDF/Excel 功能
4. **import_parser.py** - CSV/图片批量导入

## ✅ 已使用的模块

### 1. ReviewScheduler (review_scheduler.py)

**使用位置：**
- `src/mistake_book/ui/main_window.py` - 主窗口初始化
- `src/mistake_book/services/review_service.py` - 复习服务
- `demo.py` - 演示脚本
- `test_import.py` - 测试脚本

**使用方式：**
```python
# main_window.py
self.scheduler = ReviewScheduler()
self.review_service = ReviewService(self.data_manager, self.scheduler)

# review_service.py
from mistake_book.core.review_scheduler import ReviewScheduler

class ReviewService:
    def __init__(self, data_manager: DataManager, scheduler: ReviewScheduler):
        self.scheduler = scheduler
```

**功能状态：** ✅ 正常使用
- 在 ReviewService 中被使用
- 实现 SM-2 算法
- 计算下次复习时间

### 2. DataManager (data_manager.py)

**使用位置：**
- `src/mistake_book/ui/main_window.py` - 主窗口初始化
- `src/mistake_book/services/question_service.py` - 错题服务
- `src/mistake_book/services/review_service.py` - 复习服务
- `src/mistake_book/services/ui_service.py` - UI 服务
- `test_import.py` - 测试脚本

**使用方式：**
```python
# main_window.py
self.data_manager = DataManager(self.db_manager)

# 各个服务层
class QuestionService:
    def __init__(self, data_manager: DataManager, ...):
        self.data_manager = data_manager

class ReviewService:
    def __init__(self, data_manager: DataManager, ...):
        self.data_manager = data_manager

class UIService:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
```

**功能状态：** ✅ 正常使用
- 所有服务层都依赖它
- 封装数据库操作
- 提供增删改查接口

## ❌ 未使用的模块

### 1. ExportHandler (export_handler.py)

**当前状态：** ❌ 未被使用

**代码内容：**
```python
class ExportHandler:
    """导出处理器"""
    
    def export_to_pdf(self, questions: List[Dict[str, Any]], output_path: Path):
        """导出为PDF"""
        # TODO: 使用reportlab或其他库实现
        pass
    
    def export_to_excel(self, questions: List[Dict[str, Any]], output_path: Path):
        """导出为Excel"""
        # TODO: 使用openpyxl实现
        pass
```

**问题分析：**
1. 方法体为空（只有 TODO 注释）
2. 没有任何地方导入或使用
3. 主窗口有"导出"按钮，但未连接功能

**建议：**
- 需要实现导出功能
- 应该创建 `ExportService` 封装导出逻辑
- 在主窗口的导出按钮中调用

### 2. ImportParser (import_parser.py)

**当前状态：** ❌ 未被使用

**代码内容：**
```python
class ImportParser:
    """导入解析器"""
    
    def parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """解析CSV文件"""
        questions = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
        return questions
    
    def parse_images(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """批量解析图片（需要OCR）"""
        # TODO: 集成OCR服务
        return []
```

**问题分析：**
1. `parse_csv()` 有基本实现，但未被使用
2. `parse_images()` 只有 TODO，未实现
3. 没有任何地方导入或使用
4. 缺少批量导入的 UI 入口

**建议：**
- 需要创建 `ImportService` 封装导入逻辑
- 在主窗口添加"批量导入"功能
- 完善图片批量导入功能

## 📈 使用率统计

| 模块 | 状态 | 使用次数 | 完成度 |
|------|------|----------|--------|
| ReviewScheduler | ✅ 使用中 | 3 处 | 100% |
| DataManager | ✅ 使用中 | 5 处 | 100% |
| ExportHandler | ❌ 未使用 | 0 处 | 0% (TODO) |
| ImportParser | ❌ 未使用 | 0 处 | 30% (部分实现) |

**总体使用率：** 50% (2/4 模块被使用)

## 🎯 架构分析

### 当前架构

```
UI Layer (MainWindow)
    ↓
Service Layer (QuestionService, ReviewService, UIService)
    ↓
Core Layer (DataManager, ReviewScheduler)
    ↓
Database Layer (DatabaseManager)
```

**已使用的 Core 模块：**
- DataManager: 被所有服务层使用
- ReviewScheduler: 被 ReviewService 使用

**未使用的 Core 模块：**
- ExportHandler: 未集成到服务层
- ImportParser: 未集成到服务层

### 理想架构

```
UI Layer
    ↓
Service Layer
    ├── QuestionService (使用 DataManager)
    ├── ReviewService (使用 DataManager, ReviewScheduler)
    ├── UIService (使用 DataManager)
    ├── ExportService (使用 ExportHandler, DataManager) ← 缺失
    └── ImportService (使用 ImportParser, DataManager) ← 缺失
    ↓
Core Layer
    ├── DataManager ✅
    ├── ReviewScheduler ✅
    ├── ExportHandler ❌ 未使用
    └── ImportParser ❌ 未使用
    ↓
Database Layer
```

## 💡 改进建议

### 1. 实现导出功能

**步骤：**

1. **完善 ExportHandler**
   ```python
   # core/export_handler.py
   class ExportHandler:
       def export_to_pdf(self, questions, output_path):
           # 使用 reportlab 实现
           pass
       
       def export_to_excel(self, questions, output_path):
           # 使用 openpyxl 实现
           pass
   ```

2. **创建 ExportService**
   ```python
   # services/export_service.py
   class ExportService:
       def __init__(self, data_manager, export_handler):
           self.data_manager = data_manager
           self.export_handler = export_handler
       
       def export_questions_to_pdf(self, filters, output_path):
           questions = self.data_manager.search_questions(filters)
           return self.export_handler.export_to_pdf(questions, output_path)
       
       def export_questions_to_excel(self, filters, output_path):
           questions = self.data_manager.search_questions(filters)
           return self.export_handler.export_to_excel(questions, output_path)
   ```

3. **在 MainWindow 中集成**
   ```python
   # ui/main_window.py
   def __init__(self):
       # ...
       self.export_service = ExportService(self.data_manager, ExportHandler())
   
   def on_export_clicked(self):
       # 显示导出对话框
       # 调用 export_service
       pass
   ```

### 2. 实现批量导入功能

**步骤：**

1. **完善 ImportParser**
   ```python
   # core/import_parser.py
   class ImportParser:
       def __init__(self, ocr_engine=None):
           self.ocr_engine = ocr_engine
       
       def parse_csv(self, file_path):
           # 已有基本实现，需要验证和错误处理
           pass
       
       def parse_images(self, image_paths):
           # 使用 OCR 引擎批量识别
           results = []
           for path in image_paths:
               text = self.ocr_engine.recognize(path)
               results.append({'content': text, ...})
           return results
   ```

2. **创建 ImportService**
   ```python
   # services/import_service.py
   class ImportService:
       def __init__(self, data_manager, import_parser):
           self.data_manager = data_manager
           self.import_parser = import_parser
       
       def import_from_csv(self, file_path):
           questions = self.import_parser.parse_csv(file_path)
           # 验证和保存
           for q in questions:
               self.data_manager.add_question(q)
       
       def import_from_images(self, image_paths):
           questions = self.import_parser.parse_images(image_paths)
           # 验证和保存
           for q in questions:
               self.data_manager.add_question(q)
   ```

3. **在 MainWindow 中集成**
   ```python
   # ui/main_window.py
   def __init__(self):
       # ...
       self.import_service = ImportService(self.data_manager, ImportParser(ocr_engine))
   
   def on_import_clicked(self):
       # 显示文件选择对话框
       # 调用 import_service
       pass
   ```

### 3. 添加依赖库

**导出功能需要：**
```txt
# dependencies/requirements.txt
reportlab>=3.6.0  # PDF 导出
openpyxl>=3.0.0   # Excel 导出
```

**批量导入需要：**
```txt
# dependencies/requirements.txt
# CSV 导入使用标准库 csv，无需额外依赖
# 图片导入使用已有的 OCR 引擎
```

## 📝 总结

### 现状

- ✅ **DataManager** 和 **ReviewScheduler** 被充分使用
- ❌ **ExportHandler** 和 **ImportParser** 完全未使用
- 主窗口有导出按钮，但功能未实现
- 缺少批量导入的 UI 入口

### 原因分析

1. **功能未完成**: ExportHandler 和 ImportParser 只有框架，未实现
2. **缺少服务层**: 没有 ExportService 和 ImportService 封装
3. **UI 未集成**: 主窗口未连接这些功能

### 优先级建议

**高优先级：**
1. 实现导出功能（主窗口已有按钮）
2. 创建 ExportService 和 ImportService

**中优先级：**
3. 完善 ImportParser 的图片批量导入
4. 在主窗口添加批量导入入口

**低优先级：**
5. 优化导出格式和样式
6. 支持更多导入格式

### 架构一致性

所有功能都应遵循相同的架构模式：

```
UI → Service → Core → Database
```

- UI 层：只负责展示和用户交互
- Service 层：封装业务逻辑，协调 Core 层
- Core 层：实现核心算法和数据处理
- Database 层：数据持久化

## 🔗 相关文档

- [backend_services.md](backend_services.md) - 后端服务架构
- [refactoring_services.md](refactoring_services.md) - 服务层重构
- [ui_optimization.md](ui_optimization.md) - UI 层优化

## 📅 更新日志

- 2024-01 - 创建 Core 层使用情况分析文档
- 分析了 4 个 Core 模块的使用情况
- 提供了改进建议和实现步骤
