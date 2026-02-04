# 视图状态持久化

## 修改日期
2026-02-03

## 问题描述
在添加或删除错题后,界面会自动跳转到显示全部题目,丢失了用户当前的筛选/搜索状态。这导致用户体验不佳,需要重新进行筛选操作。

## 解决方案

### 1. 添加视图状态追踪
在 `MainWindow` 类中添加状态变量:

```python
# 当前视图状态
self.current_view_type = "all"  # all, search, nav_filter, filter
self.current_search_text = ""
self.current_nav_filter = None
```

### 2. 在各个操作中记录状态

#### 搜索操作
```python
def on_search(self, text):
    self.current_view_type = "search"
    self.current_search_text = text
    questions = self.ui_service.search_questions(text)
    self.display_questions(questions)
```

#### 导航树筛选
```python
def on_nav_item_clicked(self, item, column):
    self.current_view_type = "nav_filter"
    filters = {...}
    self.current_nav_filter = filters
    questions = self.ui_service.filter_questions(filters)
    self.display_questions(questions)
```

#### 右侧筛选面板
```python
def apply_filters(self):
    self.current_view_type = "filter"
    filters = self.ui_service.parse_filter_from_ui(...)
    questions = self.ui_service.filter_questions(filters)
    self.display_questions(questions)
```

### 3. 实现智能刷新方法

```python
def refresh_current_view(self):
    """刷新当前视图 - 保持筛选状态"""
    if self.current_view_type == "search":
        # 重新执行搜索
        questions = self.ui_service.search_questions(self.current_search_text)
        self.display_questions(questions)
    elif self.current_view_type == "nav_filter":
        # 重新应用导航筛选
        questions = self.ui_service.filter_questions(self.current_nav_filter)
        self.display_questions(questions)
    elif self.current_view_type == "filter":
        # 重新应用右侧筛选
        self.apply_filters()
    else:
        # 默认显示全部
        questions = self.ui_service.get_all_questions()
        self.display_questions(questions)
    
    # 更新统计和导航树
    self.update_statistics()
    self.refresh_navigation()
```

### 4. 在关键操作中使用智能刷新

#### 添加题目后
```python
def show_add_dialog(self):
    dialog = AddQuestionDialog(self.question_service, self)
    if dialog.exec():
        self.refresh_current_view()  # 保持当前筛选状态
        self.statusBar().showMessage("添加成功", 3000)
```

#### 删除题目后
```python
def on_delete_question(self, question):
    if success:
        self.refresh_current_view()  # 保持当前筛选状态
        self.statusBar().showMessage("删除成功", 3000)
```

#### 复习完成后
```python
def start_review(self):
    dialog = ReviewDialog(self.review_service, self)
    dialog.exec()
    self.refresh_current_view()  # 保持当前筛选状态
```

## 用户体验改进

### 修改前
1. 用户在"数学"分类下浏览题目
2. 删除一道数学题
3. 界面跳转到显示全部题目
4. 用户需要重新点击"数学"分类

### 修改后
1. 用户在"数学"分类下浏览题目
2. 删除一道数学题
3. 界面仍然显示"数学"分类的题目
4. 用户可以继续浏览

## 支持的视图类型

1. **all**: 显示全部题目
2. **search**: 搜索结果视图
3. **nav_filter**: 导航树筛选视图(科目/标签/掌握度)
4. **filter**: 右侧筛选面板视图(科目+难度+掌握度组合)

## 技术实现细节

### 状态变量说明
- `current_view_type`: 当前视图类型
- `current_search_text`: 当前搜索关键词
- `current_nav_filter`: 当前导航树筛选条件(字典)

### 刷新逻辑
1. 根据 `current_view_type` 判断当前视图类型
2. 使用保存的状态参数重新执行相应的查询
3. 更新题目列表、统计信息和导航树

### 注意事项
1. 每次用户切换视图时,都会更新状态变量
2. `load_questions()` 方法会重置状态为 "all"
3. `refresh_current_view()` 方法会保持当前状态

## 相关文件
- `src/mistake_book/ui/main_window.py`

## 测试场景

### 场景1: 搜索后添加
1. 搜索"函数"
2. 添加一道新题目
3. 验证: 仍然显示搜索"函数"的结果

### 场景2: 分类筛选后删除
1. 点击"数学"分类
2. 删除一道数学题
3. 验证: 仍然显示数学分类的题目

### 场景3: 组合筛选后复习
1. 选择"数学" + "3星难度" + "学习中"
2. 完成复习
3. 验证: 仍然显示相同的筛选结果(掌握度可能变化)
