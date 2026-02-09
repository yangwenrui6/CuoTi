"""
AddQuestionController单元测试

测试要求:
- **Property 10: Controller可独立测试**
- **Validates: Requirements 3.1, 3.3**
- 测试使用mock服务
- 测试保存逻辑
- 测试事件发布

**Validates: Requirements 3.1, 3.3**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.add_question.controller import AddQuestionController
from mistake_book.ui.events.event_bus import EventBus
from mistake_book.ui.events.events import QuestionAddedEvent


class TestControllerInitialization:
    """测试控制器独立实例化"""
    
    def test_controller_can_be_instantiated_with_mock_service(self):
        """
        测试控制器可以使用mock服务实例化
        Property 10: Controller可独立测试
        """
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        assert controller is not None
        assert isinstance(controller, AddQuestionController)
        assert controller.question_service == mock_service
    
    def test_controller_without_event_bus(self):
        """测试控制器可以在没有事件总线的情况下实例化"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service, event_bus=None)
        
        assert controller is not None
        assert controller.event_bus is None
    
    def test_controller_with_event_bus(self):
        """测试控制器可以接受事件总线"""
        mock_service = Mock()
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        assert controller is not None
        assert controller.event_bus == mock_event_bus
    
    def test_initial_state(self):
        """测试初始状态"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        assert controller._current_image_path is None
    
    def test_multiple_controllers_independent(self):
        """测试多个控制器实例互不干扰"""
        mock_service1 = Mock()
        mock_service2 = Mock()
        
        controller1 = AddQuestionController(mock_service1)
        controller2 = AddQuestionController(mock_service2)
        
        assert controller1 is not controller2
        assert controller1.question_service is not controller2.question_service
        
        # 修改controller1不应影响controller2
        controller1.on_image_selected("path1.png")
        assert controller1._current_image_path == "path1.png"
        assert controller2._current_image_path is None


class TestImageSelectedHandler:
    """测试图片选择事件处理"""
    
    def test_on_image_selected_stores_path(self):
        """测试图片选择时存储路径"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        test_path = "/path/to/image.png"
        controller.on_image_selected(test_path)
        
        assert controller._current_image_path == test_path
    
    def test_on_image_selected_updates_path(self):
        """测试图片选择时更新路径"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        # 第一次选择
        controller.on_image_selected("path1.png")
        assert controller._current_image_path == "path1.png"
        
        # 第二次选择应该更新
        controller.on_image_selected("path2.png")
        assert controller._current_image_path == "path2.png"
    
    def test_on_image_selected_with_chinese_path(self):
        """测试中文路径"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        chinese_path = "/路径/到/图片.png"
        controller.on_image_selected(chinese_path)
        
        assert controller._current_image_path == chinese_path
    
    def test_on_image_selected_with_empty_string(self):
        """测试空字符串路径"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        controller.on_image_selected("")
        assert controller._current_image_path == ""


class TestOCRCompletedHandler:
    """测试OCR识别完成事件处理"""
    
    def test_on_ocr_completed_returns_text(self):
        """测试OCR完成时返回文本"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        test_text = "识别的文本内容"
        result = controller.on_ocr_completed(test_text)
        
        assert result == test_text
    
    def test_on_ocr_completed_with_empty_text(self):
        """测试空文本"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        result = controller.on_ocr_completed("")
        assert result == ""
    
    def test_on_ocr_completed_with_multiline_text(self):
        """测试多行文本"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        multiline_text = "第一行\n第二行\n第三行"
        result = controller.on_ocr_completed(multiline_text)
        
        assert result == multiline_text
    
    def test_on_ocr_completed_with_chinese_text(self):
        """测试中文文本"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        chinese_text = "这是中文识别结果，包含标点符号。"
        result = controller.on_ocr_completed(chinese_text)
        
        assert result == chinese_text


class TestSaveQuestionSuccess:
    """测试保存成功场景"""
    
    def test_save_question_calls_service(self):
        """测试保存时调用服务层"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        controller = AddQuestionController(mock_service)
        
        test_data = {
            'subject': '数学',
            'content': '测试题目',
            'answer': '测试答案'
        }
        
        success, message = controller.save_question(test_data)
        
        # 验证服务被调用
        mock_service.create_question.assert_called_once_with(test_data)
        assert success is True
        assert message == "保存成功"
    
    def test_save_question_with_complete_data(self):
        """测试保存完整数据"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 456)
        
        controller = AddQuestionController(mock_service)
        
        complete_data = {
            'subject': '物理',
            'question_type': '计算题',
            'content': '完整的题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '详细解析',
            'difficulty': 4,
            'image_path': '/path/to/image.png'
        }
        
        success, message = controller.save_question(complete_data)
        
        mock_service.create_question.assert_called_once_with(complete_data)
        assert success is True
    
    def test_save_question_returns_correct_values(self):
        """测试保存返回正确的值"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "创建成功", 789)
        
        controller = AddQuestionController(mock_service)
        
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        assert success is True
        assert message == "创建成功"
        assert isinstance(success, bool)
        assert isinstance(message, str)


class TestSaveQuestionFailure:
    """测试保存失败场景"""
    
    def test_save_question_service_returns_false(self):
        """测试服务层返回失败"""
        mock_service = Mock()
        mock_service.create_question.return_value = (False, "保存失败：数据库错误", None)
        
        controller = AddQuestionController(mock_service)
        
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        assert success is False
        assert "保存失败" in message
    
    def test_save_question_service_raises_exception(self):
        """测试服务层抛出异常"""
        mock_service = Mock()
        mock_service.create_question.side_effect = Exception("数据库连接失败")
        
        controller = AddQuestionController(mock_service)
        
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        assert success is False
        assert "保存失败" in message
        assert "数据库连接失败" in message
    
    def test_save_question_handles_various_exceptions(self):
        """测试处理各种异常"""
        exceptions = [
            ValueError("无效的数据"),
            KeyError("缺少必需字段"),
            RuntimeError("运行时错误"),
            Exception("通用异常")
        ]
        
        for exception in exceptions:
            mock_service = Mock()
            mock_service.create_question.side_effect = exception
            
            controller = AddQuestionController(mock_service)
            
            test_data = {'content': '题目', 'answer': '答案'}
            success, message = controller.save_question(test_data)
            
            assert success is False
            assert "保存失败" in message


class TestEventPublishing:
    """测试事件发布"""
    
    def test_save_question_publishes_event_on_success(self):
        """测试保存成功时发布事件"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        test_data = {
            'subject': '数学',
            'content': '题目',
            'answer': '答案'
        }
        
        success, message = controller.save_question(test_data)
        
        # 验证事件被发布
        assert mock_event_bus.publish.called
        
        # 获取发布的事件
        call_args = mock_event_bus.publish.call_args
        published_event = call_args[0][0]
        
        # 验证事件类型和内容
        assert isinstance(published_event, QuestionAddedEvent)
        assert published_event.question_id == 123
        assert published_event.question_data == test_data
    
    def test_save_question_does_not_publish_event_on_failure(self):
        """测试保存失败时不发布事件"""
        mock_service = Mock()
        mock_service.create_question.return_value = (False, "保存失败", None)
        
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        # 验证事件未被发布
        mock_event_bus.publish.assert_not_called()
    
    def test_save_question_without_event_bus(self):
        """测试没有事件总线时不会出错"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        controller = AddQuestionController(mock_service, event_bus=None)
        
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        # 应该成功，不会因为没有事件总线而失败
        assert success is True
    
    def test_save_question_event_contains_correct_data(self):
        """测试发布的事件包含正确的数据"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 999)
        
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        test_data = {
            'subject': '化学',
            'question_type': '简答题',
            'content': '详细题目内容',
            'my_answer': '我的详细答案',
            'answer': '正确的详细答案',
            'explanation': '详细解析说明',
            'difficulty': 5
        }
        
        controller.save_question(test_data)
        
        # 获取发布的事件
        published_event = mock_event_bus.publish.call_args[0][0]
        
        # 验证所有字段都正确传递
        assert published_event.question_id == 999
        assert published_event.question_data['subject'] == '化学'
        assert published_event.question_data['question_type'] == '简答题'
        assert published_event.question_data['content'] == '详细题目内容'
        assert published_event.question_data['my_answer'] == '我的详细答案'
        assert published_event.question_data['answer'] == '正确的详细答案'
        assert published_event.question_data['explanation'] == '详细解析说明'
        assert published_event.question_data['difficulty'] == 5


class TestControllerIntegration:
    """测试控制器集成场景"""
    
    def test_complete_workflow_with_image_and_ocr(self):
        """测试完整工作流：选择图片 -> OCR识别 -> 保存"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        # 1. 选择图片
        image_path = "/path/to/question.png"
        controller.on_image_selected(image_path)
        assert controller._current_image_path == image_path
        
        # 2. OCR识别
        ocr_text = "识别出的题目内容"
        result_text = controller.on_ocr_completed(ocr_text)
        assert result_text == ocr_text
        
        # 3. 保存题目
        question_data = {
            'subject': '数学',
            'content': ocr_text,
            'answer': '答案',
            'image_path': image_path
        }
        success, message = controller.save_question(question_data)
        
        # 验证整个流程
        assert success is True
        mock_service.create_question.assert_called_once()
        mock_event_bus.publish.assert_called_once()
    
    def test_workflow_without_image(self):
        """测试没有图片的工作流"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 456)
        
        controller = AddQuestionController(mock_service)
        
        # 直接保存，不选择图片
        question_data = {
            'subject': '英语',
            'content': '手动输入的题目',
            'answer': '答案'
        }
        success, message = controller.save_question(question_data)
        
        assert success is True
        assert controller._current_image_path is None
    
    def test_workflow_with_multiple_saves(self):
        """测试多次保存"""
        mock_service = Mock()
        mock_service.create_question.side_effect = [
            (True, "保存成功", 1),
            (True, "保存成功", 2),
            (True, "保存成功", 3)
        ]
        
        mock_event_bus = Mock()
        controller = AddQuestionController(mock_service, event_bus=mock_event_bus)
        
        # 保存三次
        for i in range(3):
            data = {'content': f'题目{i+1}', 'answer': f'答案{i+1}'}
            success, message = controller.save_question(data)
            assert success is True
        
        # 验证服务被调用3次
        assert mock_service.create_question.call_count == 3
        
        # 验证事件被发布3次
        assert mock_event_bus.publish.call_count == 3


class TestControllerWithRealEventBus:
    """测试控制器与真实事件总线的集成"""
    
    def setup_method(self):
        """每个测试前清空事件总线"""
        event_bus = EventBus()
        event_bus.clear()
    
    def teardown_method(self):
        """每个测试后清空事件总线"""
        event_bus = EventBus()
        event_bus.clear()
    
    def test_save_question_with_real_event_bus(self):
        """测试使用真实事件总线"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        event_bus = EventBus()
        controller = AddQuestionController(mock_service, event_bus=event_bus)
        
        # 订阅事件
        received_events = []
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe(QuestionAddedEvent, event_handler)
        
        # 保存题目
        test_data = {'content': '题目', 'answer': '答案'}
        success, message = controller.save_question(test_data)
        
        # 验证事件被接收
        assert len(received_events) == 1
        assert isinstance(received_events[0], QuestionAddedEvent)
        assert received_events[0].question_id == 123
        assert received_events[0].question_data == test_data
    
    def test_multiple_subscribers_receive_event(self):
        """测试多个订阅者都能接收事件"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 456)
        
        event_bus = EventBus()
        controller = AddQuestionController(mock_service, event_bus=event_bus)
        
        # 多个订阅者
        received_events_1 = []
        received_events_2 = []
        received_events_3 = []
        
        event_bus.subscribe(QuestionAddedEvent, lambda e: received_events_1.append(e))
        event_bus.subscribe(QuestionAddedEvent, lambda e: received_events_2.append(e))
        event_bus.subscribe(QuestionAddedEvent, lambda e: received_events_3.append(e))
        
        # 保存题目
        test_data = {'content': '题目', 'answer': '答案'}
        controller.save_question(test_data)
        
        # 验证所有订阅者都收到事件
        assert len(received_events_1) == 1
        assert len(received_events_2) == 1
        assert len(received_events_3) == 1


class TestEdgeCases:
    """测试边界情况"""
    
    def test_save_question_with_none_data(self):
        """测试保存None数据"""
        mock_service = Mock()
        mock_service.create_question.side_effect = TypeError("参数错误")
        
        controller = AddQuestionController(mock_service)
        
        success, message = controller.save_question(None)
        
        assert success is False
        assert "保存失败" in message
    
    def test_save_question_with_empty_dict(self):
        """测试保存空字典"""
        mock_service = Mock()
        mock_service.create_question.return_value = (False, "数据不完整", None)
        
        controller = AddQuestionController(mock_service)
        
        success, message = controller.save_question({})
        
        assert success is False
    
    def test_on_image_selected_with_none(self):
        """测试选择None路径"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        # 不应该抛出异常
        controller.on_image_selected(None)
        assert controller._current_image_path is None
    
    def test_on_ocr_completed_with_none(self):
        """测试OCR返回None"""
        mock_service = Mock()
        controller = AddQuestionController(mock_service)
        
        # 不应该抛出异常
        result = controller.on_ocr_completed(None)
        assert result is None
    
    def test_service_returns_unexpected_format(self):
        """测试服务返回意外格式"""
        mock_service = Mock()
        # 返回格式不正确（缺少question_id）
        mock_service.create_question.return_value = (True, "保存成功")
        
        controller = AddQuestionController(mock_service)
        
        test_data = {'content': '题目', 'answer': '答案'}
        
        # 应该捕获异常并返回失败
        success, message = controller.save_question(test_data)
        
        assert success is False
        assert "保存失败" in message


class TestControllerIsolation:
    """测试控制器隔离性"""
    
    def test_controller_does_not_modify_input_data(self):
        """测试控制器不修改输入数据"""
        mock_service = Mock()
        mock_service.create_question.return_value = (True, "保存成功", 123)
        
        controller = AddQuestionController(mock_service)
        
        original_data = {
            'subject': '数学',
            'content': '题目',
            'answer': '答案'
        }
        
        # 复制一份用于比较
        data_copy = original_data.copy()
        
        controller.save_question(original_data)
        
        # 验证原始数据未被修改
        assert original_data == data_copy
    
    def test_controller_does_not_share_state(self):
        """测试控制器不共享状态"""
        mock_service = Mock()
        
        controller1 = AddQuestionController(mock_service)
        controller2 = AddQuestionController(mock_service)
        
        # 修改controller1的状态
        controller1.on_image_selected("path1.png")
        controller1._current_image_path = "modified_path"
        
        # controller2的状态应该不受影响
        assert controller2._current_image_path is None
    
    def test_controller_with_different_services(self):
        """测试使用不同服务的控制器"""
        mock_service1 = Mock()
        mock_service1.create_question.return_value = (True, "服务1成功", 1)
        
        mock_service2 = Mock()
        mock_service2.create_question.return_value = (True, "服务2成功", 2)
        
        controller1 = AddQuestionController(mock_service1)
        controller2 = AddQuestionController(mock_service2)
        
        test_data = {'content': '题目', 'answer': '答案'}
        
        # 调用不同的控制器
        success1, message1 = controller1.save_question(test_data)
        success2, message2 = controller2.save_question(test_data)
        
        # 验证调用了正确的服务
        assert message1 == "服务1成功"
        assert message2 == "服务2成功"
        mock_service1.create_question.assert_called_once()
        mock_service2.create_question.assert_called_once()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
