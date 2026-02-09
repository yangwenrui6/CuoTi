"""ReviewDialogController单元测试"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.dialogs.review.controller import ReviewDialogController
from mistake_book.config.constants import ReviewResult
from mistake_book.ui.events.events import ReviewCompletedEvent


class TestReviewDialogController:
    """ReviewDialogController测试类"""
    
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
            {'id': 1, 'content': '题目1', 'answer': '答案1'},
            {'id': 2, 'content': '题目2', 'answer': '答案2'},
            {'id': 3, 'content': '题目3', 'answer': '答案3'}
        ]
    
    @pytest.fixture
    def mock_event_bus(self):
        """创建mock EventBus"""
        bus = Mock()
        return bus
    
    def test_controller_initialization(self, mock_review_service, sample_questions):
        """测试控制器初始化"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        assert controller.review_service == mock_review_service
        assert controller.questions == sample_questions
        assert controller.current_index == 0
        assert controller.reviewed_count == 0
    
    def test_get_current_question_first(self, mock_review_service, sample_questions):
        """测试获取第一道题目"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        question = controller.get_current_question()
        
        assert question is not None
        assert question['id'] == 1
        assert question['content'] == '题目1'
    
    def test_get_current_question_none_when_finished(self, mock_review_service, sample_questions):
        """测试完成所有题目后返回None"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 移动到最后
        controller.current_index = len(sample_questions)
        
        question = controller.get_current_question()
        assert question is None
    
    def test_submit_review_success(self, mock_review_service, sample_questions):
        """测试提交复习结果成功"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 提交第一题
        has_next = controller.submit_review(quality=ReviewResult.GOOD.value)
        
        assert has_next is True
        assert controller.reviewed_count == 1
        assert controller.current_index == 1
        
        # 验证调用了服务
        mock_review_service.process_review_result.assert_called_once_with(
            1, ReviewResult.GOOD
        )
    
    def test_submit_review_last_question(self, mock_review_service, sample_questions):
        """测试提交最后一题"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 移动到最后一题
        controller.current_index = 2
        
        has_next = controller.submit_review(quality=ReviewResult.EASY.value)
        
        assert has_next is False
        assert controller.reviewed_count == 1
        assert controller.current_index == 3
    
    def test_submit_review_publishes_event_when_complete(
        self, mock_review_service, sample_questions, mock_event_bus
    ):
        """测试完成所有题目时发布事件"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions,
            mock_event_bus
        )
        
        # 复习所有题目
        controller.submit_review(quality=ReviewResult.GOOD.value)
        controller.submit_review(quality=ReviewResult.GOOD.value)
        controller.submit_review(quality=ReviewResult.GOOD.value)
        
        # 验证发布了事件
        assert mock_event_bus.publish.called
        
        # 获取发布的事件
        call_args = mock_event_bus.publish.call_args
        event = call_args[0][0]
        
        assert isinstance(event, ReviewCompletedEvent)
        assert event.reviewed_count == 3
    
    def test_submit_review_no_event_when_not_complete(
        self, mock_review_service, sample_questions, mock_event_bus
    ):
        """测试未完成时不发布事件"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions,
            mock_event_bus
        )
        
        # 只复习一题
        controller.submit_review(quality=ReviewResult.GOOD.value)
        
        # 不应该发布事件
        mock_event_bus.publish.assert_not_called()
    
    def test_submit_review_invalid_quality(self, mock_review_service, sample_questions):
        """测试提交无效的质量评分"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 提交无效评分
        has_next = controller.submit_review(quality=99)
        
        assert has_next is False
        # 不应该调用服务
        mock_review_service.process_review_result.assert_not_called()
    
    def test_submit_review_no_current_question(self, mock_review_service, sample_questions):
        """测试没有当前题目时提交"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 移动到超出范围
        controller.current_index = 10
        
        has_next = controller.submit_review(quality=ReviewResult.GOOD.value)
        
        assert has_next is False
        mock_review_service.process_review_result.assert_not_called()
    
    def test_submit_review_service_failure(self, mock_review_service, sample_questions):
        """测试服务层失败时仍然继续"""
        # 模拟服务失败
        mock_review_service.process_review_result.return_value = (False, "失败", {})
        
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 提交复习
        has_next = controller.submit_review(quality=ReviewResult.GOOD.value)
        
        # 即使失败也应该继续
        assert has_next is True
        assert controller.reviewed_count == 1
        assert controller.current_index == 1
    
    def test_get_progress_first_question(self, mock_review_service, sample_questions):
        """测试获取第一题的进度"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        current, total = controller.get_progress()
        
        assert current == 1
        assert total == 3
    
    def test_get_progress_middle_question(self, mock_review_service, sample_questions):
        """测试获取中间题目的进度"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        controller.current_index = 1
        current, total = controller.get_progress()
        
        assert current == 2
        assert total == 3
    
    def test_get_progress_after_completion(self, mock_review_service, sample_questions):
        """测试完成后的进度"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        controller.current_index = 3
        current, total = controller.get_progress()
        
        assert current == 4
        assert total == 3
    
    def test_get_reviewed_count(self, mock_review_service, sample_questions):
        """测试获取已复习数量"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        assert controller.get_reviewed_count() == 0
        
        controller.submit_review(quality=ReviewResult.GOOD.value)
        assert controller.get_reviewed_count() == 1
        
        controller.submit_review(quality=ReviewResult.GOOD.value)
        assert controller.get_reviewed_count() == 2
    
    def test_has_more_questions_true(self, mock_review_service, sample_questions):
        """测试还有更多题目"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        assert controller.has_more_questions() is True
        
        controller.submit_review(quality=ReviewResult.GOOD.value)
        assert controller.has_more_questions() is True
    
    def test_has_more_questions_false(self, mock_review_service, sample_questions):
        """测试没有更多题目"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 复习所有题目
        controller.submit_review(quality=ReviewResult.GOOD.value)
        controller.submit_review(quality=ReviewResult.GOOD.value)
        controller.submit_review(quality=ReviewResult.GOOD.value)
        
        assert controller.has_more_questions() is False
    
    def test_reset(self, mock_review_service, sample_questions):
        """测试重置控制器"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 复习几题
        controller.submit_review(quality=ReviewResult.GOOD.value)
        controller.submit_review(quality=ReviewResult.GOOD.value)
        
        assert controller.current_index == 2
        assert controller.reviewed_count == 2
        
        # 重置
        controller.reset()
        
        assert controller.current_index == 0
        assert controller.reviewed_count == 0
    
    def test_controller_with_empty_questions(self, mock_review_service):
        """测试空题目列表"""
        controller = ReviewDialogController(
            mock_review_service,
            []
        )
        
        assert controller.get_current_question() is None
        assert controller.has_more_questions() is False
        
        current, total = controller.get_progress()
        assert current == 1
        assert total == 0
    
    def test_controller_can_use_mock_service(self):
        """
        Property 10: Controller可独立测试
        Validates: Requirements 3.1, 3.3
        
        测试控制器可以使用mock服务独立测试
        """
        mock_service = Mock()
        mock_service.process_review_result.return_value = (True, "成功", {})
        
        questions = [{'id': 1, 'content': '测试'}]
        controller = ReviewDialogController(mock_service, questions)
        
        # 验证可以正常工作
        assert controller.review_service == mock_service
        question = controller.get_current_question()
        assert question is not None
        
        # 提交复习
        controller.submit_review(quality=ReviewResult.GOOD.value)
        
        # 验证调用了mock服务
        mock_service.process_review_result.assert_called_once()
    
    def test_multiple_quality_levels(self, mock_review_service, sample_questions):
        """测试不同的质量评分"""
        controller = ReviewDialogController(
            mock_review_service,
            sample_questions
        )
        
        # 测试所有质量级别
        quality_levels = [
            ReviewResult.AGAIN.value,
            ReviewResult.HARD.value,
            ReviewResult.GOOD.value
        ]
        
        for quality in quality_levels:
            controller.submit_review(quality=quality)
        
        # 验证所有调用
        assert mock_review_service.process_review_result.call_count == 3
        
        # 验证调用参数
        calls = mock_review_service.process_review_result.call_args_list
        assert calls[0][0][1] == ReviewResult.AGAIN
        assert calls[1][0][1] == ReviewResult.HARD
        assert calls[2][0][1] == ReviewResult.GOOD
