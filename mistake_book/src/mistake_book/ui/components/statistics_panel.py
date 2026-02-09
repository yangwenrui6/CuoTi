"""统计面板组件"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PyQt6.QtCore import Qt


class StatisticsPanel(QWidget):
    """统计面板组件"""
    
    def __init__(self, ui_service, parent=None):
        """
        初始化统计面板
        
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
        
        # 统计面板
        stats_group = QGroupBox("📊 统计")
        stats_layout = QVBoxLayout()
        
        self._total_label = QLabel("总题数: 0")
        self._mastered_label = QLabel("已掌握: 0")
        self._learning_label = QLabel("学习中: 0")
        self._review_due_label = QLabel("待复习: 0")
        
        stats_layout.addWidget(self._total_label)
        stats_layout.addWidget(self._mastered_label)
        stats_layout.addWidget(self._learning_label)
        stats_layout.addWidget(self._review_due_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
    
    def update_statistics(self):
        """更新统计数据"""
        stats = self._ui_service.get_statistics_summary()
        
        self._total_label.setText(f"总题数: {stats.get('total_questions', 0)}")
        self._mastered_label.setText(f"已掌握: {stats.get('mastered', 0)}")
        self._learning_label.setText(f"学习中: {stats.get('learning', 0)}")
        self._review_due_label.setText(f"待复习: {stats.get('due_count', 0)}")
