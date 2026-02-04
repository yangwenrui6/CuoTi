# 后端服务架构文档

## 📋 概述

错题本应用采用分层架构，后端服务分为三个主要层次：
1. **数据持久层** (Database Layer) - 数据库操作
2. **业务逻辑层** (Core Layer) - 核心业务逻辑
3. **外部服务层** (Services Layer) - 第三方服务集成

---

## 🗄️ 数据持久层 (database/)

### 1. models.py - 数据模型

**功能**: 定义SQLAlchemy ORM模型

**模型列表**:

#### Question (错题模型)
```python
class Question(Base):
    # 基本信息
    - id: 主键
    - subject: 学科（数学、物理等）
    - question_type: 题型（单选、填空等）
    - content: 题目内容
    - answer: 正确答案
    - my_answer: 我的答案
    - explanation: 解析
    - difficulty: 难度（1-5星）
    - image_path: 图片路径
    
    # 复习相关
    - mastery_level: 掌握度（0-3）
    - easiness_factor: 难度因子（SM-2算法）
    - repetitions: 重复次数
    - interval: 间隔天数
    - next_review_date: 下次复习日期
    
    # 时间戳
    - created_at: 创建时间
    - updated_at: 更新时间
    
    # 关系
    - tags: 多对多关联标签
    - reviews: 一对多关联复习记录
```

#### Tag (标签模型)
```python
class Tag(Base):
    - id: 主键
    - name: 标签名称（唯一）
    - color: 颜色（十六进制）
    
    # 关系
    - questions: 多对多关联错题
```

#### ReviewRecord (复习记录模型)
```python
class ReviewRecord(Base):
    - id: 主键
    - question_id: 外键关联错题
    - review_date: 复习日期
    - result: 复习结果（0-3）
    - time_spent: 耗时（秒）
    
    # 关系
    - question: 多对一关联错题
```

**关联表**:
- `question_tags`: 错题和标签的多对多关联表

---

### 2. db_manager.py - 数据库管理器

**功能**: 管理数据库连接、事务、备份

**类**: `DatabaseManager`

**主要方法**:

```python
class DatabaseManager:
    def __init__(self, db_path: Path)
        """初始化数据库连接"""
    
    def init_database(self)
        """创建所有表"""
    
    @contextmanager
    def session_scope(self) -> Session
        """提供事务会话上下文管理器"""
        # 自动处理commit/rollback
    
    def backup(self, backup_dir: Path) -> Path
        """备份数据库文件"""
    
    def restore(self, backup_path: Path)
        """从备份恢复数据库"""
```

**特点**:
- ✅ 连接池管理
- ✅ 自动事务处理
- ✅ 上下文管理器（with语句）
- ✅ 备份恢复功能

---

## 🧠 业务逻辑层 (core/)

### 1. review_scheduler.py - 复习调度器

**功能**: 实现SM-2间隔重复算法

**类**: `ReviewScheduler`

**主要方法**:

```python
class ReviewScheduler:
    def __init__(self, easy_bonus=1.3, interval_modifier=1.0)
        """初始化算法参数"""
    
    def calculate_next_review(
        current_interval: int,
        repetitions: int,
        easiness_factor: float,
        review_result: ReviewResult
    ) -> Tuple[int, int, float]
        """
        计算下次复习时间
        
        参数:
            - current_interval: 当前间隔天数
            - repetitions: 重复次数
            - easiness_factor: 难度因子
            - review_result: 复习结果（AGAIN/HARD/GOOD/EASY）
        
        返回:
            - 新间隔天数
            - 新重复次数
            - 新难度因子
        """
    
    def get_due_questions(self, questions: List[dict]) -> List[dict]
        """获取到期需要复习的题目"""
```

**算法逻辑**:
- AGAIN (生疏): 重置间隔，从1天开始
- HARD (困难): 稍微延长间隔
- GOOD (掌握): 标准间隔（1天→6天→按因子递增）
- EASY (熟练): 大幅延长间隔

---

### 2. data_manager.py - 数据管理器

**功能**: 封装业务层的增删改查和统计逻辑

**类**: `DataManager`

**主要方法**:

```python
class DataManager:
    def __init__(self, db_manager: DatabaseManager)
        """注入数据库管理器"""
    
    # CRUD操作
    def add_question(self, question_data: Dict) -> int
        """添加错题，返回ID"""
    
    def update_question(self, question_id: int, updates: Dict) -> bool
        """更新错题"""
    
    def delete_question(self, question_id: int) -> bool
        """删除错题"""
    
    def get_question(self, question_id: int) -> Optional[Dict]
        """获取单个错题"""
    
    # 查询操作
    def search_questions(self, filters: Dict) -> List[Dict]
        """
        搜索错题
        
        支持的筛选条件:
            - subject: 科目
            - tags: 标签列表
            - mastery_level: 掌握度
            - difficulty: 难度
        """
    
    # 统计操作
    def get_statistics(self) -> Dict[str, Any]
        """
        获取统计数据
        
        返回:
            - total_questions: 总题数
            - mastered: 已掌握数量
            - learning: 学习中数量
        """
```

**特点**:
- ✅ 业务逻辑与数据库分离
- ✅ 统一的数据接口
- ✅ 自动事务管理

---

### 3. export_handler.py - 导出处理器

**功能**: 导出错题为PDF/Excel

**类**: `ExportHandler`

**主要方法**:

```python
class ExportHandler:
    def export_to_pdf(self, questions: List[Dict], output_path: Path)
        """导出为PDF格式"""
        # TODO: 使用reportlab实现
    
    def export_to_excel(self, questions: List[Dict], output_path: Path)
        """导出为Excel格式"""
        # TODO: 使用openpyxl实现
```

**状态**: 接口已定义，待实现

---

### 4. import_parser.py - 导入解析器

**功能**: 解析CSV/图片批量导入

**类**: `ImportParser`

**主要方法**:

```python
class ImportParser:
    def parse_csv(self, file_path: Path) -> List[Dict]
        """解析CSV文件"""
    
    def parse_images(self, image_paths: List[Path]) -> List[Dict]
        """批量解析图片（需要OCR）"""
```

**状态**: 基础实现，待完善

---

## 🔌 外部服务层 (services/)

### 1. ocr_engine.py - OCR识别引擎

**功能**: 图片文字识别

**抽象基类**: `OCREngine`

```python
class OCREngine(ABC):
    @abstractmethod
    def recognize(self, image_path: Path) -> str
        """识别图片中的文字"""
```

**实现类**:

#### PaddleOCREngine
```python
class PaddleOCREngine(OCREngine):
    """PaddleOCR实现（推荐，中文支持好）"""
    
    def __init__(self)
        # 初始化PaddleOCR
        # self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    
    def recognize(self, image_path: Path) -> str
        # 调用OCR识别
        # 返回识别的文字
```

#### TesseractEngine
```python
class TesseractEngine(OCREngine):
    """Tesseract实现"""
    
    def recognize(self, image_path: Path) -> str
        # 调用pytesseract识别
```

**状态**: 接口已定义，需要安装可选依赖后启用

**安装**:
```bash
# PaddleOCR（推荐）
pip install paddleocr

# Tesseract
pip install pytesseract
```

---

### 2. notification.py - 系统通知服务

**功能**: 发送系统通知

**类**: `NotificationService`

**主要方法**:

```python
class NotificationService:
    def send_review_reminder(self, count: int)
        """
        发送复习提醒
        
        参数:
            - count: 待复习题目数量
        """
```

**依赖**: plyer库（跨平台通知）

**使用示例**:
```python
service = NotificationService()
service.send_review_reminder(15)
# 显示: "你有 15 道题目需要复习"
```

---

### 3. cloud_sync.py - 云同步服务

**功能**: 云端数据同步（预留接口）

**抽象基类**: `CloudSyncService`

```python
class CloudSyncService(ABC):
    @abstractmethod
    def upload(self, local_path: str) -> bool
        """上传到云端"""
    
    @abstractmethod
    def download(self, remote_path: str, local_path: str) -> bool
        """从云端下载"""
```

**状态**: 接口预留，待实现

**可能的实现**:
- WebDAV
- 阿里云OSS
- 腾讯云COS
- 自建服务器

---

## 🔄 服务调用流程

### 添加错题流程

```
UI层 (AddQuestionDialog)
    ↓
业务层 (DataManager.add_question)
    ↓
数据层 (DatabaseManager.session_scope)
    ↓
ORM模型 (Question)
    ↓
SQLite数据库
```

### 复习流程

```
UI层 (ReviewDialog)
    ↓
业务层 (ReviewScheduler.calculate_next_review)
    ↓
业务层 (DataManager.update_question)
    ↓
数据层 (DatabaseManager)
    ↓
数据库更新
```

### OCR识别流程

```
UI层 (AddQuestionDialog - 拖拽图片)
    ↓
工具层 (ImageProcessor.preprocess_for_ocr)
    ↓
服务层 (OCREngine.recognize)
    ↓
UI层 (自动填充表单)
```

---

## 📊 数据流向图

```
┌─────────────────────────────────────────────────┐
│                   UI Layer                      │
│  (PyQt6 - main_window, dialogs, widgets)       │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│              Business Layer                     │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ DataManager  │  │ReviewScheduler│           │
│  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ExportHandler │  │ImportParser  │           │
│  └──────────────┘  └──────────────┘           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│              Data Layer                         │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ DatabaseMgr  │  │   Models     │           │
│  └──────────────┘  └──────────────┘           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│              SQLite Database                    │
│           (mistakes.db)                         │
└─────────────────────────────────────────────────┘

         ┌──────────────────────┐
         │   Services Layer     │
         │  ┌────────────────┐  │
         │  │  OCR Engine    │  │
         │  ├────────────────┤  │
         │  │ Notification   │  │
         │  ├────────────────┤  │
         │  │  Cloud Sync    │  │
         │  └────────────────┘  │
         └──────────────────────┘
```

---

## 🎯 后端服务总结

### 已实现的服务 ✅

1. **数据持久层**
   - ✅ SQLAlchemy ORM模型
   - ✅ 数据库管理器（连接池、事务）
   - ✅ 备份恢复功能

2. **业务逻辑层**
   - ✅ SM-2复习算法
   - ✅ 数据管理器（CRUD + 统计）
   - ✅ 导入解析器（基础）

3. **外部服务层**
   - ✅ 系统通知服务
   - ✅ OCR引擎接口（待启用）
   - ✅ 云同步接口（预留）

### 待完善的功能 🚧

1. **导出功能**
   - PDF导出（需要reportlab）
   - Excel导出（需要openpyxl）

2. **OCR功能**
   - 需要安装PaddleOCR或Tesseract
   - 需要在UI层集成调用

3. **云同步**
   - 选择云存储方案
   - 实现具体的上传下载逻辑

### 技术栈

- **ORM**: SQLAlchemy 2.0+
- **数据库**: SQLite
- **通知**: plyer
- **OCR**: PaddleOCR / Tesseract（可选）
- **导出**: reportlab / openpyxl（可选）

---

## 📚 相关文档

- [项目结构](../PROJECT_STRUCTURE.md) - 完整目录结构
- [架构设计](architecture.md) - 整体架构说明
- [GUI设计](gui_design.md) - 前端界面设计
