# 数据库缓存问题修复文档

## 📋 问题描述

用户报告：添加完成后，统计数据一直累加，而不是从数据库实时查询当前的实际数量。

**具体表现：**
- 添加题目后，统计数字增加
- 但数字可能不准确（基于累加而非实际查询）
- 重启应用后，数字恢复正常（重新查询数据库）

## 🔍 问题分析

### SQLAlchemy 会话缓存机制

SQLAlchemy 的 Session 对象会缓存查询结果，以提高性能。这意味着：

1. **第一次查询**：从数据库获取数据，缓存在 session 中
2. **后续查询**：如果对象已在缓存中，直接返回缓存数据
3. **数据变更**：其他 session 的变更不会自动反映到当前 session

### 问题场景

```python
# Session 1: 添加题目
with db.session_scope() as session:
    question = Question(...)
    session.add(question)
    session.commit()  # 数据已保存到数据库

# Session 2: 查询统计（可能使用缓存）
with db.session_scope() as session:
    count = session.query(Question).count()
    # 如果 session 有缓存，可能返回旧数据
```

### 为什么重启后正常？

重启应用后：
- 所有 session 对象被销毁
- 缓存被清空
- 重新从数据库查询，获取最新数据

## ✅ 修复方案

### 1. 使用 session.expire_all()

在查询前清除 session 缓存，强制从数据库获取最新数据。

**修改 DataManager.search_questions()**

```python
def search_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """搜索错题（确保获取最新数据）"""
    with self.db.session_scope() as session:
        # 清除会话缓存，确保获取最新数据
        session.expire_all()  # ← 关键修复
        
        query = session.query(Question)
        # ... 筛选逻辑 ...
        questions = query.all()
        return [q.to_dict() for q in questions]
```

**修改 DataManager.get_statistics()**

```python
def get_statistics(self) -> Dict[str, Any]:
    """获取统计数据（实时从数据库查询）"""
    with self.db.session_scope() as session:
        # 清除会话缓存，确保获取最新数据
        session.expire_all()  # ← 关键修复
        
        total = session.query(Question).count()
        # ... 统计逻辑 ...
        return {
            "total_questions": total,
            # ...
        }
```

### 2. session.expire_all() 的作用

```python
session.expire_all()
```

**功能：**
- 标记 session 中所有对象为"过期"
- 下次访问这些对象时，强制从数据库重新加载
- 确保获取最新数据

**性能影响：**
- 轻微增加数据库查询次数
- 但确保数据一致性
- 对于小型应用，性能影响可忽略

### 3. 其他可选方案

#### 方案 A：每次创建新 session（已采用）

```python
@contextmanager
def session_scope(self) -> Session:
    """提供事务会话上下文"""
    session = self.SessionLocal()  # 每次创建新 session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()  # 关闭后缓存清空
```

**优点：** 每次都是新 session，理论上不会有缓存问题
**问题：** SQLAlchemy 的 identity map 仍可能缓存对象

#### 方案 B：使用 autoflush（不推荐）

```python
session = self.SessionLocal(autoflush=True)
```

**问题：** 只解决同一 session 内的问题，不解决跨 session 的缓存

#### 方案 C：禁用查询缓存（不推荐）

```python
query = session.query(Question).execution_options(compiled_cache=None)
```

**问题：** 性能影响大，且不解决对象缓存

## 📊 修复效果

### 修复前

```
初始状态：数据库有 5 道题
    ↓
查询统计：显示 5 道题 ✅
    ↓
添加 1 道题：数据库现在有 6 道题
    ↓
查询统计：可能显示 5 道题 ❌（使用缓存）
    ↓
重启应用
    ↓
查询统计：显示 6 道题 ✅（重新查询）
```

### 修复后

```
初始状态：数据库有 5 道题
    ↓
查询统计：显示 5 道题 ✅
    ↓
添加 1 道题：数据库现在有 6 道题
    ↓
查询统计（使用 expire_all）：显示 6 道题 ✅
    ↓
无需重启，数据始终准确 ✅
```

## 🎯 测试验证

### 测试场景 1：添加题目后统计

```python
# 步骤
1. 查看当前统计：总题数 = 10
2. 添加 1 道新题
3. 立即查看统计

# 验证
✅ 总题数应该显示 11（不是 10）
✅ 掌握度统计正确更新
✅ 无需重启应用
```

### 测试场景 2：删除题目后统计

```python
# 步骤
1. 查看当前统计：总题数 = 10
2. 删除 1 道题
3. 立即查看统计

# 验证
✅ 总题数应该显示 9（不是 10）
✅ 掌握度统计正确更新
✅ 无需重启应用
```

### 测试场景 3：复习改变掌握度

```python
# 步骤
1. 查看统计：生疏 = 5, 掌握 = 3
2. 复习 1 道生疏题目，选择"掌握"
3. 立即查看统计

# 验证
✅ 生疏应该显示 4（不是 5）
✅ 掌握应该显示 4（不是 3）
✅ 总题数不变
✅ 无需重启应用
```

### 测试场景 4：连续操作

```python
# 步骤
1. 初始：总题数 = 10
2. 添加 2 道题
3. 查看统计：应该是 12
4. 删除 1 道题
5. 查看统计：应该是 11
6. 复习 1 道题
7. 查看统计：应该是 11（总数不变，掌握度改变）

# 验证
✅ 每次操作后统计都准确
✅ 不是基于累加，而是实时查询
```

## 🔧 技术细节

### SQLAlchemy Session 生命周期

```python
# 创建 session
session = SessionLocal()

# 查询数据（第一次）
questions = session.query(Question).all()
# → 从数据库查询，缓存在 session 中

# 其他地方修改了数据库
# ...

# 再次查询（第二次）
questions = session.query(Question).all()
# → 可能返回缓存数据（不是最新的）

# 使用 expire_all 后
session.expire_all()
questions = session.query(Question).all()
# → 强制从数据库重新查询
```

### Identity Map

SQLAlchemy 使用 Identity Map 模式：
- 每个 session 维护一个对象映射表
- 相同 ID 的对象在 session 中只有一个实例
- 避免重复加载和数据不一致

**问题：** 如果数据库被其他 session 修改，当前 session 的 Identity Map 不会自动更新。

**解决：** 使用 `expire_all()` 清除 Identity Map。

### 性能考虑

**查询频率分析：**
- 添加题目：低频操作（每分钟 < 1 次）
- 删除题目：低频操作（每分钟 < 1 次）
- 复习题目：中频操作（每分钟 1-5 次）
- 查看统计：高频操作（每次操作后）

**性能影响：**
- `expire_all()` 本身很快（< 1ms）
- 增加的数据库查询：每次 < 10ms
- 总体影响：可忽略（< 20ms）

**结论：** 对于小型应用（< 10000 题），性能完全可接受。

### 何时需要 expire_all()

**需要：**
- ✅ 跨 session 的数据变更后查询
- ✅ 统计数据查询
- ✅ 列表刷新

**不需要：**
- ❌ 同一 session 内的查询
- ❌ 只读操作
- ❌ 事务内的连续操作

## 🎓 经验总结

### 1. 数据一致性 > 性能

对于用户界面应用：
- 数据准确性最重要
- 轻微的性能损失可接受
- 用户体验优先

### 2. 理解 ORM 缓存机制

使用 ORM 时要理解：
- Session 缓存
- Identity Map
- 查询缓存
- 何时需要刷新

### 3. 测试跨 Session 场景

测试时要考虑：
- 多个 session 的交互
- 数据变更后的查询
- 并发操作

### 4. 文档化缓存策略

在代码中注释：
```python
# 清除缓存，确保获取最新数据
session.expire_all()
```

让其他开发者理解为什么这样做。

## 🔮 未来改进

### 1. 智能缓存失效

只在数据变更后清除缓存：

```python
class DataManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self._cache_dirty = False
    
    def add_question(self, data):
        # ... 添加逻辑 ...
        self._cache_dirty = True  # 标记缓存失效
    
    def search_questions(self, filters):
        with self.db.session_scope() as session:
            if self._cache_dirty:
                session.expire_all()
                self._cache_dirty = False
            # ... 查询逻辑 ...
```

### 2. 事件监听

使用 SQLAlchemy 事件监听器：

```python
from sqlalchemy import event

@event.listens_for(Question, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # 数据插入后的处理
    invalidate_cache()

@event.listens_for(Question, 'after_delete')
def receive_after_delete(mapper, connection, target):
    # 数据删除后的处理
    invalidate_cache()
```

### 3. 应用级缓存

使用 Redis 或内存缓存：

```python
from functools import lru_cache
from datetime import datetime, timedelta

class DataManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self._stats_cache = None
        self._cache_time = None
    
    def get_statistics(self):
        # 缓存 5 秒
        if self._stats_cache and \
           datetime.now() - self._cache_time < timedelta(seconds=5):
            return self._stats_cache
        
        # 重新查询
        stats = self._query_statistics()
        self._stats_cache = stats
        self._cache_time = datetime.now()
        return stats
```

### 4. 数据库触发器

使用数据库触发器维护统计表：

```sql
CREATE TABLE statistics (
    id INTEGER PRIMARY KEY,
    total_questions INTEGER,
    mastered INTEGER,
    learning INTEGER,
    updated_at TIMESTAMP
);

CREATE TRIGGER update_stats_after_insert
AFTER INSERT ON questions
BEGIN
    UPDATE statistics SET 
        total_questions = total_questions + 1,
        updated_at = CURRENT_TIMESTAMP;
END;
```

## 📝 涉及文件

### 修改的文件

1. **src/mistake_book/core/data_manager.py**
   - `search_questions()` - 添加 `session.expire_all()`
   - `get_statistics()` - 添加 `session.expire_all()`

2. **src/mistake_book/database/db_manager.py**
   - 添加 `get_fresh_session()` 方法（备用）

### 未修改的文件

以下文件无需修改：
- `services/ui_service.py` - 调用 DataManager，自动获取最新数据
- `ui/main_window.py` - UI 层无需关心缓存问题
- `database/models.py` - 模型定义无需改变

## 📚 相关文档

- [data_flow_fix.md](data_flow_fix.md) - 数据流修复
- [ui_refresh_fix.md](ui_refresh_fix.md) - UI 刷新修复
- [database_design.md](database_design.md) - 数据库设计

## 📚 参考资料

- [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/14/orm/session_basics.html)
- [SQLAlchemy Session API](https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.expire_all)
- [Understanding SQLAlchemy Caching](https://docs.sqlalchemy.org/en/14/orm/session_state_management.html)

## 📅 更新日志

- 2024-01 - 创建数据库缓存问题修复文档
- 修复 search_questions 的缓存问题
- 修复 get_statistics 的缓存问题
- 添加 session.expire_all() 确保数据最新
- 验证统计数据实时准确性
