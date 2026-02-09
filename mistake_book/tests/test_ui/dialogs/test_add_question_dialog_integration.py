"""
AddQuestionDialog集成测试

测试要求:
- 测试对话框与Controller集成
- 测试组件信号连接
- 测试完整的添加流程

**Validates: Requirements 3.1**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.add_question.dialog import AddQuestionDialog
from mistake_book.ui.dialogs.add_question.controller import AddQuestionController
from mistake_book.ui.events.event_bus import EventBus
from mistake_book.ui.events.events import QuestionAddedEvent


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例（整个模块共享）"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_question_service():
    """创建mock QuestionService"""
    service = Mock()
    service.ocr_engine = None  # 默认OCR不可用
    service.create_question.return_value = (True, "保存成功", 123)
    return service


@pytest.fixture
def mock_event_bus():
    """创建mock EventBus"""
    event_bus = Mock()
    return event_bus


@pytest.fixture
def controller(mock_question_service, mock_event_bus):
    """创建Controller实例"""
    return AddQuestionController(mock_question_service, mock_event_bus)


@pytest.fixture
def dialog(qapp, controller):
    """创建Dialog实例"""
    dlg = AddQuestionDialog(controller)
    yield dlg
    dlg.close()
    dlg.deleteLater()


class TestDialogInitialization:
    """测试对话框初始化"""
    
    def test_dialog_can_be_instantiated(self, qapp, controller):
        """测试对话框可以实例化"""
        dialog = AddQuestionDialog(controller)
        
        assert dialog is not None
        assert isinstance(dialog, AddQuestionDialog)
        assert dialog.controller == controller
        
        dialog.close()
        dialog.deleteLater()
    
    def test_dialog_has_required_components(self, dialog):
        """测试对话框包含所有必需组件"""
        # 验证组件存在
        assert hasattr(dialog, 'image_uploader')
        assert hasattr(dialog, 'ocr_panel')
        assert hasattr(dialog, 'question_form')
        assert hasattr(dialog, 'save_btn')
        
        # 验证组件不为None
        assert dialog.image_uploader is not None
        assert dialog.ocr_panel is not None
        assert dialog.question_form is not None
        assert dialog.save_btn is not None
    
    def test_dialog_window_properties(self, dialog):
        """测试对话框窗口属性"""
        assert dialog.windowTitle() == "➕ 添加错题"
        assert dialog.minimumWidth() == 800
        assert dialog.minimumHeight() == 700
    
    def test_dialog_components_are_independent_instances(self, qapp, controller):
        """测试每个对话框实例的组件是独立的"""
        dialog1 = AddQuestionDialog(controller)
        dialog2 = AddQuestionDialog(controller)
        
        # 验证组件是不同的实例
        assert dialog1.image_uploader is not dialog2.image_uploader
        assert dialog1.ocr_panel is not dialog2.ocr_panel
        assert dialog1.question_form is not dialog2.question_form
        
        dialog1.close()
        dialog2.close()
        dialog1.deleteLater()
        dialog2.deleteLater()


class TestControllerIntegration:
    """测试对话框与Controller的集成"""
    
    def test_dialog_uses_controller_service(self, dialog, mock_question_service):
        """测试对话框使用Controller的服务"""
        # OCRPanel应该使用controller的question_service
        assert dialog.ocr_panel._question_service == mock_question_service
    
    def test_dialog_controller_reference(self, dialog, controller):
        """测试对话框持有Controller引用"""
        assert dialog.controller is controller
    
    def test_save_calls_controller(self, dialog, controller, mock_question_service):
        """测试保存时调用Controller"""
        # 设置表单数据
        test_data = {
            'subject': '数学',
            'question_type': '选择题',
            'content': '测试题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 3
        }
        dialog.question_form.set_data(test_data)
        
        # 模拟点击保存按钮
        with patch.object(dialog, 'accept') as mock_accept:
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
            
            # 验证controller的save_question被调用
            mock_question_service.create_question.assert_called_once()
            
            # 验证对话框被接受（关闭）
            mock_accept.assert_called_once()


class TestSignalConnections:
    """测试信号连接"""
    
    def test_image_selected_signal_connected(self, dialog):
        """测试图片选择信号已连接"""
        # 模拟图片选择
        test_path = "/path/to/test.png"
        
        with patch.object(dialog.controller, 'on_image_selected') as mock_handler:
            with patch.object(dialog.ocr_panel, 'recognize_image'):
                # 发送信号
                dialog.image_uploader.image_selected.emit(test_path)
                
                # 验证处理器被调用
                mock_handler.assert_called_once_with(test_path)
    
    def test_ocr_completed_signal_connected(self, dialog):
        """测试OCR完成信号已连接"""
        test_text = "识别的文本"
        
        with patch.object(dialog.controller, 'on_ocr_completed', return_value=test_text) as mock_handler:
            with patch.object(dialog.question_form, 'set_content') as mock_set_content:
                with patch.object(dialog.question_form, 'focus_content'):
                    # 发送信号
                    dialog.ocr_panel.recognition_completed.emit(test_text)
                    
                    # 验证处理器被调用
                    mock_handler.assert_called_once_with(test_text)
                    
                    # 验证文本被设置到表单
                    mock_set_content.assert_called_once_with(test_text)
    
    def test_ocr_failed_signal_connected(self, dialog):
        """测试OCR失败信号已连接"""
        error_message = "OCR识别失败"
        
        # 发送信号（不应该抛出异常）
        dialog.ocr_panel.recognition_failed.emit(error_message)
        
        # 如果包含特定关键词，会显示对话框
        # 这里只验证信号连接正常，不会崩溃
    
    def test_save_button_connected(self, dialog):
        """测试保存按钮已连接"""
        # 验证保存按钮的clicked信号已连接
        # 通过检查是否有连接的接收者
        assert dialog.save_btn.receivers(dialog.save_btn.clicked) > 0


class TestCompleteWorkflow:
    """测试完整的添加流程"""
    
    def test_workflow_without_image(self, dialog, mock_question_service):
        """测试不使用图片的完整流程"""
        # 1. 填写表单
        test_data = {
            'subject': '物理',
            'question_type': '计算题',
            'content': '手动输入的题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '详细解析',
            'difficulty': 4
        }
        dialog.question_form.set_data(test_data)
        
        # 2. 点击保存
        with patch.object(dialog, 'accept') as mock_accept:
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
            
            # 3. 验证保存成功
            mock_question_service.create_question.assert_called_once()
            call_args = mock_question_service.create_question.call_args[0][0]
            
            # 验证数据正确传递
            assert call_args['subject'] == '物理'
            assert call_args['content'] == '手动输入的题目内容'
            assert call_args['answer'] == '正确答案'
            
            # 验证对话框关闭
            mock_accept.assert_called_once()
    
    def test_workflow_with_image_and_ocr(self, dialog, mock_question_service):
        """测试使用图片和OCR的完整流程"""
        # 1. 选择图片 - 使用set_image来正确设置图片路径
        test_image_path = "/path/to/question.png"
        
        # Mock the image loading to avoid file system access
        with patch.object(dialog.image_uploader, '_load_image', return_value=True) as mock_load:
            # Manually set the path since _load_image is mocked
            dialog.image_uploader._current_image_path = test_image_path
            dialog.image_uploader.set_image(test_image_path)
        
        # 2. 模拟OCR识别完成
        ocr_text = "OCR识别的题目内容"
        dialog.ocr_panel.recognition_completed.emit(ocr_text)
        
        # 验证文本被填充到表单
        form_data = dialog.question_form.get_data()
        assert form_data['content'] == ocr_text
        
        # 3. 补充其他信息
        dialog.question_form.set_data({
            'subject': '化学',
            'question_type': '简答题',
            'content': ocr_text,
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 5
        })
        
        # 4. 保存
        with patch.object(dialog, 'accept') as mock_accept:
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
            
            # 验证保存成功
            mock_question_service.create_question.assert_called_once()
            call_args = mock_question_service.create_question.call_args[0][0]
            
            # 验证包含图片路径
            assert call_args['image_path'] == test_image_path
            assert call_args['content'] == ocr_text
            
            mock_accept.assert_called_once()
    
    def test_workflow_validation_failure(self, dialog, mock_question_service):
        """测试验证失败的流程"""
        # 不填写必填字段
        dialog.question_form.clear()
        
        # 尝试保存
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
            
            # 验证显示了警告
            mock_warning.assert_called_once()
            
            # 验证没有调用服务保存
            mock_question_service.create_question.assert_not_called()
    
    def test_workflow_save_failure(self, dialog, mock_question_service):
        """测试保存失败的流程"""
        # 模拟服务返回失败
        mock_question_service.create_question.return_value = (False, "数据库错误", None)
        
        # 填写表单
        test_data = {
            'subject': '数学',
            'question_type': '选择题',
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '答案',
            'explanation': '解析',
            'difficulty': 3
        }
        dialog.question_form.set_data(test_data)
        
        # 尝试保存
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            with patch.object(dialog, 'accept') as mock_accept:
                QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
                
                # 验证显示了错误消息
                mock_warning.assert_called_once()
                
                # 验证对话框没有关闭
                mock_accept.assert_not_called()


class TestEventBusIntegration:
    """测试事件总线集成"""
    
    def test_save_publishes_event(self, qapp, mock_question_service):
        """测试保存成功时发布事件"""
        # 使用真实的EventBus
        event_bus = EventBus()
        event_bus.clear()
        
        controller = AddQuestionController(mock_question_service, event_bus)
        dialog = AddQuestionDialog(controller)
        
        # 订阅事件
        received_events = []
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe(QuestionAddedEvent, event_handler)
        
        # 填写表单
        test_data = {
            'subject': '英语',
            'question_type': '翻译题',
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 2
        }
        dialog.question_form.set_data(test_data)
        
        # 保存
        with patch.object(dialog, 'accept'):
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
        
        # 验证事件被发布
        assert len(received_events) == 1
        assert isinstance(received_events[0], QuestionAddedEvent)
        assert received_events[0].question_id == 123
        
        # 清理
        event_bus.clear()
        dialog.close()
        dialog.deleteLater()


class TestUIBehavior:
    """测试UI行为"""
    
    def test_save_button_disabled_during_save(self, dialog, mock_question_service):
        """测试保存时按钮被禁用"""
        # 填写表单
        test_data = {
            'subject': '数学',
            'question_type': '选择题',
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '答案',
            'explanation': '解析',
            'difficulty': 3
        }
        dialog.question_form.set_data(test_data)
        
        # 模拟慢速保存
        def slow_save(*args, **kwargs):
            # 在这个时刻，按钮应该是禁用的
            assert not dialog.save_btn.isEnabled()
            assert dialog.save_btn.text() == "保存中..."
            return (True, "保存成功", 123)
        
        mock_question_service.create_question.side_effect = slow_save
        
        with patch.object(dialog, 'accept'):
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
        
        # 保存完成后，按钮应该恢复
        assert dialog.save_btn.isEnabled()
        assert dialog.save_btn.text() == "💾 保存"
    
    def test_save_button_restored_on_validation_failure(self, dialog):
        """测试验证失败时按钮状态恢复"""
        # 不填写表单（验证会失败）
        dialog.question_form.clear()
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning'):
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
        
        # 按钮应该恢复可用
        assert dialog.save_btn.isEnabled()
        assert dialog.save_btn.text() == "💾 保存"
    
    def test_save_button_restored_on_save_failure(self, dialog, mock_question_service):
        """测试保存失败时按钮状态恢复"""
        # 模拟保存失败
        mock_question_service.create_question.return_value = (False, "保存失败", None)
        
        # 填写表单
        test_data = {
            'subject': '数学',
            'question_type': '选择题',
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '答案',
            'explanation': '解析',
            'difficulty': 3
        }
        dialog.question_form.set_data(test_data)
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning'):
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
        
        # 按钮应该恢复可用
        assert dialog.save_btn.isEnabled()
        assert dialog.save_btn.text() == "💾 保存"


class TestComponentInteraction:
    """测试组件间交互"""
    
    def test_image_uploader_to_ocr_panel(self, dialog):
        """测试图片上传器到OCR面板的交互"""
        test_path = "/path/to/image.png"
        
        with patch.object(dialog.ocr_panel, 'recognize_image') as mock_recognize:
            # 模拟图片选择
            dialog.image_uploader.image_selected.emit(test_path)
            
            # 验证OCR面板的recognize_image被调用
            mock_recognize.assert_called_once_with(test_path)
    
    def test_ocr_panel_to_question_form(self, dialog):
        """测试OCR面板到题目表单的交互"""
        test_text = "识别的题目内容"
        
        # 模拟OCR完成
        dialog.ocr_panel.recognition_completed.emit(test_text)
        
        # 验证文本被设置到表单
        form_data = dialog.question_form.get_data()
        assert form_data['content'] == test_text
    
    def test_question_form_to_controller(self, qapp, mock_event_bus):
        """测试题目表单到控制器的交互"""
        # Create a fresh mock service for this test
        fresh_mock_service = Mock()
        fresh_mock_service.ocr_engine = None
        fresh_mock_service.create_question.return_value = (True, "保存成功", 123)
        
        # Create a fresh dialog for this test to avoid state pollution
        controller = AddQuestionController(fresh_mock_service, mock_event_bus)
        dialog = AddQuestionDialog(controller)
        
        # 填写表单 - 使用有效的科目名称
        test_data = {
            'subject': '物理',  # Changed from '生物' to '物理' (valid subject)
            'question_type': '计算题',  # Changed to match available types
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 1
        }
        dialog.question_form.set_data(test_data)
        
        # 保存
        with patch.object(dialog, 'accept'):
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
        
        # 验证数据传递到controller
        fresh_mock_service.create_question.assert_called_once()
        call_args = fresh_mock_service.create_question.call_args[0][0]
        
        assert call_args['subject'] == '物理'
        assert call_args['content'] == '题目内容'
        assert call_args['answer'] == '正确答案'
        
        # Cleanup
        dialog.close()
        dialog.deleteLater()


class TestDialogLifecycle:
    """测试对话框生命周期"""
    
    def test_dialog_can_be_opened_multiple_times(self, qapp, controller):
        """测试对话框可以多次打开"""
        # 第一次打开
        dialog1 = AddQuestionDialog(controller)
        assert dialog1 is not None
        dialog1.close()
        dialog1.deleteLater()
        
        # 第二次打开
        dialog2 = AddQuestionDialog(controller)
        assert dialog2 is not None
        dialog2.close()
        dialog2.deleteLater()
        
        # 验证是不同的实例
        assert dialog1 is not dialog2
    
    def test_dialog_cleanup_on_close(self, qapp, controller):
        """测试对话框关闭时的清理"""
        dialog = AddQuestionDialog(controller)
        
        # 设置一些数据
        dialog.question_form.set_data({
            'subject': '数学',
            'content': '题目',
            'answer': '答案'
        })
        dialog.controller.on_image_selected("/path/to/image.png")
        
        # 关闭对话框
        dialog.close()
        dialog.deleteLater()
        
        # 创建新对话框，应该是干净的状态
        new_dialog = AddQuestionDialog(controller)
        form_data = new_dialog.get_data() if hasattr(new_dialog, 'get_data') else new_dialog.question_form.get_data()
        
        # 新对话框的表单应该是空的
        assert form_data['content'] == ''
        
        new_dialog.close()
        new_dialog.deleteLater()


class TestErrorHandling:
    """测试错误处理"""
    
    def test_handle_ocr_initialization_error(self, dialog):
        """测试处理OCR初始化错误"""
        error_message = "OCR引擎未初始化，请下载模型"
        
        # 模拟OCR失败
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.ocr_panel.recognition_failed.emit(error_message)
            
            # 验证显示了警告对话框
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "OCR初始化提示" in call_args[1]
    
    def test_handle_service_exception(self, dialog, mock_question_service):
        """测试处理服务层异常"""
        # 模拟服务抛出异常
        mock_question_service.create_question.side_effect = Exception("数据库连接失败")
        
        # 填写表单
        test_data = {
            'subject': '数学',
            'question_type': '选择题',
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '答案',
            'explanation': '解析',
            'difficulty': 3
        }
        dialog.question_form.set_data(test_data)
        
        # 尝试保存
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            QTest.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)
            
            # 验证显示了错误消息
            mock_warning.assert_called_once()
            
            # 验证按钮状态恢复
            assert dialog.save_btn.isEnabled()
    
    def test_handle_empty_ocr_result(self, dialog):
        """测试处理空的OCR结果"""
        # 模拟OCR返回空字符串
        dialog.ocr_panel.recognition_completed.emit("")
        
        # 验证表单内容为空（不应该崩溃）
        form_data = dialog.question_form.get_data()
        assert form_data['content'] == ""


class TestAccessibility:
    """测试可访问性"""
    
    def test_save_button_is_default(self, dialog):
        """测试保存按钮是默认按钮"""
        assert dialog.save_btn.isDefault()
    
    def test_dialog_has_window_title(self, dialog):
        """测试对话框有窗口标题"""
        assert dialog.windowTitle() != ""
        assert "添加错题" in dialog.windowTitle()
    
    def test_components_are_visible(self, dialog):
        """测试组件可见"""
        # Show the dialog to make components visible
        dialog.show()
        
        assert dialog.image_uploader.isVisible()
        assert dialog.ocr_panel.isVisible()
        assert dialog.question_form.isVisible()
        assert dialog.save_btn.isVisible()
        
        dialog.hide()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
