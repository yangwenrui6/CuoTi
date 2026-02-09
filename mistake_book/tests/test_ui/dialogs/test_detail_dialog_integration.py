"""
DetailDialog集成测试

测试要求:
- 测试对话框与Controller集成
- 测试UI组件创建
- 测试信号连接
- 测试保存和关闭逻辑

**Validates: Requirements 3.1**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.detail.controller import DetailDialogController
from mistake_book.ui.dialogs.detail.dialog import DetailDialog


# 创建QApplication实例（PyQt需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestDetailDialogInitialization:
    """测试对话框初始化"""
    
    def test_dialog_can_be_instantiated_with_controller(self, qapp):
        """测试对话框可以使用控制器实例化"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        assert dialog is not None
        assert isinstance(dialog, DetailDialog)
        assert dialog.controller == controller

    
    def test_dialog_creates_all_ui_components(self, qapp):
        """测试对话框创建所有UI组件"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 验证可编辑控件被创建
        assert dialog.content_edit is not None
        assert dialog.my_answer_edit is not None
        assert dialog.correct_answer_edit is not None
        assert dialog.explanation_edit is not None
    
    def test_dialog_loads_question_data(self, qapp):
        """测试对话框加载题目数据"""
        mock_service = Mock()
        question_data = {
            'id': 123,
            'content': '测试题目内容',
            'my_answer': '测试我的答案',
            'answer': '测试正确答案',
            'explanation': '测试解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 验证数据被加载到UI
        assert dialog.content_edit.toPlainText() == '测试题目内容'
        assert dialog.my_answer_edit.toPlainText() == '测试我的答案'
        assert dialog.correct_answer_edit.toPlainText() == '测试正确答案'
        assert dialog.explanation_edit.toPlainText() == '测试解析'


class TestDetailDialogSaveLogic:
    """测试保存逻辑"""
    
    @patch('mistake_book.ui.dialogs.detail.dialog.QMessageBox.information')
    def test_save_with_no_changes_shows_message(self, mock_info, qapp):
        """测试没有修改时保存显示提示"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 点击保存按钮（没有修改）
        dialog._on_save_clicked()
        
        # 验证显示提示信息
        mock_info.assert_called_once()
        # QMessageBox.information(parent, title, message)
        # args[0] is parent, args[1] is title, args[2] is message
        call_args = mock_info.call_args[0]
        message = call_args[2] if len(call_args) > 2 else call_args[1]
        assert "没有修改" in message
    
    @patch('mistake_book.ui.dialogs.detail.dialog.QMessageBox.information')
    def test_save_with_changes_calls_controller(self, mock_info, qapp):
        """测试有修改时保存调用控制器"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 修改内容
        dialog.content_edit.setPlainText('修改后的题目')
        
        # 点击保存按钮
        dialog._on_save_clicked()
        
        # 验证服务被调用
        mock_service.update_question.assert_called_once()
        
        # 验证显示成功消息
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "成功" in args[1]

    
    @patch('mistake_book.ui.dialogs.detail.dialog.QMessageBox.warning')
    def test_save_failure_shows_error(self, mock_warning, qapp):
        """测试保存失败显示错误"""
        mock_service = Mock()
        mock_service.update_question.return_value = (False, "数据库错误")
        
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 修改内容
        dialog.content_edit.setPlainText('修改后的题目')
        
        # 点击保存按钮
        dialog._on_save_clicked()
        
        # 验证显示错误消息
        mock_warning.assert_called_once()
        # QMessageBox.warning(parent, title, message)
        call_args = mock_warning.call_args[0]
        message = call_args[2] if len(call_args) > 2 else call_args[1]
        assert "数据库错误" in message


class TestDetailDialogCloseLogic:
    """测试关闭逻辑"""
    
    def test_close_without_changes_accepts(self, qapp):
        """测试没有修改时直接关闭"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 点击关闭按钮
        dialog._on_close_clicked()
        
        # 对话框应该被接受（关闭）
        # 注意：在测试中我们无法直接验证accept()被调用，
        # 但可以验证没有显示确认对话框
    
    @patch('mistake_book.ui.dialogs.detail.dialog.QMessageBox.question')
    def test_close_with_changes_shows_confirmation(self, mock_question, qapp):
        """测试有修改时关闭显示确认对话框"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 修改内容
        dialog.content_edit.setPlainText('修改后的题目')
        
        # 模拟用户选择"放弃"
        mock_question.return_value = QMessageBox.StandardButton.Discard
        
        # 点击关闭按钮
        dialog._on_close_clicked()
        
        # 验证显示确认对话框
        mock_question.assert_called_once()
        # QMessageBox.question(parent, title, message, buttons, default)
        call_args = mock_question.call_args[0]
        message = call_args[2] if len(call_args) > 2 else call_args[1]
        assert "未保存" in message


class TestDetailDialogDataFlow:
    """测试数据流"""
    
    def test_get_current_data_returns_form_values(self, qapp):
        """测试获取当前数据返回表单值"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        dialog = DetailDialog(controller)
        
        # 修改表单
        dialog.content_edit.setPlainText('新题目')
        dialog.my_answer_edit.setPlainText('新答案')
        dialog.correct_answer_edit.setPlainText('新正确答案')
        dialog.explanation_edit.setPlainText('新解析')
        
        # 获取当前数据
        current_data = dialog._get_current_data()
        
        # 验证数据正确
        assert current_data['content'] == '新题目'
        assert current_data['my_answer'] == '新答案'
        assert current_data['answer'] == '新正确答案'
        assert current_data['explanation'] == '新解析'


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
