"""
ImageUploader组件单元测试

测试要求:
- 测试组件独立实例化
- 测试图片加载和信号发送
- 测试中文路径处理

**Validates: Requirements 3.1**
"""

import sys
import pytest
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import QApplication

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mistake_book.ui.components.image_uploader import ImageUploader


# 创建QApplication实例（PyQt测试需要）
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def test_image_path(tmp_path):
    """创建测试图片"""
    img = Image.new('RGB', (100, 100), color='red')
    image_path = tmp_path / "test_image.png"
    img.save(image_path)
    return str(image_path)


@pytest.fixture
def chinese_path_image(tmp_path):
    """创建中文路径的测试图片"""
    # 创建中文目录
    chinese_dir = tmp_path / "测试目录"
    chinese_dir.mkdir(exist_ok=True)
    
    # 创建图片
    img = Image.new('RGB', (100, 100), color='blue')
    image_path = chinese_dir / "测试图片.png"
    img.save(image_path)
    return str(image_path)


class TestImageUploaderInitialization:
    """测试组件独立实例化"""
    
    def test_component_can_be_instantiated(self, qapp):
        """测试组件可以独立实例化"""
        uploader = ImageUploader()
        assert uploader is not None
        assert isinstance(uploader, ImageUploader)
    
    def test_initial_state(self, qapp):
        """测试初始状态"""
        uploader = ImageUploader()
        assert uploader.get_image_path() is None
        assert uploader._current_image_path is None
    
    def test_component_without_parent(self, qapp):
        """测试组件可以在没有父组件的情况下实例化"""
        uploader = ImageUploader(parent=None)
        assert uploader is not None
        assert uploader.parent() is None
    
    def test_multiple_instances_independent(self, qapp):
        """测试多个实例互不干扰"""
        uploader1 = ImageUploader()
        uploader2 = ImageUploader()
        
        assert uploader1 is not uploader2
        assert uploader1.get_image_path() is None
        assert uploader2.get_image_path() is None


class TestImageLoading:
    """测试图片加载功能"""
    
    def test_load_valid_image(self, qapp, test_image_path):
        """测试加载有效图片"""
        uploader = ImageUploader()
        result = uploader.set_image(test_image_path)
        
        assert result is True
        assert uploader.get_image_path() == test_image_path
        assert uploader._current_image_path == test_image_path
    
    def test_load_nonexistent_image(self, qapp):
        """测试加载不存在的图片"""
        uploader = ImageUploader()
        result = uploader.set_image("/nonexistent/path/image.png")
        
        assert result is False
        assert uploader.get_image_path() is None
    
    def test_clear_image(self, qapp, test_image_path):
        """测试清空图片"""
        uploader = ImageUploader()
        uploader.set_image(test_image_path)
        
        # 确认图片已加载
        assert uploader.get_image_path() is not None
        
        # 清空图片
        uploader.clear()
        
        assert uploader.get_image_path() is None
        assert uploader._current_image_path is None
    
    def test_replace_image(self, qapp, test_image_path, tmp_path):
        """测试更换图片"""
        uploader = ImageUploader()
        
        # 加载第一张图片
        uploader.set_image(test_image_path)
        assert uploader.get_image_path() == test_image_path
        
        # 创建第二张图片
        img2 = Image.new('RGB', (100, 100), color='green')
        image_path2 = tmp_path / "test_image2.png"
        img2.save(image_path2)
        
        # 更换图片
        uploader.set_image(str(image_path2))
        assert uploader.get_image_path() == str(image_path2)


class TestSignalEmission:
    """测试信号发送"""
    
    def test_image_selected_signal(self, qapp, test_image_path):
        """测试image_selected信号发送"""
        uploader = ImageUploader()
        
        # 使用列表记录信号
        signal_received = []
        uploader.image_selected.connect(lambda path: signal_received.append(path))
        
        # 加载图片并手动发送信号（模拟用户操作）
        uploader._load_image(test_image_path)
        uploader.image_selected.emit(test_image_path)
        
        # 验证信号被发送
        assert len(signal_received) == 1
        assert signal_received[0] == test_image_path
    
    def test_image_cleared_signal(self, qapp, test_image_path):
        """测试image_cleared信号发送"""
        uploader = ImageUploader()
        uploader.set_image(test_image_path)
        
        # 使用列表记录信号
        signal_received = []
        uploader.image_cleared.connect(lambda: signal_received.append(True))
        
        # 清空图片
        uploader.clear()
        
        # 验证信号被发送
        assert len(signal_received) == 1
    
    def test_signal_with_callback(self, qapp, test_image_path):
        """测试信号回调功能"""
        uploader = ImageUploader()
        signal_received = []
        
        # 连接信号到回调函数
        uploader.image_selected.connect(lambda path: signal_received.append(path))
        
        # 触发信号
        uploader._load_image(test_image_path)
        uploader.image_selected.emit(test_image_path)
        
        # 验证回调被调用
        assert len(signal_received) == 1
        assert signal_received[0] == test_image_path


class TestChinesePathHandling:
    """测试中文路径处理"""
    
    def test_load_chinese_path_image(self, qapp, chinese_path_image):
        """测试加载中文路径的图片"""
        uploader = ImageUploader()
        result = uploader.set_image(chinese_path_image)
        
        assert result is True
        assert uploader.get_image_path() == chinese_path_image
    
    def test_chinese_filename(self, qapp, tmp_path):
        """测试中文文件名"""
        # 创建中文文件名的图片
        img = Image.new('RGB', (100, 100), color='yellow')
        image_path = tmp_path / "中文文件名.png"
        img.save(image_path)
        
        uploader = ImageUploader()
        result = uploader.set_image(str(image_path))
        
        assert result is True
        assert uploader.get_image_path() == str(image_path)
    
    def test_mixed_chinese_english_path(self, qapp, tmp_path):
        """测试中英文混合路径"""
        # 创建中英文混合路径
        mixed_dir = tmp_path / "test测试" / "images图片"
        mixed_dir.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (100, 100), color='purple')
        image_path = mixed_dir / "test测试.png"
        img.save(image_path)
        
        uploader = ImageUploader()
        result = uploader.set_image(str(image_path))
        
        assert result is True
        assert uploader.get_image_path() == str(image_path)


class TestUIBehavior:
    """测试UI行为"""
    
    def test_hint_text_changes_after_load(self, qapp, test_image_path):
        """测试加载图片后提示文字变化"""
        uploader = ImageUploader()
        initial_text = uploader._hint_label.text()
        
        uploader.set_image(test_image_path)
        
        # 提示文字应该改变
        assert uploader._hint_label.text() != initial_text
        assert "✅" in uploader._hint_label.text()
    
    def test_button_text_changes_after_load(self, qapp, test_image_path):
        """测试加载图片后按钮文字变化"""
        uploader = ImageUploader()
        initial_button_text = uploader._upload_btn.text()
        
        uploader.set_image(test_image_path)
        
        # 按钮文字应该改变
        assert uploader._upload_btn.text() != initial_button_text
        assert "更换" in uploader._upload_btn.text()
    
    def test_image_preview_visible_after_load(self, qapp, test_image_path):
        """测试加载图片后预览可见"""
        uploader = ImageUploader()
        uploader.show()  # Show the widget so child widgets can be visible
        qapp.processEvents()  # Process Qt events
        
        # 初始状态预览不可见
        assert not uploader._image_label.isVisible()
        
        result = uploader.set_image(test_image_path)
        qapp.processEvents()  # Process Qt events
        
        # 确保图片加载成功
        assert result is True
        
        # 加载后预览可见
        assert uploader._image_label.isVisible()
    
    def test_view_button_visible_after_load(self, qapp, test_image_path):
        """测试加载图片后查看按钮可见"""
        uploader = ImageUploader()
        uploader.show()  # Show the widget so child widgets can be visible
        qapp.processEvents()  # Process Qt events
        
        # 初始状态按钮不可见
        assert not uploader._view_btn.isVisible()
        
        result = uploader.set_image(test_image_path)
        qapp.processEvents()  # Process Qt events
        
        # 确保图片加载成功
        assert result is True
        
        # 加载后按钮可见
        assert uploader._view_btn.isVisible()
    
    def test_ui_reset_after_clear(self, qapp, test_image_path):
        """测试清空后UI重置"""
        uploader = ImageUploader()
        uploader.show()  # Show the widget
        qapp.processEvents()
        
        uploader.set_image(test_image_path)
        qapp.processEvents()
        
        # 清空
        uploader.clear()
        qapp.processEvents()
        
        # UI应该重置
        assert not uploader._image_label.isVisible()
        assert not uploader._view_btn.isVisible()
        assert "拖拽" in uploader._hint_label.text()


class TestEdgeCases:
    """测试边界情况"""
    
    def test_load_empty_path(self, qapp):
        """测试加载空路径"""
        uploader = ImageUploader()
        result = uploader.set_image("")
        
        assert result is False
        assert uploader.get_image_path() is None
    
    def test_load_invalid_image_format(self, qapp, tmp_path):
        """测试加载无效图片格式"""
        # 创建一个文本文件
        text_file = tmp_path / "not_an_image.txt"
        text_file.write_text("This is not an image")
        
        uploader = ImageUploader()
        result = uploader.set_image(str(text_file))
        
        assert result is False
        assert uploader.get_image_path() is None
    
    def test_load_corrupted_image(self, qapp, tmp_path):
        """测试加载损坏的图片文件"""
        # 创建一个假的PNG文件（只有头部）
        fake_png = tmp_path / "corrupted.png"
        fake_png.write_bytes(b'\x89PNG\r\n\x1a\n')
        
        uploader = ImageUploader()
        result = uploader.set_image(str(fake_png))
        
        assert result is False
        assert uploader.get_image_path() is None
    
    def test_set_hint_text(self, qapp):
        """测试设置自定义提示文字"""
        uploader = ImageUploader()
        custom_text = "自定义提示文字"
        
        uploader.set_hint_text(custom_text)
        
        assert uploader._hint_label.text() == custom_text


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
