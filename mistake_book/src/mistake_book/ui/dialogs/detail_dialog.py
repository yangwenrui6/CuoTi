"""错题详情对话框 - 查看错题完整信息"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QWidget, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path
from typing import Dict, Any, Optional


class QuestionDetailDialog(QDialog):
    """错题详情对话框"""
    
    # 信号：当答案被修改时发出
    answer_updated = pyqtSignal(int, dict)  # question_id, updates
    
    def __init__(self, question_data: Dict[str, Any], question_service=None, parent=None):
        super().__init__(parent)
        self.question_data = question_data
        self.original_data = question_data.copy()  # 保存原始数据用于比较
        self.question_service = question_service  # 用于获取图片完整路径
        
        # 存储可编辑控件的引用
        self.content_edit: Optional[QTextEdit] = None
        self.my_answer_edit: Optional[QTextEdit] = None
        self.correct_answer_edit: Optional[QTextEdit] = None
        self.explanation_edit: Optional[QTextEdit] = None
        
        self.setWindowTitle("📖 错题详情")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # 标题栏
        self.add_title_section(content_layout)
        
        # 基本信息
        self.add_basic_info_section(content_layout)
        
        # 题目内容
        self.add_content_section(content_layout)
        
        # 答案部分
        self.add_answer_section(content_layout)
        
        # 复习数据
        self.add_review_data_section(content_layout)
        
        # 图片（如果有）
        self.add_image_section(content_layout)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # 底部按钮
        self.add_buttons(layout)
    
    def add_title_section(self, layout):
        """添加标题栏"""
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: #3498db; border-radius: 8px; padding: 15px;")
        title_layout = QVBoxLayout(title_widget)
        
        # 题目ID
        id_label = QLabel(f"题目 #{self.question_data.get('id', 'N/A')}")
        id_label.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        title_layout.addWidget(id_label)
        
        # 科目和题型
        info_label = QLabel(
            f"{self.question_data.get('subject', '')} · "
            f"{self.question_data.get('question_type', '')}"
        )
        info_label.setStyleSheet("color: white; font-size: 11pt;")
        title_layout.addWidget(info_label)
        
        layout.addWidget(title_widget)
    
    def add_basic_info_section(self, layout):
        """添加基本信息"""
        group = QGroupBox("📋 基本信息")
        group_layout = QVBoxLayout()
        
        # 难度
        difficulty = self.question_data.get('difficulty', 3)
        difficulty_label = QLabel(f"难度: {'⭐' * difficulty}")
        difficulty_label.setStyleSheet("font-size: 11pt;")
        group_layout.addWidget(difficulty_label)
        
        # 掌握度
        mastery_level = self.question_data.get('mastery_level', 0)
        mastery_text = ["🔴 生疏", "🟡 学习中", "🟢 掌握", "🔵 熟练"]
        mastery_label = QLabel(f"掌握度: {mastery_text[mastery_level]}")
        mastery_label.setStyleSheet("font-size: 11pt;")
        group_layout.addWidget(mastery_label)
        
        # 标签
        tags = self.question_data.get('tags', [])
        if tags:
            tags_text = " ".join([f"🏷️ {tag}" for tag in tags])
            tags_label = QLabel(f"标签: {tags_text}")
            tags_label.setStyleSheet("font-size: 11pt;")
            tags_label.setWordWrap(True)
            group_layout.addWidget(tags_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_content_section(self, layout):
        """添加题目内容 - 可编辑"""
        group = QGroupBox("📝 题目内容 (可编辑)")
        group_layout = QVBoxLayout()
        
        content = self.question_data.get('content', '')
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(content)
        self.content_edit.setMinimumHeight(100)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14pt;
                font-weight: 500;
                padding: 20px;
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                line-height: 1.8;
                color: #212121;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        group_layout.addWidget(self.content_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_answer_section(self, layout):
        """添加答案部分 - 可编辑"""
        # 我的答案
        my_answer = self.question_data.get('my_answer', '')
        group = QGroupBox("❌ 我的答案 (可编辑)")
        group_layout = QVBoxLayout()
        
        self.my_answer_edit = QTextEdit()
        self.my_answer_edit.setPlainText(my_answer)
        self.my_answer_edit.setMinimumHeight(80)
        self.my_answer_edit.setStyleSheet("""
            QTextEdit {
                font-size: 13pt;
                font-weight: 500;
                padding: 18px;
                background-color: #ffebee;
                border: 2px solid #ef5350;
                border-radius: 8px;
                line-height: 1.7;
                color: #c62828;
            }
            QTextEdit:focus {
                border: 2px solid #e53935;
                background-color: #fff;
            }
        """)
        group_layout.addWidget(self.my_answer_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # 正确答案
        answer = self.question_data.get('answer', '')
        group = QGroupBox("✅ 正确答案 (可编辑)")
        group_layout = QVBoxLayout()
        
        self.correct_answer_edit = QTextEdit()
        self.correct_answer_edit.setPlainText(answer)
        self.correct_answer_edit.setMinimumHeight(80)
        self.correct_answer_edit.setStyleSheet("""
            QTextEdit {
                font-size: 13pt;
                font-weight: 600;
                padding: 18px;
                background-color: #e8f5e9;
                border: 2px solid #66bb6a;
                border-radius: 8px;
                line-height: 1.7;
                color: #2e7d32;
            }
            QTextEdit:focus {
                border: 2px solid #43a047;
                background-color: #fff;
            }
        """)
        group_layout.addWidget(self.correct_answer_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # 解析
        explanation = self.question_data.get('explanation', '')
        group = QGroupBox("💡 解析 (可编辑)")
        group_layout = QVBoxLayout()
        
        self.explanation_edit = QTextEdit()
        self.explanation_edit.setPlainText(explanation)
        self.explanation_edit.setMinimumHeight(80)
        self.explanation_edit.setStyleSheet("""
            QTextEdit {
                font-size: 12pt;
                padding: 18px;
                background-color: #fff8e1;
                border: 2px solid #ffb74d;
                border-radius: 8px;
                line-height: 1.7;
                color: #f57c00;
            }
            QTextEdit:focus {
                border: 2px solid #fb8c00;
                background-color: #fff;
            }
        """)
        group_layout.addWidget(self.explanation_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_review_data_section(self, layout):
        """添加复习数据"""
        group = QGroupBox("📊 复习数据")
        group_layout = QVBoxLayout()
        
        # 复习次数
        repetitions = self.question_data.get('repetitions', 0)
        rep_label = QLabel(f"已复习: {repetitions} 次")
        rep_label.setStyleSheet("font-size: 11pt;")
        group_layout.addWidget(rep_label)
        
        # 间隔天数
        interval = self.question_data.get('interval', 0)
        interval_label = QLabel(f"当前间隔: {interval} 天")
        interval_label.setStyleSheet("font-size: 11pt;")
        group_layout.addWidget(interval_label)
        
        # 难度因子
        ef = self.question_data.get('easiness_factor', 2.5)
        ef_label = QLabel(f"难度因子: {ef:.2f}")
        ef_label.setStyleSheet("font-size: 11pt;")
        group_layout.addWidget(ef_label)
        
        # 下次复习时间
        next_review = self.question_data.get('next_review_date')
        if next_review:
            from datetime import datetime
            if isinstance(next_review, str):
                next_review_text = next_review
            else:
                next_review_text = next_review.strftime("%Y-%m-%d %H:%M")
            
            next_label = QLabel(f"下次复习: {next_review_text}")
            next_label.setStyleSheet("font-size: 11pt; color: #e74c3c; font-weight: bold;")
            group_layout.addWidget(next_label)
        
        # 创建时间
        created_at = self.question_data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_text = created_at
            else:
                created_text = created_at.strftime("%Y-%m-%d %H:%M")
            
            created_label = QLabel(f"创建时间: {created_text}")
            created_label.setStyleSheet("font-size: 10pt; color: #7f8c8d;")
            group_layout.addWidget(created_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_image_section(self, layout):
        """添加图片（如果有）"""
        image_path_str = self.question_data.get('image_path')
        if not image_path_str:
            return
        
        # 获取完整路径
        if self.question_service:
            full_path = self.question_service.get_image_full_path(image_path_str)
        else:
            # 兼容旧代码，直接使用路径
            full_path = Path(image_path_str) if Path(image_path_str).exists() else None
        
        if full_path and full_path.exists():
            group = QGroupBox("🖼️ 题目图片")
            group_layout = QVBoxLayout()
            
            # 使用PIL加载图片，避免中文路径问题
            try:
                from PIL import Image
                import numpy as np
                from PyQt6.QtGui import QImage
                
                pil_image = Image.open(full_path)
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                img_array = np.array(pil_image)
                height, width, channel = img_array.shape
                bytes_per_line = 3 * width
                q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                
                image_label = QLabel()
                scaled = pixmap.scaled(700, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                group_layout.addWidget(image_label)
                
                group.setLayout(group_layout)
                layout.addWidget(group)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"加载图片失败: {e}")
    
    def add_buttons(self, layout):
        """添加底部按钮"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 保存按钮
        save_btn = QPushButton("💾 保存修改")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_changes)
        save_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                padding: 10px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.close_dialog)
        close_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                padding: 10px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def has_changes(self) -> bool:
        """检查是否有修改"""
        if not self.content_edit or not self.my_answer_edit or not self.correct_answer_edit or not self.explanation_edit:
            return False
        
        current_content = self.content_edit.toPlainText().strip()
        current_my_answer = self.my_answer_edit.toPlainText().strip()
        current_correct_answer = self.correct_answer_edit.toPlainText().strip()
        current_explanation = self.explanation_edit.toPlainText().strip()
        
        original_content = self.original_data.get('content', '').strip()
        original_my_answer = self.original_data.get('my_answer', '').strip()
        original_correct_answer = self.original_data.get('answer', '').strip()
        original_explanation = self.original_data.get('explanation', '').strip()
        
        return (current_content != original_content or
                current_my_answer != original_my_answer or
                current_correct_answer != original_correct_answer or
                current_explanation != original_explanation)
    
    def save_changes(self):
        """保存修改"""
        if not self.has_changes():
            QMessageBox.information(self, "提示", "没有修改需要保存")
            return
        
        # 收集修改的数据
        updates = {
            'content': self.content_edit.toPlainText().strip(),
            'my_answer': self.my_answer_edit.toPlainText().strip(),
            'answer': self.correct_answer_edit.toPlainText().strip(),
            'explanation': self.explanation_edit.toPlainText().strip()
        }
        
        # 发出信号通知主窗口保存
        question_id = self.question_data.get('id')
        if question_id:
            self.answer_updated.emit(question_id, updates)
            
            # 更新原始数据，避免重复提示
            self.original_data['content'] = updates['content']
            self.original_data['my_answer'] = updates['my_answer']
            self.original_data['answer'] = updates['answer']
            self.original_data['explanation'] = updates['explanation']
            
            QMessageBox.information(self, "成功", "修改已保存！")
    
    def close_dialog(self):
        """关闭对话框前检查是否有未保存的修改"""
        if self.has_changes():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "您有未保存的修改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_changes()
                self.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                self.reject()
            # Cancel - 不做任何操作，保持对话框打开
        else:
            self.accept()
    
    def closeEvent(self, event):
        """重写关闭事件，处理窗口关闭按钮"""
        if self.has_changes():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "您有未保存的修改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_changes()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
