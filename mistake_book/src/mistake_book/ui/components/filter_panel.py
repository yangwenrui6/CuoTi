"""筛选面板组件"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Any


class FilterPanel(QWidget):
    """筛选面板组件"""
    
    # 信号
    filter_changed = pyqtSignal(dict)  # 筛选条件变化
    
    def __init__(self, ui_service, parent=None):
        """
        初始化筛选面板
        
        Args:
            ui_service: UI服务实例
        """
        super().__init__(parent)
        self._ui_service = ui_service
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 筛选面板
        filter_group = QGroupBox("🔧 筛选")
        filter_layout = QVBoxLayout()
        
        # 从服务获取筛选选项
        filter_options = self._ui_service.get_filter_options()
        
        # 科目筛选
        filter_layout.addWidget(QLabel("科目:"))
        self._subject_filter = QComboBox()
        self._subject_filter.addItems(filter_options['subjects'])
        self._subject_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._subject_filter)
        
        # 难度筛选
        filter_layout.addWidget(QLabel("难度:"))
        self._difficulty_filter = QComboBox()
        self._difficulty_filter.addItems(filter_options['difficulties'])
        self._difficulty_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._difficulty_filter)
        
        # 掌握度筛选
        filter_layout.addWidget(QLabel("掌握度:"))
        self._mastery_filter = QComboBox()
        self._mastery_filter.addItems(filter_options['mastery_levels'])
        self._mastery_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._mastery_filter)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
    
    def get_filters(self) -> Dict[str, Any]:
        """获取当前筛选条件"""
        return self._ui_service.parse_filter_from_ui(
            self._subject_filter.currentText(),
            self._difficulty_filter.currentText(),
            self._mastery_filter.currentText()
        )
    
    def reset_filters(self):
        """重置筛选条件"""
        self._subject_filter.setCurrentIndex(0)
        self._difficulty_filter.setCurrentIndex(0)
        self._mastery_filter.setCurrentIndex(0)
    
    def _on_filter_changed(self):
        """筛选条件变化时触发"""
        filters = self.get_filters()
        self.filter_changed.emit(filters)
