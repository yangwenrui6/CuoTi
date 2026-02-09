"""ReviewDialog集成测试"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.review.dialog import ReviewDialog
from mistake_book.ui.dialogs.review.controller import ReviewDialogController
from mistake_book.config.constants import ReviewResult


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestReviewDialogIntegration:
    """ReviewDialog集成测试类"""
    
    @pytest.fixture
    def mock_review_service(self):
        """创建mock ReviewService"""
        service = Mock()
        service.process_review_result.return_value = (True, "成功", {
            'interval': 1,
            'repetitions': 1,
            'easiness_factor': 2.5,
            'mastery_level': 2
        })
        return service
    
    @pytest.fixture
    def sample_questions(self):
        """创建示例题目列表"""
        return [
            {
                'id': 1,
                'subject': '数学',
                'question_type': '单选题',
                'content': '1 + 1 = ?',
                'my_answer': '3',
                'answer': '2',
                'explanation': '基础加法',
                'difficulty': 1
            },
            {
                'id': 2,
                'subject': '英语',
                'question_type': '填空题',
                'content': 'What is your name?',
                'my_answer': '',
                'answer': 'My name is...',
                'explanation': '自我介绍',
                'difficulty': 2
            }
        ]
    
    @pytest.fixture
    def controller(self, mock_review_service, sample_questions):
        """创建控制器"""
        return ReviewDialogController(
            mock_review_service,
            sample_questions
        )
    
    def test_dialog_initialization(self, qapp, controller):
        """测试对话框初始化"""
        dialog = ReviewDialog(controller)
        
        assert dialog is not None
        assert dialog.controller == controller
        assert dialog.windowTitle() == "📚 复习模式"
        
        # 验证UI组件存在
        assert hasattr(dialog, 'progress_label')
        assert hasattr(dialog, 'content_widget')
        assert hasattr(dialog, 'show_answer_btn')
        assert hasattr(dialog, 'mastery_widget')
        
        dialog.close()
    
    def test_dialog_displays_first_question(self, qapp, controller):
        """测试对话框显示第一道题目"""
        dialog = ReviewDialog(controller)
        dialog.show()  # 需要显示对话框才能检查可见性
        
        # 验证进度显示
        assert "题目 1 / 2" in dialog.progress_label.text()
        
        # 验证显示答案按钮可见
        assert dialog.show_answer_btn.isVisible()
        
        # 验证掌握度按钮初始隐藏
        assert not dialog.mastery_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_toggle_answer(self, qapp, controller):
        """测试切换答案显示"""
        dialog = ReviewDialog(controller)
        dialog.show()  # 需要显示对话框
        
        # 初始状态：答案隐藏
        assert not dialog.answer_widget.isVisible()
        assert dialog.show_answer_btn.isVisible()
        assert not dialog.mastery_widget.isVisible()
        
        # 点击显示答案
        dialog._toggle_answer()
        
        # 答案显示，显示按钮隐藏，掌握度按钮显示
        assert dialog.answer_widget.isVisible()
        assert not dialog.show_answer_btn.isVisible()
        assert dialog.mastery_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_submit_review_and_next_question(self, qapp, controller):
        """测试提交复习并进入下一题"""
        dialog = ReviewDialog(controller)
        dialog.show()  # 需要显示对话框
        
        # 显示答案
        dialog._toggle_answer()
        
        # 选择掌握度
        dialog._on_quality_selected(ReviewResult.GOOD)
        
        # 验证进入下一题
        assert "题目 2 / 2" in dialog.progress_label.text()
        
        # 验证按钮状态重置
        assert dialog.show_answer_btn.isVisible()
        assert not dialog.mastery_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_complete_all_questions(self, qapp, controller):
        """测试完成所有题目"""
        dialog = ReviewDialog(controller)
        
        # 完成第一题
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        
        # 完成第二题
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.EASY)
        
        # 验证显示总结页面
        assert "复习完成" in dialog.progress_label.text()
        assert not dialog.bottom_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_finish_review_with_confirmation(self, qapp, controller):
        """测试结束复习时的确认对话框"""
        dialog = ReviewDialog(controller)
        dialog.show()  # 需要显示对话框
        
        # Mock QMessageBox
        with patch('mistake_book.ui.dialogs.review.dialog.QMessageBox.question') as mock_question:
            # 模拟用户选择"否"
            from PyQt6.QtWidgets import QMessageBox
            mock_question.return_value = QMessageBox.StandardButton.No
            
            # 点击结束复习
            dialog._on_finish_review()
            
            # 验证显示了确认对话框
            mock_question.assert_called_once()
            
            # 验证没有显示总结（因为用户选择了"否"）
            assert dialog.bottom_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_finish_review_confirmed(self, qapp, controller):
        """测试确认结束复习"""
        dialog = ReviewDialog(controller)
        
        # Mock QMessageBox
        with patch('mistake_book.ui.dialogs.review.dialog.QMessageBox.question') as mock_question:
            # 模拟用户选择"是"
            from PyQt6.QtWidgets import QMessageBox
            mock_question.return_value = QMessageBox.StandardButton.Yes
            
            # 点击结束复习
            dialog._on_finish_review()
            
            # 验证显示了总结
            assert "复习完成" in dialog.progress_label.text()
        
        dialog.close()
    
    def test_dialog_continue_review_signal(self, qapp, controller):
        """测试继续复习信号"""
        dialog = ReviewDialog(controller)
        
        # 连接信号
        signal_received = []
        dialog.review_completed.connect(lambda: signal_received.append(True))
        
        # 完成所有题目
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        
        # 点击继续复习
        dialog._on_continue_review()
        
        # 验证信号发出
        assert len(signal_received) == 1
        
        dialog.close()
    
    def test_dialog_with_image_question(self, qapp, mock_review_service, tmp_path):
        """测试显示带图片的题目"""
        # 创建临时图片文件
        image_path = tmp_path / "test_image.png"
        
        # 创建一个简单的PNG图片
        from PyQt6.QtGui import QImage, QPainter
        image = QImage(100, 100, QImage.Format.Format_RGB32)
        painter = QPainter(image)
        painter.fillRect(0, 0, 100, 100, Qt.GlobalColor.white)
        painter.end()
        image.save(str(image_path))
        
        questions = [{
            'id': 1,
            'subject': '数学',
            'question_type': '单选题',
            'content': '测试题目',
            'answer': '答案',
            'image_path': str(image_path),
            'difficulty': 3
        }]
        
        controller = ReviewDialogController(mock_review_service, questions)
        dialog = ReviewDialog(controller)
        
        # 验证对话框创建成功
        assert dialog is not None
        
        dialog.close()
    
    def test_dialog_with_question_without_my_answer(self, qapp, mock_review_service):
        """测试没有我的答案的题目"""
        questions = [{
            'id': 1,
            'subject': '数学',
            'question_type': '单选题',
            'content': '测试题目',
            'my_answer': '',  # 空的我的答案
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 2
        }]
        
        controller = ReviewDialogController(mock_review_service, questions)
        dialog = ReviewDialog(controller)
        dialog.show()  # 需要显示对话框
        
        # 显示答案
        dialog._toggle_answer()
        
        # 验证答案区域显示
        assert dialog.answer_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_progress_display(self, qapp, controller):
        """测试进度显示"""
        dialog = ReviewDialog(controller)
        
        # 第一题
        assert "题目 1 / 2" in dialog.progress_label.text()
        
        # 进入第二题
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        assert "题目 2 / 2" in dialog.progress_label.text()
        
        # 完成所有题目
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        assert "复习完成" in dialog.progress_label.text()
        
        dialog.close()
    
    def test_dialog_controller_integration(self, qapp, mock_review_service, sample_questions):
        """
        测试对话框与Controller集成
        
        验证：
        - Dialog正确使用Controller获取题目
        - Dialog正确调用Controller提交复习
        - Dialog正确响应Controller的返回值
        """
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        dialog = ReviewDialog(controller)
        
        # 验证初始状态
        assert controller.get_reviewed_count() == 0
        assert controller.current_index == 0
        
        # 提交第一题
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        
        # 验证Controller状态更新
        assert controller.get_reviewed_count() == 1
        assert controller.current_index == 1
        
        # 验证服务被调用
        mock_review_service.process_review_result.assert_called_once_with(
            1, ReviewResult.GOOD
        )
        
        dialog.close()
    
    def test_dialog_handles_service_failure(self, qapp, sample_questions):
        """测试对话框处理服务失败的情况"""
        # 创建失败的服务
        mock_service = Mock()
        mock_service.process_review_result.return_value = (False, "保存失败", {})
        
        controller = ReviewDialogController(mock_service, sample_questions)
        dialog = ReviewDialog(controller)
        
        # 提交复习（即使服务失败也应该继续）
        dialog._toggle_answer()
        dialog._on_quality_selected(ReviewResult.GOOD)
        
        # 验证进入下一题
        assert "题目 2 / 2" in dialog.progress_label.text()
        
        dialog.close()
    
    def test_dialog_all_quality_levels(self, qapp, mock_review_service):
        """测试所有质量评分级别"""
        questions = [
            {'id': i, 'content': f'题目{i}', 'answer': f'答案{i}', 'difficulty': 1}
            for i in range(1, 5)
        ]
        
        controller = ReviewDialogController(mock_review_service, questions)
        dialog = ReviewDialog(controller)
        
        quality_levels = [
            ReviewResult.AGAIN,
            ReviewResult.HARD,
            ReviewResult.GOOD,
            ReviewResult.EASY
        ]
        
        for quality in quality_levels:
            dialog._toggle_answer()
            dialog._on_quality_selected(quality)
        
        # 验证所有评分都被提交
        assert mock_review_service.process_review_result.call_count == 4
        
        # 验证显示总结
        assert "复习完成" in dialog.progress_label.text()
        
        dialog.close()
    
    def test_dialog_empty_questions_list(self, qapp, mock_review_service):
        """测试空题目列表"""
        controller = ReviewDialogController(mock_review_service, [])
        dialog = ReviewDialog(controller)
        
        # 应该直接显示总结
        assert "复习完成" in dialog.progress_label.text()
        assert not dialog.bottom_widget.isVisible()
        
        dialog.close()
    
    def test_dialog_ui_components_exist(self, qapp, controller):
        """测试所有UI组件都存在"""
        dialog = ReviewDialog(controller)
        
        # 验证顶部组件
        assert dialog.progress_label is not None
        
        # 验证内容区域
        assert dialog.content_widget is not None
        assert dialog.content_layout is not None
        
        # 验证底部按钮
        assert dialog.bottom_widget is not None
        assert dialog.show_answer_btn is not None
        assert dialog.mastery_widget is not None
        
        # 验证答案区域
        assert dialog.answer_widget is not None
        
        dialog.close()
    
    def test_dialog_minimum_size(self, qapp, controller):
        """测试对话框最小尺寸"""
        dialog = ReviewDialog(controller)
        
        min_size = dialog.minimumSize()
        assert min_size.width() == 900
        assert min_size.height() == 700
        
        dialog.close()
