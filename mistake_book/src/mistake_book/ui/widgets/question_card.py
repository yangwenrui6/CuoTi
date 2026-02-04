"""错题卡片组件"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class QuestionCard(QWidget):
    """错题卡片 - 带掌握度色标"""
    
    clicked = pyqtSignal(dict)  # 点击信号(查看详情)
    delete_requested = pyqtSignal(dict)  # 删除请求信号
    
    def __init__(self, question_data):
        super().__init__()
        self.question_data = question_data
        
        # 设置固定高度，让所有卡片大小一致
        self.setFixedHeight(180)
        
        self.init_ui()
        
        # 设置鼠标悬停效果
        self.setStyleSheet("""
            QuestionCard {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
            QuestionCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(15)
        
        # 左侧：掌握度色标
        mastery_level = self.question_data.get("mastery_level", 0)
        color_map = {
            0: "#e74c3c",  # 生疏 - 红色
            1: "#f39c12",  # 学习中 - 橙色
            2: "#27ae60",  # 掌握 - 绿色
            3: "#3498db",  # 熟练 - 蓝色
        }
        color = color_map.get(mastery_level, "#95a5a6")
        
        color_bar = QWidget()
        color_bar.setFixedWidth(10)
        color_bar.setStyleSheet(f"""
            background-color: {color};
            border-radius: 5px;
        """)
        layout.addWidget(color_bar)
        
        # 中间：内容区
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        
        # 标题行：科目 + 题型
        title_layout = QHBoxLayout()
        
        subject_label = QLabel(f"📚 {self.question_data.get('subject', '')}")
        subject_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 13pt;")
        title_layout.addWidget(subject_label)
        
        type_label = QLabel(f"• {self.question_data.get('question_type', '')}")
        type_label.setStyleSheet("color: #5a6c7d; font-size: 12pt; font-weight: 500;")
        title_layout.addWidget(type_label)
        
        title_layout.addStretch()
        
        # 难度星级
        difficulty = self.question_data.get('difficulty', 3)
        difficulty_label = QLabel("⭐" * difficulty)
        difficulty_label.setStyleSheet("font-size: 12pt;")
        title_layout.addWidget(difficulty_label)
        
        content_layout.addLayout(title_layout)
        
        # 题目摘要（截取前100字）
        content = self.question_data.get('content', '')
        summary = content[:100] + "..." if len(content) > 100 else content
        
        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setMaximumHeight(70)  # 限制摘要高度，约3行
        summary_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 12pt;
            line-height: 1.6;
            font-weight: 500;
            padding: 5px 0;
        """)
        content_layout.addWidget(summary_label)
        
        # 标签（如果有）
        tags = self.question_data.get('tags', [])
        if tags:
            tags_layout = QHBoxLayout()
            for tag in tags[:3]:  # 最多显示3个标签
                tag_label = QLabel(f"🏷️ {tag}")
                tag_label.setStyleSheet("""
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 5px 12px;
                    border-radius: 12px;
                    font-size: 10pt;
                    font-weight: 500;
                """)
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            content_layout.addLayout(tags_layout)
        
        layout.addLayout(content_layout)
        
        # 右侧：操作按钮和状态
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        action_layout.setSpacing(10)
        
        # 掌握度文字
        mastery_text = ["🔴 生疏", "🟡 学习中", "🟢 掌握", "🔵 熟练"]
        mastery_label = QLabel(mastery_text[mastery_level])
        mastery_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 11pt;
        """)
        action_layout.addWidget(mastery_label)
        
        # 复习次数
        repetitions = self.question_data.get('repetitions', 0)
        rep_label = QLabel(f"已复习 {repetitions} 次")
        rep_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; font-weight: 500;")
        action_layout.addWidget(rep_label)
        
        action_layout.addStretch()
        
        # 删除按钮
        delete_btn = QPushButton("🗑️ 删除")
        delete_btn.setFixedSize(80, 35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_btn.clicked.connect(self.on_delete_clicked)
        action_layout.addWidget(delete_btn)
        
        layout.addLayout(action_layout)
    
    def on_delete_clicked(self):
        """删除按钮点击事件"""
        self.delete_requested.emit(self.question_data)
        # 阻止事件传播,避免触发卡片点击
        event = self.sender()
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 点击卡片查看详情"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.question_data)
