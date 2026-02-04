# 数据库设计文档

## 📋 概述

错题本应用使用 **SQLite** 作为数据库，通过 **SQLAlchemy ORM** 进行数据操作。

- **数据库引擎**: SQLite
- **ORM框架**: SQLAlchemy 2.0+
- **数据库文件**: `mistakes.db`
- **存储位置**: 用户数据目录（跨平台）

---

## 🗂️ 数据库架构

### ER图（实体关系图）

```
┌─────────────────┐         ┌─────────────────┐
│    Question     │         │      Tag        │
│   (错题表)      │◄───────►│    (标签表)     │
└─────────────────┘    M:N  └─────────────────┘
         │                           ▲
         │ 1:N                       │
         ▼                           │
┌─────────────────┐                 │
│  ReviewRecord   │                 │
│  (复习记录表)   │                 │
└─────────────────┘                 │
                                    │
         ┌──────────────────────────┘
         │
┌─────────────────┐
│ question_tags   │
│  (关联表)       │
└─────────────────┘
```

---

## 📊 数据表详细设计

### 1. questions (错题表)

**用途**: 存储错题的完整信息

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| **id** | INTEGER | PRIMARY KEY | 自增 | 主键 |
| **subject** | VARCHAR(50) | NOT NULL | - | 学科（数学、物理等） |
| **question_type** | VARCHAR(20) | - | - | 题型（单选、填空等） |
| **content** | TEXT | NOT NULL | - | 题目内容 |
| **answer** | TEXT | - | - | 正确答案 |
| **my_answer** | TEXT | - | - | 我的答案 |
| **explanation** | TEXT | - | - | 解析 |
| **difficulty** | INTEGER | - | 3 | 难度（1-5星） |
| **image_path** | VARCHAR(500) | - | - | 图片路径 |
| **mastery_level** | INTEGER | - | 0 | 掌握度（0-3） |
| **easiness_factor** | FLOAT | - | 2.5 | 难度因子（SM-2算法） |
| **repetitions** | INTEGER | - | 0 | 重复次数 |
| **interval** | INTEGER | - | 0 | 间隔天数 |
| **next_review_date** | DATETIME | - | NULL | 下次复习日期 |
| **created_at** | DATETIME | - | NOW() | 创建时间 |
| **updated_at** | DATETIME | - | NOW() | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_subject ON questions(subject);
CREATE INDEX idx_mastery_level ON questions(mastery_level);
CREATE INDEX idx_next_review_date ON questions(next_review_date);
```

**字段说明**:

#### 基本信息字段
- `subject`: 学科分类，如"数学"、"物理"、"化学"等
- `question_type`: 题型，如"单选题"、"填空题"、"简答题"等
- `content`: 题目的完整内容
- `answer`: 标准答案
- `my_answer`: 用户的错误答案（用于对比学习）
- `explanation`: 题目解析，帮助理解
- `difficulty`: 主观难度评级，1-5星
- `image_path`: 题目图片的存储路径（可选）

#### 复习算法字段（SM-2算法）
- `mastery_level`: 掌握度等级
  - 0: 生疏（完全不会）
  - 1: 学习中（有点难）
  - 2: 掌握（基本会做）
  - 3: 熟练（完全掌握）

- `easiness_factor`: 难度因子（1.3-2.5）
  - 用于计算下次复习间隔
  - 根据复习结果动态调整

- `repetitions`: 已复习次数
  - 用于判断复习阶段

- `interval`: 当前复习间隔（天数）
  - 下次复习距离上次的天数

- `next_review_date`: 下次复习的具体日期
  - 用于筛选到期题目

#### 时间戳字段
- `created_at`: 记录创建时间
- `updated_at`: 最后更新时间（自动更新）

---

### 2. tags (标签表)

**用途**: 存储标签信息，用于分类管理

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| **id** | INTEGER | PRIMARY KEY | 自增 | 主键 |
| **name** | VARCHAR(50) | UNIQUE, NOT NULL | - | 标签名称 |
| **color** | VARCHAR(7) | - | #3498db | 颜色（十六进制） |

**索引**:
```sql
CREATE UNIQUE INDEX idx_tag_name ON tags(name);
```

**字段说明**:
- `name`: 标签名称，如"代数"、"函数"、"力学"等，必须唯一
- `color`: 标签显示颜色，格式为 #RRGGBB

**预设标签示例**:
```python
常用标签 = [
    ("代数", "#e74c3c"),
    ("几何", "#3498db"),
    ("函数", "#2ecc71"),
    ("力学", "#f39c12"),
    ("电学", "#9b59b6"),
]
```

---

### 3. review_records (复习记录表)

**用途**: 记录每次复习的详细信息

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| **id** | INTEGER | PRIMARY KEY | 自增 | 主键 |
| **question_id** | INTEGER | FOREIGN KEY | - | 关联错题ID |
| **review_date** | DATETIME | - | NOW() | 复习时间 |
| **result** | INTEGER | - | - | 复习结果（0-3） |
| **time_spent** | INTEGER | - | - | 耗时（秒） |

**外键约束**:
```sql
FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
```

**索引**:
```sql
CREATE INDEX idx_question_id ON review_records(question_id);
CREATE INDEX idx_review_date ON review_records(review_date);
```

**字段说明**:
- `question_id`: 关联的错题ID，删除错题时级联删除记录
- `review_date`: 复习的具体时间
- `result`: 复习结果
  - 0: AGAIN（生疏）
  - 1: HARD（困难）
  - 2: GOOD（掌握）
  - 3: EASY（熟练）
- `time_spent`: 复习该题花费的时间（秒）

---

### 4. question_tags (关联表)

**用途**: 实现错题和标签的多对多关系

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| **question_id** | INTEGER | FOREIGN KEY | 错题ID |
| **tag_id** | INTEGER | FOREIGN KEY | 标签ID |

**外键约束**:
```sql
FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
```

**联合主键**:
```sql
PRIMARY KEY (question_id, tag_id)
```

**索引**:
```sql
CREATE INDEX idx_qt_question ON question_tags(question_id);
CREATE INDEX idx_qt_tag ON question_tags(tag_id);
```

---

## 🔗 表关系说明

### 1. Question ↔ Tag (多对多)

**关系**: 一道错题可以有多个标签，一个标签可以关联多道错题

**实现**: 通过 `question_tags` 关联表

**示例**:
```python
# 一道题有多个标签
question = session.query(Question).first()
print(question.tags)  # [Tag("代数"), Tag("函数")]

# 一个标签关联多道题
tag = session.query(Tag).filter_by(name="代数").first()
print(tag.questions)  # [Question1, Question2, ...]
```

### 2. Question → ReviewRecord (一对多)

**关系**: 一道错题可以有多条复习记录

**实现**: ReviewRecord 表中的 `question_id` 外键

**示例**:
```python
# 查询某题的所有复习记录
question = session.query(Question).first()
print(question.reviews)  # [ReviewRecord1, ReviewRecord2, ...]

# 查询某条记录对应的题目
record = session.query(ReviewRecord).first()
print(record.question)  # Question对象
```

---

## 📈 数据库操作示例

### 创建错题

```python
from mistake_book.database.models import Question, Tag
from mistake_book.database.db_manager import DatabaseManager

db = DatabaseManager("mistakes.db")

with db.session_scope() as session:
    # 创建错题
    question = Question(
        subject="数学",
        question_type="单选题",
        content="求函数 f(x)=x²+2x+1 的最小值",
        answer="0",
        my_answer="1",
        explanation="配方法: f(x)=(x+1)²，最小值为0",
        difficulty=3
    )
    
    # 添加标签
    tag1 = session.query(Tag).filter_by(name="函数").first()
    if not tag1:
        tag1 = Tag(name="函数", color="#3498db")
        session.add(tag1)
    
    question.tags.append(tag1)
    
    session.add(question)
    # 自动commit
```

### 查询错题

```python
# 查询所有数学题
with db.session_scope() as session:
    questions = session.query(Question).filter_by(subject="数学").all()

# 查询需要复习的题目
from datetime import datetime

with db.session_scope() as session:
    due_questions = session.query(Question).filter(
        Question.next_review_date <= datetime.now()
    ).all()

# 按标签查询
with db.session_scope() as session:
    tag = session.query(Tag).filter_by(name="代数").first()
    questions = tag.questions
```

### 更新复习数据

```python
from mistake_book.config.constants import ReviewResult

with db.session_scope() as session:
    question = session.query(Question).get(1)
    
    # 更新复习数据
    question.mastery_level = ReviewResult.GOOD.value
    question.repetitions += 1
    question.interval = 6
    question.next_review_date = datetime.now() + timedelta(days=6)
    
    # 添加复习记录
    record = ReviewRecord(
        question_id=question.id,
        result=ReviewResult.GOOD.value,
        time_spent=120  # 2分钟
    )
    session.add(record)
```

### 统计查询

```python
# 统计各科目题目数量
with db.session_scope() as session:
    from sqlalchemy import func
    
    stats = session.query(
        Question.subject,
        func.count(Question.id)
    ).group_by(Question.subject).all()
    
    for subject, count in stats:
        print(f"{subject}: {count}道题")

# 统计掌握度分布
with db.session_scope() as session:
    mastery_stats = session.query(
        Question.mastery_level,
        func.count(Question.id)
    ).group_by(Question.mastery_level).all()
```

---

## 🔒 数据完整性

### 外键约束

1. **级联删除**: 删除错题时，自动删除相关的复习记录和标签关联
2. **引用完整性**: 确保 question_id 和 tag_id 必须存在

### 唯一性约束

1. **标签名称唯一**: 防止重复创建相同标签
2. **联合主键**: question_tags 表防止重复关联

### 非空约束

1. **必填字段**: subject, content 必须填写
2. **默认值**: 为可选字段提供合理默认值

---

## 💾 数据备份策略

### 自动备份

```python
from pathlib import Path
from datetime import datetime

# 每周自动备份
backup_dir = Path("backups")
backup_path = db.backup(backup_dir)
print(f"备份成功: {backup_path}")
```

### 备份文件命名

格式: `backup_YYYYMMDD_HHMMSS.db`

示例: `backup_20240115_143022.db`

### 恢复数据

```python
# 从备份恢复
backup_file = Path("backups/backup_20240115_143022.db")
db.restore(backup_file)
```

---

## 📊 数据库性能优化

### 索引策略

1. **常用查询字段**: subject, mastery_level, next_review_date
2. **外键字段**: question_id, tag_id
3. **唯一字段**: tag.name

### 查询优化

```python
# 使用索引查询
session.query(Question).filter_by(subject="数学")  # 使用索引

# 预加载关联数据（避免N+1问题）
from sqlalchemy.orm import joinedload

questions = session.query(Question).options(
    joinedload(Question.tags),
    joinedload(Question.reviews)
).all()
```

### 批量操作

```python
# 批量插入
questions = [
    Question(subject="数学", content="题目1"),
    Question(subject="物理", content="题目2"),
]
session.bulk_save_objects(questions)
```

---

## 🔄 数据迁移

### 版本升级

如果需要修改表结构，使用 Alembic 进行迁移：

```bash
# 初始化迁移
alembic init migrations

# 创建迁移脚本
alembic revision --autogenerate -m "添加新字段"

# 执行迁移
alembic upgrade head
```

### 数据导入导出

```python
# 导出为JSON
import json

with db.session_scope() as session:
    questions = session.query(Question).all()
    data = [q.to_dict() for q in questions]
    
    with open("export.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 从JSON导入
with open("export.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    
with db.session_scope() as session:
    for item in data:
        question = Question(**item)
        session.add(question)
```

---

## 📝 数据库维护

### 定期维护任务

1. **清理过期数据**: 删除很久以前的复习记录
2. **优化数据库**: SQLite VACUUM 命令
3. **检查完整性**: PRAGMA integrity_check

```python
# 清理6个月前的复习记录
from datetime import timedelta

six_months_ago = datetime.now() - timedelta(days=180)

with db.session_scope() as session:
    session.query(ReviewRecord).filter(
        ReviewRecord.review_date < six_months_ago
    ).delete()

# 优化数据库
import sqlite3
conn = sqlite3.connect("mistakes.db")
conn.execute("VACUUM")
conn.close()
```

---

## 📚 相关文档

- [后端服务](backend_services.md) - 后端服务架构
- [数据模型代码](../src/mistake_book/database/models.py) - ORM模型实现
- [数据库管理器](../src/mistake_book/database/db_manager.py) - 数据库操作
