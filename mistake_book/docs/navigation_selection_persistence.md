# 导航树选中状态持久化

## 修改日期
2026-02-03

## 问题描述
用户在左侧导航树中点击某个项目(如"数学"科目)后,该项目会被高亮选中。但当用户删除或添加题目后,导航树会刷新,导致选中状态丢失,用户失去了当前浏览位置的视觉标识。

## 问题原因
`refresh_navigation()` 方法在刷新导航树时:
1. 调用 `self.nav_tree.clear()` 清空所有节点
2. 重新创建所有节点
3. 没有保存和恢复之前的选中状态

## 解决方案

### 1. 保存选中状态
在清空导航树之前,保存当前选中项的数据:

```python
def refresh_navigation(self):
    # 保存当前选中项的数据
    current_item = self.nav_tree.currentItem()
    selected_data = None
    if current_item:
        selected_data = current_item.data(0, Qt.ItemDataRole.UserRole)
```

### 2. 重建导航树
按原有逻辑重新创建所有节点。

### 3. 恢复选中状态
在创建每个节点时,检查是否与之前选中的项目匹配:

#### 科目节点
```python
for subject in nav_data['subjects']:
    item = QTreeWidgetItem([subject])
    item.setData(0, Qt.ItemDataRole.UserRole, {"type": "subject", "value": subject})
    self.nav_tree.addTopLevelItem(item)
    
    # 恢复选中状态
    if selected_data and selected_data.get("type") == "subject" and selected_data.get("value") == subject:
        self.nav_tree.setCurrentItem(item)
```

#### 标签节点
```python
for tag in nav_data['tags']:
    tag_item = QTreeWidgetItem([tag])
    tag_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "tag", "value": tag})
    tags_root.addChild(tag_item)
    
    # 恢复选中状态
    if selected_data and selected_data.get("type") == "tag" and selected_data.get("value") == tag:
        self.nav_tree.setCurrentItem(tag_item)
```

#### 掌握度节点
```python
for level_data in nav_data['mastery_levels']:
    item = QTreeWidgetItem([f"{level_data['name']} ({level_data['count']})"])
    item.setData(0, Qt.ItemDataRole.UserRole, {"type": "mastery", "value": level_data['value']})
    mastery_root.addChild(item)
    
    # 恢复选中状态
    if selected_data and selected_data.get("type") == "mastery" and selected_data.get("value") == level_data['value']:
        self.nav_tree.setCurrentItem(item)
```

## 技术实现

### 节点数据结构
每个导航树节点都存储了类型和值:

```python
{
    "type": "subject",  # 或 "tag", "mastery"
    "value": "数学"     # 具体的值
}
```

### 匹配逻辑
通过比较类型和值来确定是否是同一个节点:

```python
if selected_data and \
   selected_data.get("type") == "subject" and \
   selected_data.get("value") == subject:
    self.nav_tree.setCurrentItem(item)
```

### QTreeWidget API
- `currentItem()`: 获取当前选中的项目
- `setCurrentItem(item)`: 设置选中的项目
- `data(column, role)`: 获取节点存储的数据
- `setData(column, role, value)`: 设置节点存储的数据

## 用户体验改进

### 修改前
1. 用户点击"数学"科目,看到数学题目列表
2. "数学"节点高亮显示
3. 用户删除一道数学题
4. 导航树刷新,"数学"节点不再高亮
5. 用户失去了当前位置的视觉标识

### 修改后
1. 用户点击"数学"科目,看到数学题目列表
2. "数学"节点高亮显示
3. 用户删除一道数学题
4. 导航树刷新,"数学"节点仍然高亮
5. 用户清楚地知道当前在浏览数学题目

## 应用场景

### 场景1: 删除题目后
1. 点击"数学"科目
2. 删除一道数学题
3. 验证: "数学"节点仍然高亮

### 场景2: 添加题目后
1. 点击"物理"科目
2. 添加一道物理题
3. 验证: "物理"节点仍然高亮

### 场景3: 复习后
1. 点击"学习中"掌握度
2. 完成复习(掌握度可能改变)
3. 验证: "学习中"节点仍然高亮

### 场景4: 标签筛选
1. 点击某个标签
2. 删除或添加题目
3. 验证: 该标签节点仍然高亮

## 边界情况处理

### 情况1: 没有选中任何项目
```python
current_item = self.nav_tree.currentItem()
if current_item:  # 检查是否为None
    selected_data = current_item.data(0, Qt.ItemDataRole.UserRole)
```

### 情况2: 选中的项目已不存在
例如删除了某个科目的最后一道题,该科目可能从列表中消失:
- 刷新后不会找到匹配的节点
- 不会设置任何选中状态
- 用户看到的是无选中状态的导航树

### 情况3: 节点数据为空
```python
if selected_data and \
   selected_data.get("type") == "subject" and \
   selected_data.get("value") == subject:
```
使用 `and` 短路逻辑,确保 `selected_data` 不为 `None` 才访问其方法。

## 与视图状态持久化的配合

这个功能与之前实现的"视图状态持久化"功能配合使用:

1. **视图状态持久化**: 保持筛选条件,确保显示正确的题目列表
2. **导航选中持久化**: 保持视觉标识,让用户知道当前在哪个分类

两者结合,提供完整的用户体验:
- 用户知道在看什么(导航高亮)
- 用户看到正确的内容(筛选保持)

## 相关文件
- `src/mistake_book/ui/main_window.py`

## 相关文档
- `view_state_persistence.md`: 视图状态持久化
