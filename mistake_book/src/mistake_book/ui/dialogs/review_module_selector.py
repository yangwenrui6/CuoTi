"""复习模块选择对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, List, Optional


class ReviewModuleSelectorDialog(QDialog):
    """复习模块选择对话框"""
    
    # 信号：选择了模块后发出 (subject, question_type)
    module_selected = pyqtSignal(str, str)
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        
        # 存储可用的科目和题型
        self.subjects: List[str] = []
        self.question_types: Dict[str, List[str]] = {}  # {科目: [题型列表]}
        self.question_counts: Dict[str, Dict[str, int]] = {}  # {科目: {题型: 数量}}
        
        # 当前选择
        self.selected_subject: Optional[str] = None
        self.selected_question_type: Optional[str] = None
        
        self.setWindowTitle("📚 选择复习模块")
        self.setMinimumSize(700, 500)
        
        self.load_modules()
        self.init_ui()
    
    def load_modules(self):
        """加载所有可用的模块（科目和题型）"""
        # 获取所有题目
        all_questions = self.data_manager.search_questions({})
        
        # 统计科目和题型
        subject_types: Dict[str, set] = {}
        counts: Dict[str, Dict[str, int]] = {}
        
        for q in all_questions:
            subject = q.get('subject', '未分类')
            q_type = q.get('question_type', '其他')
            
            # 收集科目和题型
            if subject not in subject_types:
                subject_types[subject] = set()
                counts[subject] = {}
            
            subject_types[subject].add(q_type)
            
            # 统计数量
            if q_type not in counts[subject]:
                counts[subject][q_type] = 0
            counts[subject][q_type] += 1
        
        # 转换为列表
        self.subjects = sorted(subject_types.keys())
        self.question_types = {
            subject: sorted(list(types)) 
            for subject, types in subject_types.items()
        }
        self.question_counts = counts
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("请选择您要复习的模块")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
        """)
        layout.addWidget(title_label)
        
        # 主内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧：科目列表
        subject_group = QGroupBox("📚 选择科目")
        subject_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #3498db;
            }
        """)
        subject_layout = QVBoxLayout()
        
        self.subject_list = QListWidget()
        self.subject_list.setStyleSheet("""
            QListWidget {
                font-size: 13pt;
                border: 3px solid #3498db;
                border-radius: 8px;
                padding: 8px;
                background-color: #e3f2fd;
                outline: none;
            }
            QListWidget::item {
                padding: 15px;
                border-radius: 6px;
                margin: 3px;
                background-color: white;
                color: #1565c0;
                font-weight: 600;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #90caf9;
                color: #0d47a1;
            }
            QListWidget::item:selected {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:focus {
                outline: none;
            }
        """)
        self.subject_list.itemClicked.connect(self.on_subject_selected)
        
        # 添加科目项
        for subject in self.subjects:
            total_count = sum(self.question_counts[subject].values())
            item = QListWidgetItem(f"{subject} ({total_count}题)")
            self.subject_list.addItem(item)
        
        subject_layout.addWidget(self.subject_list)
        subject_group.setLayout(subject_layout)
        content_layout.addWidget(subject_group)
        
        # 右侧：题型列表
        type_group = QGroupBox("📝 选择题型")
        type_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #27ae60;
            }
        """)
        type_layout = QVBoxLayout()
        
        self.type_list = QListWidget()
        self.type_list.setStyleSheet("""
            QListWidget {
                font-size: 13pt;
                border: 3px solid #27ae60;
                border-radius: 8px;
                padding: 8px;
                background-color: #e8f5e9;
                outline: none;
            }
            QListWidget::item {
                padding: 15px;
                border-radius: 6px;
                margin: 3px;
                background-color: white;
                color: #2e7d32;
                font-weight: 600;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #81c784;
                color: #1b5e20;
            }
            QListWidget::item:selected {
                background-color: #388e3c;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:focus {
                outline: none;
            }
        """)
        self.type_list.itemClicked.connect(self.on_type_selected)
        
        # 初始禁用
        self.type_list.setEnabled(False)
        
        type_layout.addWidget(self.type_list)
        type_group.setLayout(type_layout)
        content_layout.addWidget(type_group)
        
        layout.addLayout(content_layout)
        
        # 选择提示
        self.selection_label = QLabel("请先选择科目，然后选择题型")
        self.selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_label.setStyleSheet("""
            font-size: 11pt;
            color: #7f8c8d;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
        """)
        layout.addWidget(self.selection_label)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 全部复习按钮
        all_btn = QPushButton("📖 复习全部")
        all_btn.setMinimumSize(120, 45)
        all_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                font-weight: bold;
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        all_btn.clicked.connect(self.on_review_all)
        button_layout.addWidget(all_btn)
        
        # 开始复习按钮
        self.start_btn = QPushButton("🚀 开始复习")
        self.start_btn.setMinimumSize(120, 45)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.start_btn.clicked.connect(self.on_start_review)
        button_layout.addWidget(self.start_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumSize(100, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def on_subject_selected(self, item: QListWidgetItem):
        """科目被选择"""
        # 获取科目名称（去掉题目数量）
        text = item.text()
        subject = text.split(' (')[0]
        self.selected_subject = subject
        self.selected_question_type = None
        
        # 清空并启用题型列表
        self.type_list.clear()
        self.type_list.setEnabled(True)
        
        # 添加题型项
        if subject in self.question_types:
            for q_type in self.question_types[subject]:
                count = self.question_counts[subject].get(q_type, 0)
                type_item = QListWidgetItem(f"{q_type} ({count}题)")
                self.type_list.addItem(type_item)
        
        # 更新提示
        self.selection_label.setText(f"已选择科目：{subject}，请选择题型")
        self.start_btn.setEnabled(False)
    
    def on_type_selected(self, item: QListWidgetItem):
        """题型被选择"""
        # 获取题型名称（去掉题目数量）
        text = item.text()
        q_type = text.split(' (')[0]
        self.selected_question_type = q_type
        
        # 更新提示
        count = self.question_counts[self.selected_subject].get(q_type, 0)
        self.selection_label.setText(
            f"✅ 已选择：{self.selected_subject} - {q_type} ({count}题)"
        )
        self.selection_label.setStyleSheet("""
            font-size: 11pt;
            color: #27ae60;
            font-weight: bold;
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 6px;
        """)
        
        # 启用开始按钮
        self.start_btn.setEnabled(True)
    
    def on_start_review(self):
        """开始复习选定的模块"""
        if not self.selected_subject or not self.selected_question_type:
            QMessageBox.warning(self, "提示", "请先选择科目和题型")
            return
        
        print(f"发出信号：{self.selected_subject}, {self.selected_question_type}")  # 调试信息
        
        # 发出信号
        self.module_selected.emit(self.selected_subject, self.selected_question_type)
        
        # 关闭对话框
        self.accept()
        self.accept()
    
    def on_review_all(self):
        """复习全部题目"""
        total = sum(
            sum(counts.values()) 
            for counts in self.question_counts.values()
        )
        
        if total == 0:
            QMessageBox.information(self, "提示", "暂无题目可复习")
            return
        
        reply = QMessageBox.question(
            self,
            "确认",
            f"确定要复习全部 {total} 道题目吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 发出信号，使用空字符串表示全部
            self.module_selected.emit("", "")
            self.accept()
