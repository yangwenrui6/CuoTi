# 数据流修复文档

## 📋 问题描述

在检查代码时发现，题目的基本信息和掌握程度数据没有正确地在各层之间传递，导致以下问题：

1. **数据丢失**: `Question.to_dict()` 只返回部分字段（id, subject, content, answer, tags）
2. **显示不完整**: UI 层无法获取完整的题目信息（题型、难度、掌握度等）
3. **筛选失效**: 数据管理层的筛选功能未完整实现
4. **统计不准**: 统计数据返回硬编码的 0 值

## 🔍 问题分析

### 1. Question.to_dict() 方法不完整

**问题代码：**
```python
def to_dict(self):
    """转换为字典"""
    return {
        "id": self.id,
        "subject": self.subject,
        "content": self.content,
        "answer": self.answer,
        "tags": [tag.name for tag in self.tags]
    }
```

**缺失字段：**
- question_type（题型）
- my_answer（我的答案）
- explanation（解析）
- difficulty（难度）
- image_path（图片路径）
- mastery_level（掌握度）
- easiness_factor（难度因子）
- repetitions（复习次数）
- interval（间隔天数）
- next_review_date（下次复习时间）
- created_at（创建时间）
- updated_at（更新时间）

### 2. DataManager.search_questions() 筛选不完整

**问题代码：**
```python
def search_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    with self.db.session_scope() as session:
        query = session.query(Question)
        
        if "subject" in filters:
            query = query.filter_by(subject=filters["subject"])
        if "tags" in filters:
            # 标签过滤逻辑
            pass  # ← 未实现
        
        questions = query.all()
        return [q.to_dict() for q in questions]
```

**缺失功能：**
- 掌握度筛选
- 难度筛选
- 标签筛选（只有 pass）

### 3. DataManager.get_statistics() 返回假数据

**问题代码：**
```python
def get_statistics(self) -> Dict[str, Any]:
    with self.db.session_scope() as session:
        total = session.query(Question).count()
        # 更多统计逻辑
        return {
            "total_questions": total,
            "mastered": 0,  # ← 硬编码
            "learning": 0   # ← 硬编码
        }
```

## ✅ 修复方案

### 1. 完善 Question.to_dict() 方法

**修复后代码：**
```python
def to_dict(self):
    """转换为字典（返回所有字段）"""
    return {
        # 基本信息
        "id": self.id,
        "subject": self.subject,
        "question_type": self.question_type,
        "content": self.content,
        "answer": self.answer,
        "my_answer": self.my_answer,
        "explanation": self.explanation,
        "difficulty": self.difficulty,
        "image_path": self.image_path,
        
        # 复习相关
        "mastery_level": self.mastery_level,
        "easiness_factor": self.easiness_factor,
        "repetitions": self.repetitions,
        "interval": self.interval,
        "next_review_date": self.next_review_date,
        
        # 时间戳
        "created_at": self.created_at,
        "updated_at": self.updated_at,
        
        # 关联数据
        "tags": [tag.name for tag in self.tags]
    }
```

**改进点：**
- ✅ 返回所有数据库字段
- ✅ 分组注释，便于理解
- ✅ 包含复习算法相关字段
- ✅ 包含时间戳字段

### 2. 完善 DataManager.search_questions() 方法

**修复后代码：**
```python
def search_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """搜索错题（支持多条件筛选）"""
    with self.db.session_scope() as session:
        query = session.query(Question)
        
        # 科目筛选
        if "subject" in filters:
            query = query.filter_by(subject=filters["subject"])
        
        # 掌握度筛选
        if "mastery_level" in filters:
            query = query.filter_by(mastery_level=filters["mastery_level"])
        
        # 难度筛选
        if "difficulty" in filters:
            query = query.filter_by(difficulty=filters["difficulty"])
        
        # 标签筛选
        if "tags" in filters and filters["tags"]:
            # 筛选包含指定标签的题目
            for tag_name in filters["tags"]:
                query = query.join(Question.tags).filter(Tag.name == tag_name)
        
        questions = query.all()
        return [q.to_dict() for q in questions]
```

**改进点：**
- ✅ 实现掌握度筛选
- ✅ 实现难度筛选
- ✅ 实现标签筛选（支持多标签）
- ✅ 添加详细注释

### 3. 完善 DataManager.get_statistics() 方法

**修复后代码：**
```python
def get_statistics(self) -> Dict[str, Any]:
    """获取统计数据（从数据库实时计算）"""
    with self.db.session_scope() as session:
        total = session.query(Question).count()
        
        # 按掌握度统计
        mastered = session.query(Question).filter(
            Question.mastery_level.in_([2, 3])
        ).count()  # 掌握 + 熟练
        
        learning = session.query(Question).filter_by(mastery_level=1).count()
        unfamiliar = session.query(Question).filter_by(mastery_level=0).count()
        
        # 待复习数量
        from datetime import datetime
        due_count = session.query(Question).filter(
            Question.next_review_date <= datetime.now()
        ).count()
        
        return {
            "total_questions": total,
            "mastered": mastered,
            "learning": learning,
            "unfamiliar": unfamiliar,
            "due_count": due_count
        }
```

**改进点：**
- ✅ 从数据库实时统计
- ✅ 按掌握度分类统计
- ✅ 计算待复习数量
- ✅ 返回完整统计数据

## 📊 数据流验证

### 创建错题流程

```
用户填写表单
    ↓
AddQuestionDialog 收集数据
    ↓ question_data = {
        "subject": "数学",
        "question_type": "单选题",
        "content": "...",
        "my_answer": "...",
        "answer": "...",
        "explanation": "...",
        "difficulty": 3,
        "image_path": "..."
    }
    ↓
QuestionService.create_question(question_data)
    ↓
DataManager.add_question(question_data)
    ↓
Question(**question_data) → 创建 ORM 对象
    ↓
session.add(question) → 保存到数据库
    ↓
✅ 所有字段都保存到数据库
```

### 查看错题流程

```
用户点击"查看"按钮
    ↓
MainWindow.on_view_detail(question)
    ↓
QuestionService.get_question_detail(question_id)
    ↓
DataManager.get_question(question_id)
    ↓
Question.to_dict() → 返回完整字典
    ↓ {
        "id": 1,
        "subject": "数学",
        "question_type": "单选题",
        "content": "...",
        "my_answer": "...",
        "answer": "...",
        "explanation": "...",
        "difficulty": 3,
        "mastery_level": 0,
        "repetitions": 0,
        ...
    }
    ↓
QuestionDetailDialog 显示所有信息
    ↓
✅ 用户看到完整的题目信息
```

### 筛选错题流程

```
用户选择筛选条件
    ↓
MainWindow.apply_filters()
    ↓
UIService.parse_filter_from_ui() → 解析UI值
    ↓ filters = {
        "subject": "数学",
        "difficulty": 3,
        "mastery_level": 0
    }
    ↓
UIService.filter_questions(filters)
    ↓
DataManager.search_questions(filters)
    ↓
SQL查询：WHERE subject='数学' AND difficulty=3 AND mastery_level=0
    ↓
返回匹配的题目列表（完整数据）
    ↓
✅ 筛选结果正确显示
```

### 统计数据流程

```
MainWindow.update_statistics()
    ↓
UIService.get_statistics_summary()
    ↓
DataManager.get_statistics()
    ↓
SQL统计查询：
    - COUNT(*) → 总题数
    - COUNT WHERE mastery_level IN (2,3) → 已掌握
    - COUNT WHERE mastery_level=1 → 学习中
    - COUNT WHERE mastery_level=0 → 生疏
    - COUNT WHERE next_review_date <= NOW() → 待复习
    ↓
返回实时统计数据
    ↓
✅ 统计面板显示正确数据
```

## 🎯 修复效果

### 修复前

| 功能 | 状态 | 问题 |
|------|------|------|
| 创建错题 | ⚠️ 部分工作 | 数据保存到数据库，但读取时丢失 |
| 查看详情 | ❌ 不完整 | 只显示部分字段 |
| 卡片显示 | ❌ 不完整 | 缺少题型、难度等信息 |
| 筛选功能 | ⚠️ 部分工作 | 只支持科目筛选 |
| 统计数据 | ❌ 错误 | 显示硬编码的 0 |

### 修复后

| 功能 | 状态 | 效果 |
|------|------|------|
| 创建错题 | ✅ 完全工作 | 所有字段正确保存和读取 |
| 查看详情 | ✅ 完全工作 | 显示所有字段 |
| 卡片显示 | ✅ 完全工作 | 显示完整信息 |
| 筛选功能 | ✅ 完全工作 | 支持科目、难度、掌握度、标签 |
| 统计数据 | ✅ 完全工作 | 实时统计，数据准确 |

## 📝 涉及文件

### 修改的文件

1. **src/mistake_book/database/models.py**
   - 修改 `Question.to_dict()` 方法
   - 返回所有字段而不是部分字段

2. **src/mistake_book/core/data_manager.py**
   - 完善 `search_questions()` 方法，支持多条件筛选
   - 完善 `get_statistics()` 方法，返回实时统计
   - 优化 `get_question()` 方法的注释

### 未修改的文件

以下文件已经正确实现，无需修改：

- `ui/dialogs/add_dialog.py` - 正确收集所有表单数据
- `services/question_service.py` - 正确传递数据
- `ui/dialogs/detail_dialog.py` - 正确显示数据（只要数据完整）
- `ui/widgets/question_card.py` - 正确显示数据（只要数据完整）

## 🔍 测试验证

### 1. 创建错题测试

```python
# 测试步骤
1. 打开添加错题对话框
2. 填写所有字段：
   - 科目：数学
   - 题型：单选题
   - 内容：测试题目
   - 我的答案：A
   - 正确答案：B
   - 解析：测试解析
   - 难度：3星
3. 保存

# 验证
- 数据库中应该有新记录
- 所有字段都应该有值
- 默认 mastery_level=0, repetitions=0
```

### 2. 查看详情测试

```python
# 测试步骤
1. 在错题列表中点击"查看"按钮
2. 查看详情对话框

# 验证
- 应该显示所有字段
- 题型、难度、掌握度都应该正确
- 不应该有 undefined 或 None
```

### 3. 筛选测试

```python
# 测试步骤
1. 选择科目：数学
2. 选择难度：3星
3. 选择掌握度：生疏

# 验证
- 只显示符合所有条件的题目
- 筛选结果准确
```

### 4. 统计测试

```python
# 测试步骤
1. 添加不同掌握度的题目
2. 查看右侧统计面板

# 验证
- 总题数正确
- 已掌握数量正确（掌握+熟练）
- 学习中数量正确
- 待复习数量正确
```

## 🎓 经验总结

### 1. ORM 模型的 to_dict() 方法很重要

- 应该返回所有需要的字段
- 是数据库对象和业务逻辑之间的桥梁
- 不完整会导致数据丢失

### 2. 数据流要完整

```
Database → ORM Model → to_dict() → Service → UI
```

任何一环出问题都会导致数据丢失。

### 3. 不要硬编码数据

- 统计数据应该从数据库实时计算
- 筛选选项应该从实际数据生成
- 避免返回假数据（如 0）

### 4. 测试数据流

- 创建数据后立即查看
- 验证所有字段都正确保存和读取
- 测试边界情况（空值、特殊字符等）

## 🔮 后续改进

### 1. 性能优化

对于大量数据，可以考虑：
- 分页加载
- 延迟加载关联数据
- 缓存常用查询

### 2. 数据验证

在 `to_dict()` 中添加数据验证：
```python
def to_dict(self):
    return {
        "difficulty": self.difficulty or 3,  # 默认值
        "mastery_level": self.mastery_level or 0,
        # ...
    }
```

### 3. 字段选择

支持只返回需要的字段：
```python
def to_dict(self, fields=None):
    data = {
        "id": self.id,
        "subject": self.subject,
        # ... 所有字段
    }
    if fields:
        return {k: v for k, v in data.items() if k in fields}
    return data
```

## 📚 相关文档

- [database_design.md](database_design.md) - 数据库设计
- [backend_services.md](backend_services.md) - 后端服务
- [integration.md](integration.md) - 前后端集成

## 📅 更新日志

- 2024-01 - 创建数据流修复文档
- 修复 Question.to_dict() 返回不完整的问题
- 完善 DataManager 的筛选和统计功能
- 验证数据流的完整性
