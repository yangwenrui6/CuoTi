"""复习对话框 - UI组装器"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from pathlib import Path
from mistake_book.config.constants import ReviewResult
import logging

logger = logging.getLogger(__name__)


class ReviewDialog(QDialog):
    """复习对话框 - 使用Controller模式"""
    
    # 信号：复习完成，请求返回模块选择器
    review_completed = pyqtSignal()
    
    def __init__(self, controller, parent=None):
        """
        初始化对话框
        
        Args:
            controller: ReviewDialogController实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.controller = controller
        
        self.setWindowTitle("📚 复习模式")
        self.setMinimumSize(900, 700)
        
        self._init_ui()
        self._load_question()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部：进度和关闭按钮
        self._create_top_bar(layout)
        
        # 中间：题目内容区（可滚动）
        self._create_content_area(layout)
        
        # 底部：操作按钮区
        self._create_bottom_buttons(layout)
    
    def _create_top_bar(self, parent_layout):
        """创建顶部栏"""
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
        close_btn.clicked.connect(self._on_finish_review)
        top_layout.addWidget(close_btn)
        
        parent_layout.addLayout(top_layout)
    
    def _create_content_area(self, parent_layout):
        """创建内容区域"""
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
        parent_layout.addWidget(scroll, 1)
    
    def _create_bottom_buttons(self, parent_layout):
        """创建底部按钮区"""
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
        self.show_answer_btn.clicked.connect(self._toggle_answer)
        self.bottom_layout.addWidget(self.show_answer_btn)
        
        # 掌握度按钮组（初始隐藏）
        self._create_mastery_buttons()
        
        parent_layout.addWidget(self.bottom_widget)
    
    def _create_mastery_buttons(self):
        """创建掌握度评分按钮"""
        self.mastery_widget = QWidget()
        mastery_layout = QHBoxLayout(self.mastery_widget)
        mastery_layout.setSpacing(10)
        
        # 提示标签
        tip_label = QLabel("请评价您的掌握程度：")
        tip_label.setStyleSheet("font-size: 12pt; color: #7f8c8d;")
        mastery_layout.addWidget(tip_label)
        
        # 四个掌握度按钮
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
            btn.clicked.connect(lambda checked, r=result: self._on_quality_selected(r))
            mastery_layout.addWidget(btn)
        
        self.mastery_widget.setVisible(False)
        self.bottom_layout.addWidget(self.mastery_widget)
    
    def _load_question(self):
        """加载当前题目"""
        # 清空内容区
        self._clear_content()
        
        # 从Controller获取当前题目
        question = self.controller.get_current_question()
        
        if not question:
            # 没有更多题目，显示总结
            self._show_summary()
            return
        
        # 更新进度
        self._update_progress()
        
        # 显示题目信息
        self._display_question_info(question)
        
        # 显示题目图片（如果有）
        self._display_question_image(question)
        
        # 显示题目内容
        self._display_question_content(question)
        
        # 创建答案区域（初始隐藏）
        self._create_answer_area(question)
        
        self.content_layout.addStretch()
        
        # 重置按钮状态
        self.show_answer_btn.setVisible(True)
        self.show_answer_btn.setText("👁️ 显示答案")
        self.mastery_widget.setVisible(False)
    
    def _clear_content(self):
        """清空内容区"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _update_progress(self):
        """更新进度显示"""
        current, total = self.controller.get_progress()
        self.progress_label.setText(f"题目 {current} / {total}")
    
    def _display_question_info(self, question):
        """显示题目信息卡片"""
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
    
    def _display_question_image(self, question):
        """显示题目图片"""
        image_path = question.get('image_path')
        if not image_path or not Path(image_path).exists():
            return
        
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
        scaled = pixmap.scaled(
            800, 400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        image_label.setPixmap(scaled)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(image_label)
        
        self.content_layout.addWidget(image_frame)
    
    def _display_question_content(self, question):
        """显示题目内容"""
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
    
    def _create_answer_area(self, question):
        """创建答案区域"""
        self.answer_widget = QWidget()
        answer_layout = QVBoxLayout(self.answer_widget)
        answer_layout.setSpacing(15)
        
        # 我的答案
        my_answer = question.get('my_answer', '')
        if my_answer:
            self._add_my_answer_section(answer_layout, my_answer)
        
        # 正确答案
        correct_answer = question.get('answer', '')
        if correct_answer:
            self._add_correct_answer_section(answer_layout, correct_answer)
        
        # 解析
        explanation = question.get('explanation', '')
        if explanation:
            self._add_explanation_section(answer_layout, explanation)
        
        self.answer_widget.setVisible(False)
        self.content_layout.addWidget(self.answer_widget)
    
    def _add_my_answer_section(self, parent_layout, my_answer):
        """添加我的答案部分"""
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
        
        parent_layout.addWidget(my_answer_frame)
    
    def _add_correct_answer_section(self, parent_layout, correct_answer):
        """添加正确答案部分"""
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
        
        parent_layout.addWidget(correct_frame)
    
    def _add_explanation_section(self, parent_layout, explanation):
        """添加解析部分"""
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
        
        parent_layout.addWidget(exp_frame)
    
    def _toggle_answer(self):
        """切换答案显示"""
        is_visible = self.answer_widget.isVisible()
        self.answer_widget.setVisible(not is_visible)
        
        if not is_visible:
            # 显示答案后，隐藏显示按钮，显示掌握度按钮
            self.show_answer_btn.setVisible(False)
            self.mastery_widget.setVisible(True)
    
    def _on_quality_selected(self, result: ReviewResult):
        """
        处理质量评分选择
        
        Args:
            result: ReviewResult枚举值
        """
        logger.info(f"用户选择掌握度: {result}")
        
        # 调用Controller提交复习结果
        has_next = self.controller.submit_review(result.value)
        
        if has_next:
            # 还有下一题，加载下一题
            self._load_question()
        else:
            # 没有更多题目，显示总结
            self._show_summary()
    
    def _on_finish_review(self):
        """结束复习按钮点击"""
        if self.controller.has_more_questions():
            # 还有未复习的题目，询问是否确认结束
            current, total = self.controller.get_progress()
            remaining = total - current + 1
            
            reply = QMessageBox.question(
                self,
                "确认结束",
                f"还有 {remaining} 道题目未复习，确定要结束吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        self._show_summary()
    
    def _show_summary(self):
        """显示复习总结"""
        # 清空内容区
        self._clear_content()
        
        # 隐藏底部按钮
        self.bottom_widget.setVisible(False)
        
        # 创建总结卡片
        summary_frame = self._create_summary_frame()
        self.content_layout.addWidget(summary_frame)
        
        # 更新进度标签
        self.progress_label.setText("复习完成")
    
    def _create_summary_frame(self):
        """创建总结卡片"""
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
        reviewed_count = self.controller.get_reviewed_count()
        stats_label = QLabel(f"本次复习了 {reviewed_count} 道题目")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("font-size: 16pt; color: #2c3e50; margin: 20px 0;")
        summary_layout.addWidget(stats_label)
        
        # 按钮区域
        self._add_summary_buttons(summary_layout)
        
        return summary_frame
    
    def _add_summary_buttons(self, parent_layout):
        """添加总结页面的按钮"""
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
        continue_btn.clicked.connect(self._on_continue_review)
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
        
        parent_layout.addLayout(button_layout)
    
    def _on_continue_review(self):
        """继续复习 - 返回模块选择器"""
        # 发出信号通知主窗口
        self.review_completed.emit()
        # 关闭当前对话框
        self.accept()
