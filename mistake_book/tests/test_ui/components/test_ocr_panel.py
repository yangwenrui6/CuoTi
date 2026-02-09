"""
OCRPanel组件单元测试

测试要求:
- 测试组件独立实例化
- 测试mock OCR服务
- 测试信号发送

**Validates: Requirements 3.1, 3.3**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.components.ocr_panel import OCRPanel, OCRWorker


# 创建QApplication实例（PyQt测试需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_question_service():
    """创建mock QuestionService"""
    service = Mock()
    
    # Mock OCR引擎
    mock_ocr_engine = Mock()
    mock_ocr_engine.is_available.return_value = True
    mock_ocr_engine._initialized = True
    mock_ocr_engine.is_initializing.return_value = False
    
    service.ocr_engine = mock_ocr_engine
    service.recognize_image_with_retry.return_value = (True, "识别成功", "识别的文本内容")
    
    return service


@pytest.fixture
def mock_unavailable_service():
    """创建OCR不可用的mock服务"""
    service = Mock()
    
    # Mock OCR引擎为不可用
    mock_ocr_engine = Mock()
    mock_ocr_engine.is_available.return_value = False
    mock_ocr_engine._initialized = False
    mock_ocr_engine.is_initializing.return_value = False
    
    service.ocr_engine = mock_ocr_engine
    
    return service


@pytest.fixture
def mock_no_ocr_service():
    """创建没有OCR引擎的mock服务"""
    service = Mock()
    service.ocr_engine = None
    return service


@pytest.fixture
def test_image_path(tmp_path):
    """创建测试图片路径"""
    image_path = tmp_path / "test_image.png"
    # 创建一个空文件
    image_path.write_bytes(b"fake image data")
    return str(image_path)


class TestOCRPanelInitialization:
    """测试组件独立实例化"""
    
    def test_component_can_be_instantiated(self, qapp, mock_question_service):
        """测试组件可以独立实例化"""
        panel = OCRPanel(mock_question_service)
        assert panel is not None
        assert isinstance(panel, OCRPanel)
    
    def test_initial_state(self, qapp, mock_question_service):
        """测试初始状态"""
        panel = OCRPanel(mock_question_service)
        assert panel._question_service == mock_question_service
        assert panel._is_recognizing is False
        assert panel._current_image_path is None
        assert panel._worker is None
    
    def test_component_without_parent(self, qapp, mock_question_service):
        """测试组件可以在没有父组件的情况下实例化"""
        panel = OCRPanel(mock_question_service, parent=None)
        assert panel is not None
        assert panel.parent() is None
    
    def test_multiple_instances_independent(self, qapp, mock_question_service):
        """测试多个实例互不干扰"""
        panel1 = OCRPanel(mock_question_service)
        panel2 = OCRPanel(mock_question_service)
        
        assert panel1 is not panel2
        assert panel1._is_recognizing is False
        assert panel2._is_recognizing is False
        assert panel1._current_image_path is None
        assert panel2._current_image_path is None
    
    def test_ui_elements_initialized(self, qapp, mock_question_service):
        """测试UI元素已初始化"""
        panel = OCRPanel(mock_question_service)
        
        # 验证UI元素存在
        assert hasattr(panel, '_status_label')
        assert hasattr(panel, '_recognize_btn')
        assert panel._status_label is not None
        assert panel._recognize_btn is not None
        
        # 验证初始状态
        assert "等待图片" in panel._status_label.text()
        assert panel._recognize_btn.isEnabled() is False


class TestMockServiceIntegration:
    """测试mock OCR服务"""
    
    def test_accepts_mock_service(self, qapp, mock_question_service):
        """测试组件接受mock服务"""
        panel = OCRPanel(mock_question_service)
        assert panel._question_service == mock_question_service
    
    def test_service_not_created_internally(self, qapp, mock_question_service):
        """测试组件不在内部创建服务"""
        panel = OCRPanel(mock_question_service)
        # 验证使用的是传入的服务，而不是内部创建的
        assert panel._question_service is mock_question_service
    
    def test_handles_unavailable_ocr_engine(self, qapp, mock_unavailable_service, test_image_path):
        """测试处理OCR引擎不可用的情况"""
        panel = OCRPanel(mock_unavailable_service)
        
        # 记录信号
        failed_signals = []
        panel.recognition_failed.connect(lambda msg: failed_signals.append(msg))
        
        # 尝试识别
        panel.recognize_image(test_image_path)
        
        # 验证失败信号被发送
        assert len(failed_signals) > 0
        assert "不可用" in panel._status_label.text()
    
    def test_handles_no_ocr_engine(self, qapp, mock_no_ocr_service, test_image_path):
        """测试处理没有OCR引擎的情况"""
        panel = OCRPanel(mock_no_ocr_service)
        
        # 记录信号
        failed_signals = []
        panel.recognition_failed.connect(lambda msg: failed_signals.append(msg))
        
        # 尝试识别
        panel.recognize_image(test_image_path)
        
        # 验证失败信号被发送
        assert len(failed_signals) > 0
        assert "未启用" in panel._status_label.text()
    
    def test_mock_service_method_called(self, qapp, mock_question_service, test_image_path):
        """测试mock服务的方法被调用"""
        panel = OCRPanel(mock_question_service)
        
        # 创建并运行worker（模拟识别过程）
        worker = OCRWorker(mock_question_service, test_image_path)
        worker.run()
        
        # 验证服务方法被调用
        mock_question_service.recognize_image_with_retry.assert_called_once()
    
    def test_different_mock_services(self, qapp):
        """测试可以使用不同的mock服务"""
        service1 = Mock()
        service1.ocr_engine = Mock()
        service1.ocr_engine.is_available.return_value = True
        service1.ocr_engine._initialized = True
        
        service2 = Mock()
        service2.ocr_engine = Mock()
        service2.ocr_engine.is_available.return_value = False
        service2.ocr_engine._initialized = False
        
        panel1 = OCRPanel(service1)
        panel2 = OCRPanel(service2)
        
        assert panel1._question_service is service1
        assert panel2._question_service is service2
        assert panel1._question_service is not panel2._question_service


class TestSignalEmission:
    """测试信号发送"""
    
    def test_recognition_started_signal(self, qapp, mock_question_service):
        """测试recognition_started信号发送"""
        panel = OCRPanel(mock_question_service)
        
        # 记录信号
        started_signals = []
        panel.recognition_started.connect(lambda: started_signals.append(True))
        
        # Mock worker to prevent actual thread creation
        with patch.object(panel, '_worker', Mock()):
            # 直接发送信号
            panel.recognition_started.emit()
        
        # 验证信号被发送
        assert len(started_signals) == 1
    
    def test_recognition_completed_signal(self, qapp, mock_question_service, test_image_path):
        """测试recognition_completed信号发送"""
        panel = OCRPanel(mock_question_service)
        
        # 记录信号
        completed_signals = []
        panel.recognition_completed.connect(lambda text: completed_signals.append(text))
        
        # 模拟识别完成
        panel._on_recognition_finished(True, "成功", "识别的文本")
        
        # 验证信号被发送
        assert len(completed_signals) == 1
        assert completed_signals[0] == "识别的文本"
    
    def test_recognition_failed_signal(self, qapp, mock_question_service):
        """测试recognition_failed信号发送"""
        panel = OCRPanel(mock_question_service)
        
        # 记录信号
        failed_signals = []
        panel.recognition_failed.connect(lambda msg: failed_signals.append(msg))
        
        # 模拟识别失败
        panel._on_recognition_finished(False, "识别失败", "")
        
        # 验证信号被发送
        assert len(failed_signals) == 1
        assert failed_signals[0] == "识别失败"
    
    def test_signal_with_callback(self, qapp, mock_question_service):
        """测试信号回调功能"""
        panel = OCRPanel(mock_question_service)
        
        callback_data = []
        
        def on_completed(text):
            callback_data.append(("completed", text))
        
        def on_failed(msg):
            callback_data.append(("failed", msg))
        
        panel.recognition_completed.connect(on_completed)
        panel.recognition_failed.connect(on_failed)
        
        # 模拟成功
        panel._on_recognition_finished(True, "成功", "文本内容")
        assert len(callback_data) == 1
        assert callback_data[0] == ("completed", "文本内容")
        
        # 模拟失败
        callback_data.clear()
        panel._on_recognition_finished(False, "失败原因", "")
        assert len(callback_data) == 1
        assert callback_data[0] == ("failed", "失败原因")
    
    def test_multiple_signal_listeners(self, qapp, mock_question_service):
        """测试多个信号监听器"""
        panel = OCRPanel(mock_question_service)
        
        listener1_data = []
        listener2_data = []
        
        panel.recognition_completed.connect(lambda text: listener1_data.append(text))
        panel.recognition_completed.connect(lambda text: listener2_data.append(text))
        
        # 触发信号
        panel._on_recognition_finished(True, "成功", "测试文本")
        
        # 验证所有监听器都收到信号
        assert len(listener1_data) == 1
        assert len(listener2_data) == 1
        assert listener1_data[0] == "测试文本"
        assert listener2_data[0] == "测试文本"


class TestRecognitionFlow:
    """测试识别流程"""
    
    def test_recognize_image_sets_path(self, qapp, mock_question_service, test_image_path):
        """测试recognize_image设置图片路径"""
        panel = OCRPanel(mock_question_service)
        
        # Mock _do_recognition to prevent thread creation
        with patch.object(panel, '_do_recognition'):
            panel.recognize_image(test_image_path)
        
        assert panel._current_image_path == test_image_path
        assert panel._recognize_btn.isEnabled() is True
    
    def test_is_recognizing_flag(self, qapp, mock_question_service, test_image_path):
        """测试is_recognizing标志"""
        panel = OCRPanel(mock_question_service)
        
        # 初始状态
        assert panel.is_recognizing() is False
        
        # Mock worker to prevent thread creation
        with patch('mistake_book.ui.components.ocr_panel.OCRWorker'):
            panel._start_recognition()
            assert panel.is_recognizing() is True
        
        # 识别完成
        panel._on_recognition_finished(True, "成功", "文本")
        assert panel.is_recognizing() is False
    
    def test_set_status(self, qapp, mock_question_service):
        """测试设置状态文本"""
        panel = OCRPanel(mock_question_service)
        
        test_status = "测试状态"
        panel.set_status(test_status)
        
        assert panel._status_label.text() == test_status
    
    def test_button_state_during_recognition(self, qapp, mock_question_service, test_image_path):
        """测试识别过程中按钮状态"""
        panel = OCRPanel(mock_question_service)
        
        # Mock worker to prevent thread creation
        with patch('mistake_book.ui.components.ocr_panel.OCRWorker'):
            # 开始识别
            panel._start_recognition()
            
            # 按钮应该被禁用
            assert panel._recognize_btn.isEnabled() is False
            assert "识别中" in panel._recognize_btn.text()
        
        # 识别完成
        panel._on_recognition_finished(True, "成功", "文本")
        
        # 按钮应该被启用
        assert panel._recognize_btn.isEnabled() is True
    
    def test_status_updates_during_recognition(self, qapp, mock_question_service):
        """测试识别过程中状态更新"""
        panel = OCRPanel(mock_question_service)
        
        # Mock worker to prevent thread creation
        with patch('mistake_book.ui.components.ocr_panel.OCRWorker'):
            # 开始识别
            panel._start_recognition()
            assert "识别" in panel._status_label.text()
        
        # 识别成功
        panel._on_recognition_finished(True, "成功", "测试文本\n第二行")
        assert "✅" in panel._status_label.text()
        assert "2 行" in panel._status_label.text()
        
        # 识别失败
        panel._on_recognition_finished(False, "失败", "")
        assert "❌" in panel._status_label.text()


class TestOCRWorker:
    """测试OCR工作线程"""
    
    def test_worker_initialization(self, qapp, mock_question_service, test_image_path):
        """测试worker初始化"""
        worker = OCRWorker(mock_question_service, test_image_path)
        
        assert worker.question_service == mock_question_service
        assert worker.image_path == test_image_path
    
    def test_worker_run_success(self, qapp, mock_question_service, test_image_path):
        """测试worker成功执行"""
        mock_question_service.recognize_image_with_retry.return_value = (
            True, "识别成功", "识别的文本"
        )
        
        worker = OCRWorker(mock_question_service, test_image_path)
        
        # 记录信号
        finished_signals = []
        worker.finished.connect(lambda s, m, t: finished_signals.append((s, m, t)))
        
        # 运行worker
        worker.run()
        
        # 验证信号
        assert len(finished_signals) == 1
        success, message, text = finished_signals[0]
        assert success is True
        assert message == "识别成功"
        assert text == "识别的文本"
    
    def test_worker_run_failure(self, qapp, mock_question_service, test_image_path):
        """测试worker执行失败"""
        mock_question_service.recognize_image_with_retry.return_value = (
            False, "识别失败", None
        )
        
        worker = OCRWorker(mock_question_service, test_image_path)
        
        # 记录信号
        finished_signals = []
        worker.finished.connect(lambda s, m, t: finished_signals.append((s, m, t)))
        
        # 运行worker
        worker.run()
        
        # 验证信号
        assert len(finished_signals) == 1
        success, message, text = finished_signals[0]
        assert success is False
        assert message == "识别失败"
        assert text == ""
    
    def test_worker_exception_handling(self, qapp, mock_question_service, test_image_path):
        """测试worker异常处理"""
        mock_question_service.recognize_image_with_retry.side_effect = Exception("测试异常")
        
        worker = OCRWorker(mock_question_service, test_image_path)
        
        # 记录信号
        finished_signals = []
        worker.finished.connect(lambda s, m, t: finished_signals.append((s, m, t)))
        
        # 运行worker
        worker.run()
        
        # 验证信号
        assert len(finished_signals) == 1
        success, message, text = finished_signals[0]
        assert success is False
        assert "测试异常" in message
        assert text == ""


class TestEdgeCases:
    """测试边界情况"""
    
    def test_recognize_without_image(self, qapp, mock_question_service):
        """测试没有图片时识别"""
        panel = OCRPanel(mock_question_service)
        
        # 不设置图片直接识别
        panel._do_recognition()
        
        # 应该不会崩溃，且状态不变
        assert panel._is_recognizing is False
    
    def test_multiple_recognition_attempts(self, qapp, mock_question_service, test_image_path):
        """测试多次识别尝试"""
        panel = OCRPanel(mock_question_service)
        
        # Mock _do_recognition to prevent thread creation
        with patch.object(panel, '_do_recognition'):
            # 第一次识别
            panel.recognize_image(test_image_path)
            panel._on_recognition_finished(True, "成功", "文本1")
            
            # 第二次识别
            panel.recognize_image(test_image_path)
            panel._on_recognition_finished(True, "成功", "文本2")
        
        # 应该正常工作
        assert panel._current_image_path == test_image_path
        assert panel._is_recognizing is False
    
    def test_empty_recognition_result(self, qapp, mock_question_service):
        """测试空识别结果"""
        panel = OCRPanel(mock_question_service)
        
        # 记录信号
        failed_signals = []
        panel.recognition_failed.connect(lambda msg: failed_signals.append(msg))
        
        # 识别成功但文本为空
        panel._on_recognition_finished(True, "成功", "")
        
        # 应该视为失败
        assert len(failed_signals) > 0
    
    def test_recognition_with_multiline_text(self, qapp, mock_question_service):
        """测试多行文本识别"""
        panel = OCRPanel(mock_question_service)
        
        multiline_text = "第一行\n第二行\n第三行"
        
        # 记录信号
        completed_signals = []
        panel.recognition_completed.connect(lambda text: completed_signals.append(text))
        
        # 识别完成
        panel._on_recognition_finished(True, "成功", multiline_text)
        
        # 验证
        assert len(completed_signals) == 1
        assert completed_signals[0] == multiline_text
        assert "3 行" in panel._status_label.text()
    
    def test_button_click_without_image(self, qapp, mock_question_service):
        """测试没有图片时点击按钮"""
        panel = OCRPanel(mock_question_service)
        
        # 按钮应该是禁用的
        assert panel._recognize_btn.isEnabled() is False
        
        # 点击按钮（模拟）
        panel._on_recognize_clicked()
        
        # 不应该崩溃
        assert panel._is_recognizing is False


class TestUIBehavior:
    """测试UI行为"""
    
    def test_status_label_updates(self, qapp, mock_question_service):
        """测试状态标签更新"""
        panel = OCRPanel(mock_question_service)
        
        # 初始状态
        assert "等待" in panel._status_label.text()
        
        # 设置不同状态
        panel.set_status("测试状态1")
        assert panel._status_label.text() == "测试状态1"
        
        panel.set_status("测试状态2")
        assert panel._status_label.text() == "测试状态2"
    
    def test_button_text_updates(self, qapp, mock_question_service, test_image_path):
        """测试按钮文字更新"""
        panel = OCRPanel(mock_question_service)
        
        # 初始状态
        initial_text = panel._recognize_btn.text()
        
        # Mock _do_recognition to prevent thread creation
        with patch.object(panel, '_do_recognition'):
            # 设置图片
            panel.recognize_image(test_image_path)
            qapp.processEvents()
        
        # 按钮应该启用
        assert panel._recognize_btn.isEnabled() is True
    
    def test_ui_state_consistency(self, qapp, mock_question_service, test_image_path):
        """测试UI状态一致性"""
        panel = OCRPanel(mock_question_service)
        
        # Mock worker to prevent thread creation
        with patch('mistake_book.ui.components.ocr_panel.OCRWorker'):
            # Mock _do_recognition to prevent thread creation
            with patch.object(panel, '_do_recognition'):
                # 开始识别
                panel.recognize_image(test_image_path)
            
            panel._start_recognition()
            
            # 验证状态一致
            assert panel._is_recognizing is True
            assert panel._recognize_btn.isEnabled() is False
            assert "识别" in panel._status_label.text()
        
        # 识别完成
        panel._on_recognition_finished(True, "成功", "文本")
        
        # 验证状态一致
        assert panel._is_recognizing is False
        assert panel._recognize_btn.isEnabled() is True
        assert "✅" in panel._status_label.text()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
