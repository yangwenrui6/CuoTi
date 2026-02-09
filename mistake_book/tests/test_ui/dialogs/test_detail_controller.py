"""
DetailDialogController单元测试

测试要求:
- 测试使用mock服务
- 测试变化检测
- 测试保存逻辑
- 测试事件发布

**Validates: Requirements 3.1, 3.3**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.detail.controller import DetailDialogController
from mistake_book.ui.events.event_bus import EventBus
from mistake_book.ui.events.events import QuestionUpdatedEvent


class TestControllerInitialization:
    """测试控制器独立实例化"""
    
    def test_controller_can_be_instantiated_with_mock_service(self):
        """测试控制器可以使用mock服务实例化"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        assert controller is not None
        assert isinstance(controller, DetailDialogController)
        assert controller.question_service == mock_service
        assert controller.question_data == question_data
    
    def test_controller_without_event_bus(self):
        """测试控制器可以在没有事件总线的情况下实例化"""
        mock_service = Mock()
        question_data = {'id': 1, 'content': '题目'}
        
        controller = DetailDialogController(mock_service, question_data, event_bus=None)
        
        assert controller is not None
        assert controller.event_bus is None
    
    def test_controller_with_event_bus(self):
        """测试控制器可以接受事件总线"""
        mock_service = Mock()
        mock_event_bus = Mock()
        question_data = {'id': 1, 'content': '题目'}
        
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        assert controller is not None
        assert controller.event_bus == mock_event_bus
    
    def test_original_data_is_copied(self):
        """测试原始数据被复制而不是引用"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '原始内容',
            'my_answer': '原始答案'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        # 修改question_data不应影响original_data
        question_data['content'] = '修改后的内容'
        
        assert controller.original_data['content'] == '原始内容'
        assert controller.question_data['content'] == '修改后的内容'
    
    def test_multiple_controllers_independent(self):
        """测试多个控制器实例互不干扰"""
        mock_service1 = Mock()
        mock_service2 = Mock()
        
        data1 = {'id': 1, 'content': '题目1'}
        data2 = {'id': 2, 'content': '题目2'}
        
        controller1 = DetailDialogController(mock_service1, data1)
        controller2 = DetailDialogController(mock_service2, data2)
        
        assert controller1 is not controller2
        assert controller1.question_data is not controller2.question_data
        assert controller1.question_data['id'] == 1
        assert controller2.question_data['id'] == 2


class TestHasChanges:
    """测试变化检测功能"""
    
    def test_has_changes_no_changes(self):
        """测试没有修改时返回False"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        # 当前数据与原始数据相同
        current_data = {
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        assert controller.has_changes(current_data) is False
    
    def test_has_changes_content_modified(self):
        """测试题目内容修改时返回True"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '修改后的题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        assert controller.has_changes(current_data) is True
    
    def test_has_changes_my_answer_modified(self):
        """测试我的答案修改时返回True"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '原始答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '题目',
            'my_answer': '修改后的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        assert controller.has_changes(current_data) is True
    
    def test_has_changes_answer_modified(self):
        """测试正确答案修改时返回True"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '原始正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '修改后的正确答案',
            'explanation': '解析'
        }
        
        assert controller.has_changes(current_data) is True
    
    def test_has_changes_explanation_modified(self):
        """测试解析修改时返回True"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '题目',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '修改后的解析'
        }
        
        assert controller.has_changes(current_data) is True
    
    def test_has_changes_multiple_fields_modified(self):
        """测试多个字段修改时返回True"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始我的答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '修改后题目',
            'my_answer': '修改后我的答案',
            'answer': '修改后正确答案',
            'explanation': '修改后解析'
        }
        
        assert controller.has_changes(current_data) is True
    
    def test_has_changes_ignores_whitespace(self):
        """测试忽略首尾空白字符"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        # 添加首尾空白字符
        current_data = {
            'content': '  题目内容  ',
            'my_answer': '  我的答案  ',
            'answer': '  正确答案  ',
            'explanation': '  解析  '
        }
        
        # 应该被视为没有修改
        assert controller.has_changes(current_data) is False
    
    def test_has_changes_with_missing_fields(self):
        """测试缺少字段时的处理"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目',
            'my_answer': '我的答案'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        # 当前数据缺少某些字段
        current_data = {
            'content': '题目',
            'my_answer': '我的答案'
        }
        
        # 不应该抛出异常
        assert controller.has_changes(current_data) is False
    
    def test_has_changes_with_empty_strings(self):
        """测试空字符串的处理"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '',
            'my_answer': '',
            'answer': '',
            'explanation': ''
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '',
            'my_answer': '',
            'answer': '',
            'explanation': ''
        }
        
        assert controller.has_changes(current_data) is False


class TestSaveChangesSuccess:
    """测试保存成功场景"""
    
    def test_save_changes_calls_service(self):
        """测试保存时调用服务层"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {'id': 123, 'content': '原始内容'}
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {
            'content': '修改后的内容',
            'my_answer': '修改后的答案'
        }
        
        success, message = controller.save_changes(updates)
        
        # 验证服务被调用
        mock_service.update_question.assert_called_once_with(123, updates)
        assert success is True
        assert message == "更新成功"
    
    def test_save_changes_updates_original_data(self):
        """测试保存成功后更新原始数据"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {
            'id': 1,
            'content': '原始内容',
            'my_answer': '原始答案'
        }
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {
            'content': '新内容',
            'my_answer': '新答案'
        }
        
        success, message = controller.save_changes(updates)
        
        # 验证原始数据被更新
        assert controller.original_data['content'] == '新内容'
        assert controller.original_data['my_answer'] == '新答案'
    
    def test_save_changes_with_all_fields(self):
        """测试保存所有字段"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {'id': 456, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {
            'content': '新题目',
            'my_answer': '新我的答案',
            'answer': '新正确答案',
            'explanation': '新解析'
        }
        
        success, message = controller.save_changes(updates)
        
        mock_service.update_question.assert_called_once_with(456, updates)
        assert success is True



class TestSaveChangesFailure:
    """测试保存失败场景"""
    
    def test_save_changes_service_returns_false(self):
        """测试服务层返回失败"""
        mock_service = Mock()
        mock_service.update_question.return_value = (False, "更新失败：数据库错误")
        
        question_data = {'id': 1, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        assert success is False
        assert "更新失败" in message
    
    def test_save_changes_without_question_id(self):
        """测试没有题目ID时返回失败"""
        mock_service = Mock()
        question_data = {'content': '题目'}  # 缺少id字段
        
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        assert success is False
        assert "题目ID不存在" in message
        # 服务不应该被调用
        mock_service.update_question.assert_not_called()
    
    def test_save_changes_service_raises_exception(self):
        """测试服务层抛出异常"""
        mock_service = Mock()
        mock_service.update_question.side_effect = Exception("数据库连接失败")
        
        question_data = {'id': 1, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        assert success is False
        assert "保存失败" in message
        assert "数据库连接失败" in message
    
    def test_save_changes_does_not_update_original_on_failure(self):
        """测试保存失败时不更新原始数据"""
        mock_service = Mock()
        mock_service.update_question.return_value = (False, "更新失败")
        
        question_data = {
            'id': 1,
            'content': '原始内容',
            'my_answer': '原始答案'
        }
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {
            'content': '新内容',
            'my_answer': '新答案'
        }
        
        success, message = controller.save_changes(updates)
        
        # 验证原始数据未被修改
        assert controller.original_data['content'] == '原始内容'
        assert controller.original_data['my_answer'] == '原始答案'


class TestEventPublishing:
    """测试事件发布"""
    
    def test_save_changes_publishes_event_on_success(self):
        """测试保存成功时发布事件"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        mock_event_bus = Mock()
        question_data = {'id': 123, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        updates = {
            'content': '新内容',
            'my_answer': '新答案'
        }
        
        success, message = controller.save_changes(updates)
        
        # 验证事件被发布
        assert mock_event_bus.publish.called
        
        # 获取发布的事件
        call_args = mock_event_bus.publish.call_args
        published_event = call_args[0][0]
        
        # 验证事件类型和内容
        assert isinstance(published_event, QuestionUpdatedEvent)
        assert published_event.question_id == 123
        assert published_event.updates == updates
    
    def test_save_changes_does_not_publish_event_on_failure(self):
        """测试保存失败时不发布事件"""
        mock_service = Mock()
        mock_service.update_question.return_value = (False, "更新失败")
        
        mock_event_bus = Mock()
        question_data = {'id': 1, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        # 验证事件未被发布
        mock_event_bus.publish.assert_not_called()
    
    def test_save_changes_without_event_bus(self):
        """测试没有事件总线时不会出错"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {'id': 1, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=None)
        
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        # 应该成功，不会因为没有事件总线而失败
        assert success is True
    
    def test_save_changes_event_contains_correct_data(self):
        """测试发布的事件包含正确的数据"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        mock_event_bus = Mock()
        question_data = {'id': 999, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        updates = {
            'content': '详细题目内容',
            'my_answer': '我的详细答案',
            'answer': '正确的详细答案',
            'explanation': '详细解析说明'
        }
        
        controller.save_changes(updates)
        
        # 获取发布的事件
        published_event = mock_event_bus.publish.call_args[0][0]
        
        # 验证所有字段都正确传递
        assert published_event.question_id == 999
        assert published_event.updates['content'] == '详细题目内容'
        assert published_event.updates['my_answer'] == '我的详细答案'
        assert published_event.updates['answer'] == '正确的详细答案'
        assert published_event.updates['explanation'] == '详细解析说明'


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
    
    def test_save_changes_with_real_event_bus(self):
        """测试使用真实事件总线"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        event_bus = EventBus()
        question_data = {'id': 123, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=event_bus)
        
        # 订阅事件
        received_events = []
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe(QuestionUpdatedEvent, event_handler)
        
        # 保存修改
        updates = {'content': '新内容'}
        success, message = controller.save_changes(updates)
        
        # 验证事件被接收
        assert len(received_events) == 1
        assert isinstance(received_events[0], QuestionUpdatedEvent)
        assert received_events[0].question_id == 123
        assert received_events[0].updates == updates
    
    def test_multiple_subscribers_receive_event(self):
        """测试多个订阅者都能接收事件"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        event_bus = EventBus()
        question_data = {'id': 456, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data, event_bus=event_bus)
        
        # 多个订阅者
        received_events_1 = []
        received_events_2 = []
        received_events_3 = []
        
        event_bus.subscribe(QuestionUpdatedEvent, lambda e: received_events_1.append(e))
        event_bus.subscribe(QuestionUpdatedEvent, lambda e: received_events_2.append(e))
        event_bus.subscribe(QuestionUpdatedEvent, lambda e: received_events_3.append(e))
        
        # 保存修改
        updates = {'content': '新内容'}
        controller.save_changes(updates)
        
        # 验证所有订阅者都收到事件
        assert len(received_events_1) == 1
        assert len(received_events_2) == 1
        assert len(received_events_3) == 1


class TestControllerIntegration:
    """测试控制器集成场景"""
    
    def test_complete_workflow_check_and_save(self):
        """测试完整工作流：检查变化 -> 保存"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        mock_event_bus = Mock()
        question_data = {
            'id': 123,
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        # 1. 检查是否有变化（没有变化）
        current_data = {
            'content': '原始题目',
            'my_answer': '原始答案',
            'answer': '原始正确答案',
            'explanation': '原始解析'
        }
        assert controller.has_changes(current_data) is False
        
        # 2. 修改数据
        modified_data = {
            'content': '修改后的题目',
            'my_answer': '修改后的答案',
            'answer': '修改后的正确答案',
            'explanation': '修改后的解析'
        }
        
        # 3. 检查是否有变化（有变化）
        assert controller.has_changes(modified_data) is True
        
        # 4. 保存修改
        success, message = controller.save_changes(modified_data)
        
        # 验证整个流程
        assert success is True
        mock_service.update_question.assert_called_once()
        mock_event_bus.publish.assert_called_once()
        
        # 5. 再次检查变化（保存后应该没有变化）
        assert controller.has_changes(modified_data) is False
    
    def test_workflow_with_multiple_saves(self):
        """测试多次保存"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        mock_event_bus = Mock()
        question_data = {'id': 1, 'content': '原始内容'}
        controller = DetailDialogController(mock_service, question_data, event_bus=mock_event_bus)
        
        # 第一次保存
        updates1 = {'content': '第一次修改'}
        success1, _ = controller.save_changes(updates1)
        assert success1 is True
        
        # 第二次保存
        updates2 = {'content': '第二次修改'}
        success2, _ = controller.save_changes(updates2)
        assert success2 is True
        
        # 第三次保存
        updates3 = {'content': '第三次修改'}
        success3, _ = controller.save_changes(updates3)
        assert success3 is True
        
        # 验证服务被调用3次
        assert mock_service.update_question.call_count == 3
        
        # 验证事件被发布3次
        assert mock_event_bus.publish.call_count == 3


class TestEdgeCases:
    """测试边界情况"""
    
    def test_has_changes_with_none_values(self):
        """测试None值的处理"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': None,
            'my_answer': None
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': None,
            'my_answer': None
        }
        
        # 不应该抛出异常
        assert controller.has_changes(current_data) is False
    
    def test_save_changes_with_empty_updates(self):
        """测试保存空更新"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        question_data = {'id': 1, 'content': '题目'}
        controller = DetailDialogController(mock_service, question_data)
        
        updates = {}
        success, message = controller.save_changes(updates)
        
        # 应该正常处理
        assert success is True
        mock_service.update_question.assert_called_once_with(1, {})
    
    def test_controller_with_minimal_question_data(self):
        """测试最小化的题目数据"""
        mock_service = Mock()
        question_data = {'id': 1}
        
        controller = DetailDialogController(mock_service, question_data)
        
        assert controller is not None
        assert controller.question_data['id'] == 1
    
    def test_has_changes_with_unicode_characters(self):
        """测试Unicode字符的处理"""
        mock_service = Mock()
        question_data = {
            'id': 1,
            'content': '题目包含emoji 😀 和特殊字符 ©®™',
            'my_answer': '答案包含中文、English、日本語'
        }
        
        controller = DetailDialogController(mock_service, question_data)
        
        current_data = {
            'content': '题目包含emoji 😀 和特殊字符 ©®™',
            'my_answer': '答案包含中文、English、日本語'
        }
        
        assert controller.has_changes(current_data) is False


class TestControllerIsolation:
    """测试控制器隔离性"""
    
    def test_controller_does_not_modify_input_data(self):
        """测试控制器不修改输入数据"""
        mock_service = Mock()
        mock_service.update_question.return_value = (True, "更新成功")
        
        original_question_data = {
            'id': 1,
            'content': '原始题目',
            'my_answer': '原始答案'
        }
        
        # 复制一份用于比较
        data_copy = original_question_data.copy()
        
        controller = DetailDialogController(mock_service, original_question_data)
        
        updates = {'content': '新题目'}
        controller.save_changes(updates)
        
        # 验证输入的question_data未被修改（除了通过save_changes更新的字段）
        assert original_question_data['id'] == data_copy['id']
    
    def test_controller_does_not_share_state(self):
        """测试控制器不共享状态"""
        mock_service = Mock()
        
        data1 = {'id': 1, 'content': '题目1'}
        data2 = {'id': 2, 'content': '题目2'}
        
        controller1 = DetailDialogController(mock_service, data1)
        controller2 = DetailDialogController(mock_service, data2)
        
        # 修改controller1的原始数据
        controller1.original_data['content'] = '修改后的题目1'
        
        # controller2的状态应该不受影响
        assert controller2.original_data['content'] == '题目2'
    
    def test_controller_with_different_services(self):
        """测试使用不同服务的控制器"""
        mock_service1 = Mock()
        mock_service1.update_question.return_value = (True, "服务1更新成功")
        
        mock_service2 = Mock()
        mock_service2.update_question.return_value = (True, "服务2更新成功")
        
        data1 = {'id': 1, 'content': '题目1'}
        data2 = {'id': 2, 'content': '题目2'}
        
        controller1 = DetailDialogController(mock_service1, data1)
        controller2 = DetailDialogController(mock_service2, data2)
        
        updates = {'content': '新内容'}
        
        # 调用不同的控制器
        success1, message1 = controller1.save_changes(updates)
        success2, message2 = controller2.save_changes(updates)
        
        # 验证调用了正确的服务
        assert message1 == "服务1更新成功"
        assert message2 == "服务2更新成功"
        mock_service1.update_question.assert_called_once()
        mock_service2.update_question.assert_called_once()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
