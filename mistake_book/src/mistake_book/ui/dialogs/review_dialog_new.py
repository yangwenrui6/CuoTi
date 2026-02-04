"""新的复习对话框 - 简洁卡片式设计"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path
from typing import List, Dict, Any
from mistake_book.config.constants import ReviewResult
import logging

logger = logging.getLogger(__name__)


class ReviewDialog(QDialog):
    """复习对话框"""
    
    # 信号：复习完成，请求返回模块选择器
    review_completed = pyqtSignal()
    
    def __init__(self, questions: List[Dict[str, Any]], review_service, parent=None):
        super().__init__(parent)
        self.questions = questions
        self.review_service = review_service
        self.current_index = 0
        self.reviewed_questions = []  # 记录已复习的题目
        
        self.setWindowTitle("📚 复习模式")
        self.setMinimumSize(900, 700)
        
        self.init_ui()
        self.load_question()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部：进度和关闭按钮
        top_layout = QHBoxLayout()
        
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px 10px;
            background-color: #ecf0f1;
            border-radius: 6px;
        """)
        top_layout.addWidget(self.progress_label)
        
        top_layout.addStretch()
        
        close_btn = QPushButton("❌ 结束复习")
        close_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                padding: 8px 15px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.finish_review)
        top_layout.addWidget(close_btn)
        
        layout.addLayout(top_layout)
        
        # 中间：题目内容区（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll, 1)
        
        # 底部：操作按钮区
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_widget)
        self.bottom_layout.setSpacing(10)
        
        # 显示答案按钮
        self.show_answer_btn = QPushButton("👁️ 显示答案")
        self.show_answer_btn.setMinimumHeight(50)
        self.show_answer_btn.setStyleSheet("""
            QPushButton {
                font-size: 13pt;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.show_answer_btn.clicked.connect(self.toggle_answer)
        self.bottom_layout.addWidget(self.show_answer_btn)
        
        # 掌握度按钮组（初始隐藏）
        self.mastery_widget = QWidget()
        mastery_layout = QHBoxLayout(self.mastery_widget)
        mastery_layout.setSpacing(10)
        
        # 提示标签
        tip_label = QLabel("请评价您的掌握程度：")
        tip_label.setStyleSheet("font-size: 12pt; color: #7f8c8d;")
        mastery_layout.addWidget(tip_label)
        
        # 四个掌握度按钮
        self.mastery_buttons = []
        mastery_configs = [
            ("🔴 生疏", "#e74c3c", ReviewResult.AGAIN),
            ("🟡 困难", "#f39c12", ReviewResult.HARD),
            ("🟢 掌握", "#27ae60", ReviewResult.GOOD),
            ("🔵 熟练", "#3498db", ReviewResult.EASY)
        ]
        
        for text, color, result in mastery_configs:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 12pt;
                    font-weight: bold;
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            btn.clicked.connect(lambda checked, r=result: self.on_mastery_selected(r))
            mastery_layout.addWidget(btn)
            self.mastery_buttons.append(btn)
        
        self.mastery_widget.setVisible(False)
        self.bottom_layout.addWidget(self.mastery_widget)
        
        layout.addWidget(self.bottom_widget)
    
    def load_question(self):
        """加载当前题目"""
        # 清空内容区
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self.current_index >= len(self.questions):
            self.show_summary()
            return
        
        question = self.questions[self.current_index]
        
        # 更新进度
        self.progress_label.setText(
            f"题目 {self.current_index + 1} / {len(self.questions)}"
        )
        
        # 题目信息卡片
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        info_layout = QHBoxLayout(info_card)
        
        subject_label = QLabel(f"📚 {question.get('subject', '')}")
        subject_label.setStyleSheet("color: white; font-size: 12pt; font-weight: bold;")
        info_layout.addWidget(subject_label)
        
        type_label = QLabel(f"📝 {question.get('question_type', '')}")
        type_label.setStyleSheet("color: white; font-size: 12pt;")
        info_layout.addWidget(type_label)
        
        info_layout.addStretch()
        
        difficulty = question.get('difficulty', 3)
        diff_label = QLabel("⭐" * difficulty)
        diff_label.setStyleSheet("color: white; font-size: 12pt;")
        info_layout.addWidget(diff_label)
        
        self.content_layout.addWidget(info_card)
        
        # 题目图片（如果有）
        image_path = question.get('image_path')
        if image_path and Path(image_path).exists():
            image_frame = QFrame()
            image_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            image_layout = QVBoxLayout(image_frame)
            
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            scaled = pixmap.scaled(800, 400, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_layout.addWidget(image_label)
            
            self.content_layout.addWidget(image_frame)
        
        # 题目内容
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        
        content_title = QLabel("📝 题目内容")
        content_title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(content_title)
        
        content_text = QLabel(question.get('content', ''))
        content_text.setWordWrap(True)
        content_text.setStyleSheet("""
            font-size: 14pt;
            color: #2c3e50;
            line-height: 1.8;
            padding: 10px 0;
        """)
        content_layout.addWidget(content_text)
        
        self.content_layout.addWidget(content_frame)
        
        # 答案区域（初始隐藏）
        self.answer_widget = QWidget()
        answer_layout = QVBoxLayout(self.answer_widget)
        answer_layout.setSpacing(15)
        
        # 我的答案
        my_answer = question.get('my_answer', '')
        if my_answer:
            my_answer_frame = QFrame()
            my_answer_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffebee;
                    border: 2px solid #ef5350;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            my_answer_layout = QVBoxLayout(my_answer_frame)
            
            my_answer_title = QLabel("❌ 我的答案")
            my_answer_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #c62828;")
            my_answer_layout.addWidget(my_answer_title)
            
            my_answer_text = QLabel(my_answer)
            my_answer_text.setWordWrap(True)
            my_answer_text.setStyleSheet("font-size: 13pt; color: #c62828; padding: 5px 0;")
            my_answer_layout.addWidget(my_answer_text)
            
            answer_layout.addWidget(my_answer_frame)
        
        # 正确答案
        correct_answer = question.get('answer', '')
        if correct_answer:
            correct_frame = QFrame()
            correct_frame.setStyleSheet("""
                QFrame {
                    background-color: #e8f5e9;
                    border: 2px solid #66bb6a;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            correct_layout = QVBoxLayout(correct_frame)
            
            correct_title = QLabel("✅ 正确答案")
            correct_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2e7d32;")
            correct_layout.addWidget(correct_title)
            
            correct_text = QLabel(correct_answer)
            correct_text.setWordWrap(True)
            correct_text.setStyleSheet("font-size: 13pt; color: #2e7d32; padding: 5px 0;")
            correct_layout.addWidget(correct_text)
            
            answer_layout.addWidget(correct_frame)
        
        # 解析
        explanation = question.get('explanation', '')
        if explanation:
            exp_frame = QFrame()
            exp_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff8e1;
                    border: 2px solid #ffb74d;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            exp_layout = QVBoxLayout(exp_frame)
            
            exp_title = QLabel("💡 解析")
            exp_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f57c00;")
            exp_layout.addWidget(exp_title)
            
            exp_text = QLabel(explanation)
            exp_text.setWordWrap(True)
            exp_text.setStyleSheet("font-size: 12pt; color: #f57c00; padding: 5px 0;")
            exp_layout.addWidget(exp_text)
            
            answer_layout.addWidget(exp_frame)
        
        self.answer_widget.setVisible(False)
        self.content_layout.addWidget(self.answer_widget)
        
        self.content_layout.addStretch()
        
        # 重置按钮状态
        self.show_answer_btn.setVisible(True)
        self.show_answer_btn.setText("👁️ 显示答案")
        self.mastery_widget.setVisible(False)
    
    def toggle_answer(self):
        """切换答案显示"""
        is_visible = self.answer_widget.isVisible()
        self.answer_widget.setVisible(not is_visible)
        
        if not is_visible:
            # 显示答案后，隐藏显示按钮，显示掌握度按钮
            self.show_answer_btn.setVisible(False)
            self.mastery_widget.setVisible(True)
        else:
            self.show_answer_btn.setText("👁️ 显示答案")
    
    def on_mastery_selected(self, result: ReviewResult):
        """选择掌握度"""
        question = self.questions[self.current_index]
        question_id = question.get('id')
        
        logger.info(f"题目 {question_id} 掌握度评价: {result}")
        
        # 先记录已复习的题目（无论保存是否成功）
        self.reviewed_questions.append({
            'question': question,
            'result': result,
            'updates': {}
        })
        
        # 调用服务更新题目状态
        success, message, updates = self.review_service.process_review_result(
            question_id, result
        )
        
        if success:
            # 更新记录中的updates
            self.reviewed_questions[-1]['updates'] = updates
            logger.info(f"题目状态更新成功")
        else:
            logger.error(f"更新题目状态失败: {message}")
        
        # 进入下一题
        self.current_index += 1
        self.load_question()
    
    def finish_review(self):
        """结束复习"""
        if self.current_index < len(self.questions):
            # 还有未复习的题目，询问是否确认结束
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "确认结束",
                f"还有 {len(self.questions) - self.current_index} 道题目未复习，确定要结束吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.show_summary()
    
    def show_summary(self):
        """显示复习总结"""
        # 清空内容区
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 隐藏底部按钮
        self.bottom_widget.setVisible(False)
        
        # 总结卡片
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border: 3px solid #27ae60;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # 标题
        title = QLabel("🎉 复习完成！")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #27ae60;")
        summary_layout.addWidget(title)
        
        # 统计信息
        stats_label = QLabel(f"本次复习了 {len(self.reviewed_questions)} 道题目")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("font-size: 16pt; color: #2c3e50; margin: 20px 0;")
        summary_layout.addWidget(stats_label)
        
        # 掌握度统计
        if self.reviewed_questions:
            result_counts = {
                ReviewResult.AGAIN: 0,
                ReviewResult.HARD: 0,
                ReviewResult.GOOD: 0,
                ReviewResult.EASY: 0
            }
            
            for item in self.reviewed_questions:
                result_counts[item['result']] += 1
            
            stats_text = f"""
            🔴 生疏：{result_counts[ReviewResult.AGAIN]} 题
            🟡 困难：{result_counts[ReviewResult.HARD]} 题
            🟢 掌握：{result_counts[ReviewResult.GOOD]} 题
            🔵 熟练：{result_counts[ReviewResult.EASY]} 题
            """
            
            stats_detail = QLabel(stats_text)
            stats_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stats_detail.setStyleSheet("font-size: 14pt; color: #34495e; line-height: 2.0;")
            summary_layout.addWidget(stats_detail)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 继续复习按钮
        continue_btn = QPushButton("🔄 继续复习")
        continue_btn.setMinimumHeight(50)
        continue_btn.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        continue_btn.clicked.connect(self.on_continue_review)
        button_layout.addWidget(continue_btn)
        
        # 返回主页按钮
        home_btn = QPushButton("🏠 返回主页")
        home_btn.setMinimumHeight(50)
        home_btn.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        home_btn.clicked.connect(self.accept)
        button_layout.addWidget(home_btn)
        
        summary_layout.addLayout(button_layout)
        
        self.content_layout.addWidget(summary_frame)
        
        # 更新进度标签
        self.progress_label.setText("复习完成")
    
    def on_continue_review(self):
        """继续复习 - 返回模块选择器"""
        # 发出信号通知主窗口
        self.review_completed.emit()
        # 关闭当前对话框
        self.accept()
