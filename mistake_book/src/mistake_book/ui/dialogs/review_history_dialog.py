"""复习历史对话框 - 可视化显示复习记录"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ReviewHistoryDialog(QDialog):
    """复习历史对话框"""
    
    def __init__(self, review_service, parent=None):
        super().__init__(parent)
        self.review_service = review_service
        self.start_review_requested = False  # 标记是否请求开始复习
        
        self.setWindowTitle("📊 复习历史")
        self.setMinimumSize(1000, 600)
        
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("📊 复习历史记录")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
        """)
        layout.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("显示最近30次复习记录（按时间倒序）")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            font-size: 11pt;
            color: #7f8c8d;
            padding-bottom: 10px;
        """)
        layout.addWidget(desc_label)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "复习时间", "科目", "题型", "题目摘要", "掌握度", "下次复习"
        ])
        
        # 表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                gridline-color: #ecf0f1;
                font-size: 11pt;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 8px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 复习时间
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # 科目
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # 题型
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 题目摘要
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 掌握度
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # 下次复习
        
        # 禁止编辑
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 选择整行
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 开始复习按钮
        review_btn = QPushButton("🚀 复习这些题目")
        review_btn.setMinimumSize(140, 40)
        review_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                font-weight: bold;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        review_btn.clicked.connect(self.start_review)
        button_layout.addWidget(review_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setMinimumSize(100, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_history)
        button_layout.addWidget(refresh_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setMinimumSize(100, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_history(self):
        """加载复习历史"""
        try:
            from mistake_book.database.models import ReviewRecord, Question
            from mistake_book.config.constants import ReviewResult
            
            # 获取数据库会话
            with self.review_service.data_manager.db.session_scope() as session:
                # 查询最近30条复习记录
                records = (
                    session.query(ReviewRecord, Question)
                    .join(Question, ReviewRecord.question_id == Question.id)
                    .order_by(ReviewRecord.review_date.desc())
                    .limit(30)
                    .all()
                )
                
                # 清空表格
                self.table.setRowCount(0)
                
                # 填充数据
                for record, question in records:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    # 复习时间
                    review_time = record.review_date.strftime("%Y-%m-%d %H:%M")
                    time_item = QTableWidgetItem(review_time)
                    time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, 0, time_item)
                    
                    # 科目
                    subject_item = QTableWidgetItem(question.subject or "")
                    subject_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, 1, subject_item)
                    
                    # 题型
                    type_item = QTableWidgetItem(question.question_type or "")
                    type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, 2, type_item)
                    
                    # 题目摘要（截取前50字）
                    content = question.content or ""
                    summary = content[:50] + "..." if len(content) > 50 else content
                    summary_item = QTableWidgetItem(summary)
                    self.table.setItem(row, 3, summary_item)
                    
                    # 掌握度
                    mastery_map = {
                        ReviewResult.AGAIN.value: ("🔴 生疏", QColor(231, 76, 60)),
                        ReviewResult.HARD.value: ("🟡 困难", QColor(243, 156, 18)),
                        ReviewResult.GOOD.value: ("🟢 掌握", QColor(39, 174, 96)),
                        ReviewResult.EASY.value: ("🔵 熟练", QColor(52, 152, 219))
                    }
                    
                    mastery_text, mastery_color = mastery_map.get(
                        record.result, 
                        ("未知", QColor(149, 165, 166))
                    )
                    
                    mastery_item = QTableWidgetItem(mastery_text)
                    mastery_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    mastery_item.setForeground(mastery_color)
                    font = mastery_item.font()
                    font.setBold(True)
                    mastery_item.setFont(font)
                    self.table.setItem(row, 4, mastery_item)
                    
                    # 下次复习时间
                    if question.next_review_date:
                        next_review = question.next_review_date.strftime("%Y-%m-%d")
                        # 判断是否已到期
                        if question.next_review_date <= datetime.now():
                            next_review += " (已到期)"
                    else:
                        next_review = "未设置"
                    
                    next_item = QTableWidgetItem(next_review)
                    next_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, 5, next_item)
                
                logger.info(f"加载了 {len(records)} 条复习记录")
            
        except Exception as e:
            logger.error(f"加载复习历史失败: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "错误",
                f"加载复习历史失败：{str(e)}"
            )
    
    def start_review(self):
        """开始复习历史中的题目"""
        # 标记请求开始复习
        self.start_review_requested = True
        # 关闭对话框
        self.accept()
