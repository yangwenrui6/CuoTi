"""
QuestionForm组件单元测试

测试要求:
- **Property 12: QuestionForm数据往返一致性**
- **Validates: Requirements 2.3**
- 测试 set_data() 后 get_data() 返回相同数据
- 测试表单验证逻辑

**Validates: Requirements 3.1**
"""

import sys
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.components.question_form import QuestionForm


# 创建QApplication实例（PyQt测试需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestQuestionFormInitialization:
    """测试组件独立实例化"""
    
    def test_component_can_be_instantiated(self, qapp):
        """测试组件可以独立实例化"""
        form = QuestionForm()
        assert form is not None
        assert isinstance(form, QuestionForm)
    
    def test_initial_state(self, qapp):
        """测试初始状态"""
        form = QuestionForm()
        data = form.get_data()
        
        # 验证初始数据结构
        assert 'subject' in data
        assert 'question_type' in data
        assert 'content' in data
        assert 'my_answer' in data
        assert 'answer' in data
        assert 'explanation' in data
        assert 'difficulty' in data
        
        # 验证初始值
        assert data['content'] == ''
        assert data['my_answer'] == ''
        assert data['answer'] == ''
        assert data['explanation'] == ''
        assert data['difficulty'] == 3  # 默认3星
    
    def test_component_without_parent(self, qapp):
        """测试组件可以在没有父组件的情况下实例化"""
        form = QuestionForm(parent=None)
        assert form is not None
        assert form.parent() is None
    
    def test_multiple_instances_independent(self, qapp):
        """测试多个实例互不干扰"""
        form1 = QuestionForm()
        form2 = QuestionForm()
        
        assert form1 is not form2
        
        # 修改form1不应影响form2
        form1.set_content("测试内容1")
        assert form1.get_data()['content'] == "测试内容1"
        assert form2.get_data()['content'] == ""


class TestDataRoundTrip:
    """
    测试数据往返一致性
    Property 12: QuestionForm数据往返一致性
    """
    
    def test_basic_data_round_trip(self, qapp):
        """测试基本数据往返"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '测试题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析内容',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        # 验证所有字段都正确往返
        assert result['subject'] == test_data['subject']
        assert result['question_type'] == test_data['question_type']
        assert result['content'] == test_data['content']
        assert result['my_answer'] == test_data['my_answer']
        assert result['answer'] == test_data['answer']
        assert result['explanation'] == test_data['explanation']
        assert result['difficulty'] == test_data['difficulty']
    
    def test_empty_strings_round_trip(self, qapp):
        """测试空字符串往返"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '',
            'my_answer': '',
            'answer': '',
            'explanation': '',
            'difficulty': 1
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        assert result['content'] == ''
        assert result['my_answer'] == ''
        assert result['answer'] == ''
        assert result['explanation'] == ''
    
    def test_multiline_text_round_trip(self, qapp):
        """测试多行文本往返"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '简答题',
            'content': '第一行\n第二行\n第三行',
            'my_answer': '答案第一行\n答案第二行',
            'answer': '正确答案第一行\n正确答案第二行',
            'explanation': '解析第一行\n解析第二行',
            'difficulty': 4
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        assert result['content'] == test_data['content']
        assert result['my_answer'] == test_data['my_answer']
        assert result['answer'] == test_data['answer']
        assert result['explanation'] == test_data['explanation']
    
    def test_chinese_text_round_trip(self, qapp):
        """测试中文文本往返"""
        form = QuestionForm()
        test_data = {
            'subject': '语文',
            'question_type': '填空题',
            'content': '这是一道中文题目，包含标点符号：，。！？',
            'my_answer': '我的中文答案',
            'answer': '正确的中文答案',
            'explanation': '详细的中文解析说明',
            'difficulty': 2
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        assert result['content'] == test_data['content']
        assert result['my_answer'] == test_data['my_answer']
        assert result['answer'] == test_data['answer']
        assert result['explanation'] == test_data['explanation']
    
    def test_special_characters_round_trip(self, qapp):
        """测试特殊字符往返"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '计算题',
            'content': '计算: 2 + 2 = ? (使用符号: +-*/=)',
            'my_answer': '4 (2+2=4)',
            'answer': '4',
            'explanation': '基本加法: 2 + 2 = 4',
            'difficulty': 1
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        assert result['content'] == test_data['content']
        assert result['my_answer'] == test_data['my_answer']
        assert result['answer'] == test_data['answer']
        assert result['explanation'] == test_data['explanation']
    
    def test_all_subjects_round_trip(self, qapp):
        """测试所有科目选项往返"""
        form = QuestionForm()
        subjects = ["数学", "物理", "化学", "英语", "语文", "其他"]
        
        for subject in subjects:
            test_data = {
                'subject': subject,
                'question_type': '单选题',
                'content': f'{subject}题目',
                'my_answer': '答案',
                'answer': '正确答案',
                'explanation': '解析',
                'difficulty': 3
            }
            
            form.set_data(test_data)
            result = form.get_data()
            
            assert result['subject'] == subject
    
    def test_all_question_types_round_trip(self, qapp):
        """测试所有题型选项往返"""
        form = QuestionForm()
        question_types = ["单选题", "多选题", "填空题", "简答题", "计算题", "其他"]
        
        for qtype in question_types:
            test_data = {
                'subject': '数学',
                'question_type': qtype,
                'content': f'{qtype}内容',
                'my_answer': '答案',
                'answer': '正确答案',
                'explanation': '解析',
                'difficulty': 3
            }
            
            form.set_data(test_data)
            result = form.get_data()
            
            assert result['question_type'] == qtype
    
    def test_all_difficulty_levels_round_trip(self, qapp):
        """测试所有难度等级往返"""
        form = QuestionForm()
        
        for difficulty in range(1, 6):  # 1-5星
            test_data = {
                'subject': '数学',
                'question_type': '单选题',
                'content': '题目',
                'my_answer': '答案',
                'answer': '正确答案',
                'explanation': '解析',
                'difficulty': difficulty
            }
            
            form.set_data(test_data)
            result = form.get_data()
            
            assert result['difficulty'] == difficulty
    
    def test_partial_data_set(self, qapp):
        """测试部分数据设置"""
        form = QuestionForm()
        
        # 只设置部分字段
        partial_data = {
            'content': '只设置内容',
            'answer': '只设置答案'
        }
        
        form.set_data(partial_data)
        result = form.get_data()
        
        # 设置的字段应该被更新
        assert result['content'] == '只设置内容'
        assert result['answer'] == '只设置答案'
        
        # 未设置的字段应该保持默认值
        assert result['subject'] in ["数学", "物理", "化学", "英语", "语文", "其他"]
        assert result['question_type'] in ["单选题", "多选题", "填空题", "简答题", "计算题", "其他"]
    
    def test_whitespace_handling(self, qapp):
        """测试空白字符处理"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '  题目内容有前后空格  ',
            'my_answer': '  答案有空格  ',
            'answer': '  正确答案有空格  ',
            'explanation': '  解析有空格  ',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        # get_data() 应该去除前后空格
        assert result['content'] == '题目内容有前后空格'
        assert result['my_answer'] == '答案有空格'
        assert result['answer'] == '正确答案有空格'
        assert result['explanation'] == '解析有空格'


class TestFormValidation:
    """测试表单验证逻辑"""
    
    def test_valid_form(self, qapp):
        """测试有效表单"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '有效的题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is True
        assert error == ""
    
    def test_empty_content_invalid(self, qapp):
        """测试空内容无效"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '',  # 空内容
            'my_answer': '答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is False
        assert '内容' in error
    
    def test_empty_answer_invalid(self, qapp):
        """测试空答案无效"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '',  # 空答案
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is False
        assert '答案' in error
    
    def test_whitespace_only_content_invalid(self, qapp):
        """测试仅空白字符的内容无效"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '   ',  # 仅空白字符
            'my_answer': '答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is False
        assert '内容' in error
    
    def test_whitespace_only_answer_invalid(self, qapp):
        """测试仅空白字符的答案无效"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '   ',  # 仅空白字符
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is False
        assert '答案' in error
    
    def test_empty_my_answer_valid(self, qapp):
        """测试空的'我的答案'是有效的（可选字段）"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目内容',
            'my_answer': '',  # 我的答案可以为空
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is True
    
    def test_empty_explanation_valid(self, qapp):
        """测试空解析是有效的（可选字段）"""
        form = QuestionForm()
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '',  # 解析可以为空
            'difficulty': 3
        }
        
        form.set_data(test_data)
        is_valid, error = form.validate()
        
        assert is_valid is True


class TestFormMethods:
    """测试表单方法"""
    
    def test_clear_method(self, qapp):
        """测试清空方法"""
        form = QuestionForm()
        
        # 设置数据
        test_data = {
            'subject': '物理',
            'question_type': '计算题',
            'content': '题目内容',
            'my_answer': '我的答案',
            'answer': '正确答案',
            'explanation': '解析',
            'difficulty': 5
        }
        form.set_data(test_data)
        
        # 清空
        form.clear()
        
        # 验证清空后的状态
        result = form.get_data()
        assert result['content'] == ''
        assert result['my_answer'] == ''
        assert result['answer'] == ''
        assert result['explanation'] == ''
        assert result['difficulty'] == 3  # 重置为默认值
    
    def test_set_content_method(self, qapp):
        """测试设置内容方法"""
        form = QuestionForm()
        test_content = "通过set_content设置的内容"
        
        form.set_content(test_content)
        
        result = form.get_data()
        assert result['content'] == test_content
    
    def test_focus_content_method(self, qapp):
        """测试聚焦内容方法"""
        form = QuestionForm()
        form.show()  # 需要显示才能聚焦
        
        # 调用聚焦方法（不会抛出异常即可）
        form.focus_content()
        
        # 验证内容编辑框有焦点
        assert form._content_edit.hasFocus()


class TestSignalEmission:
    """测试信号发送"""
    
    def test_data_changed_signal_on_content_change(self, qapp):
        """测试内容变化时发送信号"""
        form = QuestionForm()
        
        signal_received = []
        form.data_changed.connect(lambda: signal_received.append(True))
        
        # 修改内容
        form.set_content("新内容")
        
        # 验证信号被发送
        assert len(signal_received) > 0
    
    def test_data_changed_signal_on_subject_change(self, qapp):
        """测试科目变化时发送信号"""
        form = QuestionForm()
        
        signal_received = []
        form.data_changed.connect(lambda: signal_received.append(True))
        
        # 修改科目
        form._subject_combo.setCurrentIndex(1)
        
        # 验证信号被发送
        assert len(signal_received) > 0
    
    def test_data_changed_signal_on_difficulty_change(self, qapp):
        """测试难度变化时发送信号"""
        form = QuestionForm()
        
        signal_received = []
        form.data_changed.connect(lambda: signal_received.append(True))
        
        # 修改难度
        form._difficulty_combo.setCurrentIndex(4)
        
        # 验证信号被发送
        assert len(signal_received) > 0


class TestEdgeCases:
    """测试边界情况"""
    
    def test_invalid_difficulty_value(self, qapp):
        """测试无效的难度值"""
        form = QuestionForm()
        
        # 设置超出范围的难度值
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目',
            'answer': '答案',
            'difficulty': 10  # 超出1-5范围
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        # 应该保持原有值（不会设置无效值）
        assert 1 <= result['difficulty'] <= 5
    
    def test_invalid_subject_value(self, qapp):
        """测试无效的科目值"""
        form = QuestionForm()
        
        # 设置不存在的科目
        test_data = {
            'subject': '不存在的科目',
            'question_type': '单选题',
            'content': '题目',
            'answer': '答案',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        # 应该保持原有值（不会设置无效值）
        assert result['subject'] in ["数学", "物理", "化学", "英语", "语文", "其他"]
    
    def test_very_long_text(self, qapp):
        """测试非常长的文本"""
        form = QuestionForm()
        
        long_text = "很长的文本" * 1000  # 5000个字符
        test_data = {
            'subject': '数学',
            'question_type': '简答题',
            'content': long_text,
            'my_answer': long_text,
            'answer': long_text,
            'explanation': long_text,
            'difficulty': 3
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        # 应该能够处理长文本
        assert result['content'] == long_text
        assert result['my_answer'] == long_text
        assert result['answer'] == long_text
        assert result['explanation'] == long_text
    
    def test_unicode_emoji(self, qapp):
        """测试Unicode表情符号"""
        form = QuestionForm()
        
        test_data = {
            'subject': '数学',
            'question_type': '单选题',
            'content': '题目 😀 🎉 ⭐',
            'my_answer': '答案 ✅',
            'answer': '正确 ✓',
            'explanation': '解析 📝',
            'difficulty': 3
        }
        
        form.set_data(test_data)
        result = form.get_data()
        
        assert result['content'] == test_data['content']
        assert result['my_answer'] == test_data['my_answer']
        assert result['answer'] == test_data['answer']
        assert result['explanation'] == test_data['explanation']


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
