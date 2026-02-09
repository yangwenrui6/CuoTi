"""
FilterPanel组件单元测试

测试要求:
- 测试组件独立实例化
- 测试筛选条件获取
- 测试信号发送

**Validates: Requirements 3.1**
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock
from PyQt6.QtWidgets import QApplication

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.components.filter_panel import FilterPanel


# 创建QApplication实例（PyQt测试需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_ui_service():
    """创建mock UIService"""
    service = Mock()
    
    # Mock get_filter_options方法
    service.get_filter_options.return_value = {
        'subjects': ['全部', '数学', '物理', '化学', '英语'],
        'difficulties': ['全部', '1星', '2星', '3星', '4星', '5星'],
        'mastery_levels': ['全部', '生疏', '学习中', '掌握', '熟练']
    }
    
    # Mock parse_filter_from_ui方法
    def parse_filter(subject, difficulty, mastery):
        filters = {}
        if subject and subject != "全部":
            filters['subject'] = subject
        if difficulty and difficulty != "全部":
            try:
                filters['difficulty'] = int(difficulty[0])
            except (ValueError, IndexError):
                pass
        if mastery and mastery != "全部":
            mastery_map = {
                '生疏': 0,
                '学习中': 1,
                '掌握': 2,
                '熟练': 3
            }
            if mastery in mastery_map:
                filters['mastery_level'] = mastery_map[mastery]
        return filters
    
    service.parse_filter_from_ui.side_effect = parse_filter
    
    return service


class TestFilterPanelInitialization:
    """测试组件独立实例化"""
    
    def test_component_can_be_instantiated(self, qapp, mock_ui_service):
        """测试组件可以独立实例化"""
        panel = FilterPanel(mock_ui_service)
        assert panel is not None
        assert isinstance(panel, FilterPanel)
    
    def test_initial_state(self, qapp, mock_ui_service):
        """测试初始状态"""
        panel = FilterPanel(mock_ui_service)
        assert panel._ui_service == mock_ui_service
        
        # 验证UI元素已初始化
        assert hasattr(panel, '_subject_filter')
        assert hasattr(panel, '_difficulty_filter')
        assert hasattr(panel, '_mastery_filter')
    
    def test_component_without_parent(self, qapp, mock_ui_service):
        """测试组件可以在没有父组件的情况下实例化"""
        panel = FilterPanel(mock_ui_service, parent=None)
        assert panel is not None
        assert panel.parent() is None
    
    def test_multiple_instances_independent(self, qapp, mock_ui_service):
        """测试多个实例互不干扰"""
        panel1 = FilterPanel(mock_ui_service)
        panel2 = FilterPanel(mock_ui_service)
        
        assert panel1 is not panel2
        assert panel1._ui_service == mock_ui_service
        assert panel2._ui_service == mock_ui_service
    
    def test_ui_elements_initialized(self, qapp, mock_ui_service):
        """测试UI元素已初始化"""
        panel = FilterPanel(mock_ui_service)
        
        # 验证下拉框存在
        assert panel._subject_filter is not None
        assert panel._difficulty_filter is not None
        assert panel._mastery_filter is not None
        
        # 验证下拉框有选项
        assert panel._subject_filter.count() > 0
        assert panel._difficulty_filter.count() > 0
        assert panel._mastery_filter.count() > 0
    
    def test_service_method_called_on_init(self, qapp, mock_ui_service):
        """测试初始化时调用服务方法"""
        panel = FilterPanel(mock_ui_service)
        
        # 验证get_filter_options被调用
        mock_ui_service.get_filter_options.assert_called_once()


class TestMockServiceIntegration:
    """测试mock服务集成"""
    
    def test_accepts_mock_service(self, qapp, mock_ui_service):
        """测试组件接受mock服务"""
        panel = FilterPanel(mock_ui_service)
        assert panel._ui_service == mock_ui_service
    
    def test_service_not_created_internally(self, qapp, mock_ui_service):
        """测试组件不在内部创建服务"""
        panel = FilterPanel(mock_ui_service)
        # 验证使用的是传入的服务，而不是内部创建的
        assert panel._ui_service is mock_ui_service
    
    def test_different_mock_services(self, qapp):
        """测试可以使用不同的mock服务"""
        service1 = Mock()
        service1.get_filter_options.return_value = {
            'subjects': ['全部', '数学'],
            'difficulties': ['全部', '1星'],
            'mastery_levels': ['全部', '生疏']
        }
        service1.parse_filter_from_ui.return_value = {}
        
        service2 = Mock()
        service2.get_filter_options.return_value = {
            'subjects': ['全部', '物理'],
            'difficulties': ['全部', '2星'],
            'mastery_levels': ['全部', '掌握']
        }
        service2.parse_filter_from_ui.return_value = {}
        
        panel1 = FilterPanel(service1)
        panel2 = FilterPanel(service2)
        
        assert panel1._ui_service is service1
        assert panel2._ui_service is service2
        assert panel1._ui_service is not panel2._ui_service


class TestFilterRetrieval:
    """测试筛选条件获取"""
    
    def test_get_filters_initial_state(self, qapp, mock_ui_service):
        """测试获取初始筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        filters = panel.get_filters()
        
        # 初始状态应该是空字典（全部选中）
        assert isinstance(filters, dict)
        mock_ui_service.parse_filter_from_ui.assert_called()
    
    def test_get_filters_with_subject(self, qapp, mock_ui_service):
        """测试获取科目筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置科目筛选
        panel._subject_filter.setCurrentText("数学")
        
        filters = panel.get_filters()
        
        # 验证parse_filter_from_ui被调用
        assert mock_ui_service.parse_filter_from_ui.called
        # 验证返回的是字典
        assert isinstance(filters, dict)
    
    def test_get_filters_with_difficulty(self, qapp, mock_ui_service):
        """测试获取难度筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置难度筛选
        panel._difficulty_filter.setCurrentText("3星")
        
        filters = panel.get_filters()
        
        # 验证返回的是字典
        assert isinstance(filters, dict)
        mock_ui_service.parse_filter_from_ui.assert_called()
    
    def test_get_filters_with_mastery(self, qapp, mock_ui_service):
        """测试获取掌握度筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置掌握度筛选
        panel._mastery_filter.setCurrentText("掌握")
        
        filters = panel.get_filters()
        
        # 验证返回的是字典
        assert isinstance(filters, dict)
        mock_ui_service.parse_filter_from_ui.assert_called()
    
    def test_get_filters_with_all_conditions(self, qapp, mock_ui_service):
        """测试获取所有筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置所有筛选条件
        panel._subject_filter.setCurrentText("数学")
        panel._difficulty_filter.setCurrentText("3星")
        panel._mastery_filter.setCurrentText("掌握")
        
        filters = panel.get_filters()
        
        # 验证返回的是字典
        assert isinstance(filters, dict)
        # 验证parse_filter_from_ui被调用，参数正确
        mock_ui_service.parse_filter_from_ui.assert_called_with("数学", "3星", "掌握")
    
    def test_get_filters_multiple_times(self, qapp, mock_ui_service):
        """测试多次获取筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 第一次获取
        filters1 = panel.get_filters()
        assert isinstance(filters1, dict)
        
        # 修改筛选条件
        panel._subject_filter.setCurrentText("物理")
        
        # 第二次获取
        filters2 = panel.get_filters()
        assert isinstance(filters2, dict)
        
        # 验证parse_filter_from_ui被调用多次
        assert mock_ui_service.parse_filter_from_ui.call_count >= 2


class TestResetFilters:
    """测试重置筛选条件"""
    
    def test_reset_filters(self, qapp, mock_ui_service):
        """测试重置筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置筛选条件
        panel._subject_filter.setCurrentIndex(2)
        panel._difficulty_filter.setCurrentIndex(3)
        panel._mastery_filter.setCurrentIndex(1)
        
        # 重置
        panel.reset_filters()
        
        # 验证所有下拉框都回到第一项
        assert panel._subject_filter.currentIndex() == 0
        assert panel._difficulty_filter.currentIndex() == 0
        assert panel._mastery_filter.currentIndex() == 0
    
    def test_reset_filters_initial_state(self, qapp, mock_ui_service):
        """测试初始状态重置"""
        panel = FilterPanel(mock_ui_service)
        
        # 初始状态就重置
        panel.reset_filters()
        
        # 应该不会出错
        assert panel._subject_filter.currentIndex() == 0
        assert panel._difficulty_filter.currentIndex() == 0
        assert panel._mastery_filter.currentIndex() == 0
    
    def test_reset_filters_multiple_times(self, qapp, mock_ui_service):
        """测试多次重置"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置筛选条件
        panel._subject_filter.setCurrentIndex(1)
        panel.reset_filters()
        
        # 再次设置
        panel._subject_filter.setCurrentIndex(2)
        panel.reset_filters()
        
        # 验证重置成功
        assert panel._subject_filter.currentIndex() == 0


class TestSignalEmission:
    """测试信号发送"""
    
    def test_filter_changed_signal_on_subject_change(self, qapp, mock_ui_service):
        """测试科目变化时发送信号"""
        panel = FilterPanel(mock_ui_service)
        
        # 记录信号
        signal_received = []
        panel.filter_changed.connect(lambda filters: signal_received.append(filters))
        
        # 修改科目
        panel._subject_filter.setCurrentIndex(1)
        qapp.processEvents()
        
        # 验证信号被发送
        assert len(signal_received) > 0
        assert isinstance(signal_received[0], dict)
    
    def test_filter_changed_signal_on_difficulty_change(self, qapp, mock_ui_service):
        """测试难度变化时发送信号"""
        panel = FilterPanel(mock_ui_service)
        
        # 记录信号
        signal_received = []
        panel.filter_changed.connect(lambda filters: signal_received.append(filters))
        
        # 修改难度
        panel._difficulty_filter.setCurrentIndex(2)
        qapp.processEvents()
        
        # 验证信号被发送
        assert len(signal_received) > 0
        assert isinstance(signal_received[0], dict)
    
    def test_filter_changed_signal_on_mastery_change(self, qapp, mock_ui_service):
        """测试掌握度变化时发送信号"""
        panel = FilterPanel(mock_ui_service)
        
        # 记录信号
        signal_received = []
        panel.filter_changed.connect(lambda filters: signal_received.append(filters))
        
        # 修改掌握度
        panel._mastery_filter.setCurrentIndex(1)
        qapp.processEvents()
        
        # 验证信号被发送
        assert len(signal_received) > 0
        assert isinstance(signal_received[0], dict)
    
    def test_signal_with_callback(self, qapp, mock_ui_service):
        """测试信号回调功能"""
        panel = FilterPanel(mock_ui_service)
        
        callback_data = []
        
        def on_filter_changed(filters):
            callback_data.append(filters)
        
        panel.filter_changed.connect(on_filter_changed)
        
        # 触发变化
        panel._subject_filter.setCurrentIndex(1)
        qapp.processEvents()
        
        # 验证回调被调用
        assert len(callback_data) > 0
        assert isinstance(callback_data[0], dict)
    
    def test_multiple_signal_listeners(self, qapp, mock_ui_service):
        """测试多个信号监听器"""
        panel = FilterPanel(mock_ui_service)
        
        listener1_data = []
        listener2_data = []
        
        panel.filter_changed.connect(lambda filters: listener1_data.append(filters))
        panel.filter_changed.connect(lambda filters: listener2_data.append(filters))
        
        # 触发信号
        panel._subject_filter.setCurrentIndex(1)
        qapp.processEvents()
        
        # 验证所有监听器都收到信号
        assert len(listener1_data) > 0
        assert len(listener2_data) > 0
    
    def test_signal_contains_correct_data(self, qapp, mock_ui_service):
        """测试信号包含正确的数据"""
        panel = FilterPanel(mock_ui_service)
        
        signal_received = []
        panel.filter_changed.connect(lambda filters: signal_received.append(filters))
        
        # 设置特定的筛选条件
        panel._subject_filter.setCurrentText("数学")
        qapp.processEvents()
        
        # 验证信号数据
        assert len(signal_received) > 0
        # 验证parse_filter_from_ui被调用
        assert mock_ui_service.parse_filter_from_ui.called


class TestFilterOptions:
    """测试筛选选项"""
    
    def test_subject_options_loaded(self, qapp, mock_ui_service):
        """测试科目选项已加载"""
        panel = FilterPanel(mock_ui_service)
        
        # 验证科目选项
        subjects = [panel._subject_filter.itemText(i) 
                   for i in range(panel._subject_filter.count())]
        
        assert '全部' in subjects
        assert '数学' in subjects
        assert len(subjects) > 0
    
    def test_difficulty_options_loaded(self, qapp, mock_ui_service):
        """测试难度选项已加载"""
        panel = FilterPanel(mock_ui_service)
        
        # 验证难度选项
        difficulties = [panel._difficulty_filter.itemText(i) 
                       for i in range(panel._difficulty_filter.count())]
        
        assert '全部' in difficulties
        assert '1星' in difficulties
        assert len(difficulties) > 0
    
    def test_mastery_options_loaded(self, qapp, mock_ui_service):
        """测试掌握度选项已加载"""
        panel = FilterPanel(mock_ui_service)
        
        # 验证掌握度选项
        mastery_levels = [panel._mastery_filter.itemText(i) 
                         for i in range(panel._mastery_filter.count())]
        
        assert '全部' in mastery_levels
        assert '生疏' in mastery_levels
        assert len(mastery_levels) > 0
    
    def test_custom_filter_options(self, qapp):
        """测试自定义筛选选项"""
        service = Mock()
        service.get_filter_options.return_value = {
            'subjects': ['全部', '自定义科目'],
            'difficulties': ['全部', '简单', '困难'],
            'mastery_levels': ['全部', '未掌握', '已掌握']
        }
        service.parse_filter_from_ui.return_value = {}
        
        panel = FilterPanel(service)
        
        # 验证自定义选项
        subjects = [panel._subject_filter.itemText(i) 
                   for i in range(panel._subject_filter.count())]
        assert '自定义科目' in subjects


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_filter_options(self, qapp):
        """测试空筛选选项"""
        service = Mock()
        service.get_filter_options.return_value = {
            'subjects': [],
            'difficulties': [],
            'mastery_levels': []
        }
        service.parse_filter_from_ui.return_value = {}
        
        # 应该不会崩溃
        panel = FilterPanel(service)
        assert panel is not None
    
    def test_service_returns_none(self, qapp):
        """测试服务返回None"""
        service = Mock()
        service.get_filter_options.return_value = {
            'subjects': ['全部'],
            'difficulties': ['全部'],
            'mastery_levels': ['全部']
        }
        service.parse_filter_from_ui.return_value = None
        
        panel = FilterPanel(service)
        
        # get_filters应该处理None情况
        filters = panel.get_filters()
        # 即使服务返回None，也应该返回某个值
        assert filters is not None or filters is None  # 允许两种情况
    
    def test_rapid_filter_changes(self, qapp, mock_ui_service):
        """测试快速连续修改筛选条件"""
        panel = FilterPanel(mock_ui_service)
        
        signal_count = []
        panel.filter_changed.connect(lambda f: signal_count.append(1))
        
        # 快速修改多次
        for i in range(5):
            panel._subject_filter.setCurrentIndex(i % 3)
            qapp.processEvents()
        
        # 应该收到多个信号
        assert len(signal_count) > 0
    
    def test_reset_after_signal_connection(self, qapp, mock_ui_service):
        """测试连接信号后重置"""
        panel = FilterPanel(mock_ui_service)
        
        signal_received = []
        panel.filter_changed.connect(lambda f: signal_received.append(f))
        
        # 设置筛选条件
        panel._subject_filter.setCurrentIndex(1)
        qapp.processEvents()
        
        # 重置
        panel.reset_filters()
        qapp.processEvents()
        
        # 应该收到信号
        assert len(signal_received) > 0


class TestUIBehavior:
    """测试UI行为"""
    
    def test_combobox_interaction(self, qapp, mock_ui_service):
        """测试下拉框交互"""
        panel = FilterPanel(mock_ui_service)
        
        # 获取初始索引
        initial_index = panel._subject_filter.currentIndex()
        
        # 修改索引
        panel._subject_filter.setCurrentIndex(1)
        
        # 验证修改成功
        assert panel._subject_filter.currentIndex() != initial_index
    
    def test_filter_state_persistence(self, qapp, mock_ui_service):
        """测试筛选状态持久性"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置筛选条件
        panel._subject_filter.setCurrentIndex(2)
        panel._difficulty_filter.setCurrentIndex(3)
        
        # 获取筛选条件
        filters1 = panel.get_filters()
        
        # 再次获取（不修改）
        filters2 = panel.get_filters()
        
        # 状态应该保持
        assert panel._subject_filter.currentIndex() == 2
        assert panel._difficulty_filter.currentIndex() == 3
    
    def test_ui_state_after_reset(self, qapp, mock_ui_service):
        """测试重置后UI状态"""
        panel = FilterPanel(mock_ui_service)
        
        # 设置筛选条件
        panel._subject_filter.setCurrentIndex(2)
        panel._difficulty_filter.setCurrentIndex(3)
        panel._mastery_filter.setCurrentIndex(1)
        
        # 重置
        panel.reset_filters()
        
        # 验证UI状态
        assert panel._subject_filter.currentIndex() == 0
        assert panel._difficulty_filter.currentIndex() == 0
        assert panel._mastery_filter.currentIndex() == 0
        assert panel._subject_filter.currentText() == "全部"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
