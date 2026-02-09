"""题目表单组件"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Any, Tuple


class QuestionForm(QWidget):
    """题目表单组件"""
    
    # 信号
    data_changed = pyqtSignal()  # 数据变化
    
    def __init__(self, parent=None):
        """初始化表单"""
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 科目
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("科目:"))
        self._subject_combo = QComboBox()
        self._subject_combo.addItems(["数学", "物理", "化学", "英语", "语文", "其他"])
        subject_layout.addWidget(self._subject_combo)
        layout.addLayout(subject_layout)
        
        # 题型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("题型:"))
        self._type_combo = QComboBox()
        self._type_combo.addItems([
            "单选题", "多选题", "填空题", "简答题", "计算题", "其他"
        ])
        type_layout.addWidget(self._type_combo)
        layout.addLayout(type_layout)
        
        # 题目内容
        layout.addWidget(QLabel("题目内容:"))
        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("输入题目内容...")
        self._content_edit.setMinimumHeight(100)
        self._content_edit.setMaximumHeight(200)
        self._content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self._content_edit)
        
        # 我的答案
        layout.addWidget(QLabel("我的答案:"))
        self._my_answer_edit = QTextEdit()
        self._my_answer_edit.setPlaceholderText("输入你的答案...")
        self._my_answer_edit.setMaximumHeight(60)
        layout.addWidget(self._my_answer_edit)
        
        # 正确答案
        layout.addWidget(QLabel("正确答案:"))
        self._answer_edit = QTextEdit()
        self._answer_edit.setPlaceholderText("输入正确答案...")
        self._answer_edit.setMaximumHeight(60)
        layout.addWidget(self._answer_edit)
        
        # 解析
        layout.addWidget(QLabel("解析:"))
        self._explanation_edit = QTextEdit()
        self._explanation_edit.setPlaceholderText("输入解析...")
        self._explanation_edit.setMaximumHeight(80)
        layout.addWidget(self._explanation_edit)
        
        # 难度
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("难度:"))
        self._difficulty_combo = QComboBox()
        self._difficulty_combo.addItems([
            "1星 ⭐", "2星 ⭐⭐", "3星 ⭐⭐⭐", 
            "4星 ⭐⭐⭐⭐", "5星 ⭐⭐⭐⭐⭐"
        ])
        self._difficulty_combo.setCurrentIndex(2)  # 默认3星
        difficulty_layout.addWidget(self._difficulty_combo)
        layout.addLayout(difficulty_layout)
    
    def _connect_signals(self):
        """连接信号"""
        self._subject_combo.currentTextChanged.connect(self.data_changed.emit)
        self._type_combo.currentTextChanged.connect(self.data_changed.emit)
        self._content_edit.textChanged.connect(self.data_changed.emit)
        self._my_answer_edit.textChanged.connect(self.data_changed.emit)
        self._answer_edit.textChanged.connect(self.data_changed.emit)
        self._explanation_edit.textChanged.connect(self.data_changed.emit)
        self._difficulty_combo.currentIndexChanged.connect(self.data_changed.emit)
    
    def get_data(self) -> Dict[str, Any]:
        """
        获取表单数据
        
        Returns:
            {
                'subject': str,
                'question_type': str,
                'content': str,
                'my_answer': str,
                'answer': str,
                'explanation': str,
                'difficulty': int (1-5)
            }
        """
        return {
            'subject': self._subject_combo.currentText(),
            'question_type': self._type_combo.currentText(),
            'content': self._content_edit.toPlainText().strip(),
            'my_answer': self._my_answer_edit.toPlainText().strip(),
            'answer': self._answer_edit.toPlainText().strip(),
            'explanation': self._explanation_edit.toPlainText().strip(),
            'difficulty': self._difficulty_combo.currentIndex() + 1
        }
    
    def set_data(self, data: Dict[str, Any]):
        """设置表单数据（用于编辑场景）"""
        if 'subject' in data:
            index = self._subject_combo.findText(data['subject'])
            if index >= 0:
                self._subject_combo.setCurrentIndex(index)
        
        if 'question_type' in data:
            index = self._type_combo.findText(data['question_type'])
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        
        if 'content' in data:
            self._content_edit.setPlainText(data['content'])
        
        if 'my_answer' in data:
            self._my_answer_edit.setPlainText(data['my_answer'])
        
        if 'answer' in data:
            self._answer_edit.setPlainText(data['answer'])
        
        if 'explanation' in data:
            self._explanation_edit.setPlainText(data['explanation'])
        
        if 'difficulty' in data:
            difficulty = data['difficulty']
            if 1 <= difficulty <= 5:
                self._difficulty_combo.setCurrentIndex(difficulty - 1)
    
    def validate(self) -> Tuple[bool, str]:
        """
        验证表单数据
        
        Returns:
            (是否有效, 错误信息)
        """
        data = self.get_data()
        
        if not data['content']:
            return False, "题目内容不能为空"
        
        if not data['answer']:
            return False, "正确答案不能为空"
        
        return True, ""
    
    def clear(self):
        """清空表单"""
        self._subject_combo.setCurrentIndex(0)
        self._type_combo.setCurrentIndex(0)
        self._content_edit.clear()
        self._my_answer_edit.clear()
        self._answer_edit.clear()
        self._explanation_edit.clear()
        self._difficulty_combo.setCurrentIndex(2)
    
    def set_content(self, text: str):
        """设置题目内容（用于OCR识别后填充）"""
        self._content_edit.setPlainText(text)
    
    def focus_content(self):
        """聚焦到题目内容输入框"""
        self._content_edit.setFocus()
