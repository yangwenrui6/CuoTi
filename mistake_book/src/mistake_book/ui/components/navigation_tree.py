"""导航树组件"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, 
    QTreeWidgetItem, QTreeWidgetItemIterator
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, Optional


class NavigationTree(QWidget):
    """导航树组件"""
    
    # 信号
    item_selected = pyqtSignal(dict)  # 选中项变化 {type, value}
    
    def __init__(self, ui_service, parent=None):
        """
        初始化导航树
        
        Args:
            ui_service: UI服务实例
        """
        super().__init__(parent)
        self._ui_service = ui_service
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title = QLabel("📂 分类导航")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # 树形导航
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("科目/标签")
        self._tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._tree)
    
    def _load_data(self):
        """加载导航数据"""
        # 从服务获取导航数据
        nav_data = self._ui_service.get_navigation_data()
        
        # 添加科目节点
        for subject in nav_data['subjects']:
            item = QTreeWidgetItem([subject])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "subject", "value": subject})
            self._tree.addTopLevelItem(item)
        
        # 添加标签节点
        if nav_data['tags']:
            tags_root = QTreeWidgetItem(["🏷️ 标签"])
            for tag in nav_data['tags']:
                tag_item = QTreeWidgetItem([tag])
                tag_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "tag", "value": tag})
                tags_root.addChild(tag_item)
            self._tree.addTopLevelItem(tags_root)
        
        # 添加掌握度节点
        mastery_root = QTreeWidgetItem(["📊 掌握度"])
        for level_data in nav_data['mastery_levels']:
            item = QTreeWidgetItem([f"{level_data['name']} ({level_data['count']})"])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "mastery", "value": level_data['value']})
            mastery_root.addChild(item)
        self._tree.addTopLevelItem(mastery_root)
        
        # 展开所有节点
        self._tree.expandAll()
    
    def refresh(self):
        """刷新导航树数据"""
        # 保存当前选中项的数据
        current_item = self._tree.currentItem()
        selected_data = None
        if current_item:
            selected_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        # 清空导航树
        self._tree.clear()
        
        # 重新加载数据
        self._load_data()
        
        # 恢复选中状态
        if selected_data:
            self._restore_selection(selected_data)
    
    def _restore_selection(self, selected_data: Dict[str, Any]):
        """恢复选中状态"""
        # 遍历所有项，找到匹配的项并选中
        iterator = QTreeWidgetItemIterator(self._tree)
        while iterator.value():
            item = iterator.value()
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data == selected_data:
                self._tree.setCurrentItem(item)
                break
            iterator += 1
    
    def get_selected_filter(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的筛选条件"""
        current_item = self._tree.currentItem()
        if not current_item:
            return None
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return None
        
        # 构建筛选条件
        filters = {}
        if data["type"] == "subject":
            filters["subject"] = data["value"]
        elif data["type"] == "mastery":
            filters["mastery_level"] = data["value"]
        elif data["type"] == "tag":
            filters["tags"] = [data["value"]]
        
        return filters
    
    def _on_item_clicked(self, item, column):
        """树节点点击事件"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data)
