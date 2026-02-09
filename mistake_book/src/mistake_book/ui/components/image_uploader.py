"""图片上传组件 - 支持拖拽和点击上传"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageUploader(QWidget):
    """图片上传组件 - 支持拖拽、点击上传、图片预览"""
    
    # 信号
    image_selected = pyqtSignal(str)  # 图片路径
    image_cleared = pyqtSignal()      # 清空图片
    
    def __init__(self, parent=None):
        """初始化组件"""
        super().__init__(parent)
        self._current_image_path: Optional[str] = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setAcceptDrops(True)
        self.setMinimumHeight(250)
        self.setStyleSheet("""
            ImageUploader {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
            ImageUploader:hover {
                background-color: #d5dbdb;
            }
        """)
        
        # 设置鼠标指针为手型
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        
        # 提示文字
        self._hint_label = QLabel("📸 拖拽图片到此处\n或点击上传图片")
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint_label.setStyleSheet("font-size: 14pt; color: #7f8c8d;")
        layout.addWidget(self._hint_label)
        
        # 上传按钮
        self._upload_btn = QPushButton("📁 选择图片")
        self._upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self._upload_btn.clicked.connect(self._on_select_clicked)
        layout.addWidget(self._upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 图片预览
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setVisible(False)
        self._image_label.setStyleSheet(
            "border: 1px solid #bdc3c7; background-color: white;"
        )
        self._image_label.setMaximumHeight(300)
        layout.addWidget(self._image_label)
        
        # 查看大图按钮
        self._view_btn = QPushButton("🔍 查看大图")
        self._view_btn.setVisible(False)
        self._view_btn.clicked.connect(self._view_full_image)
        layout.addWidget(self._view_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def get_image_path(self) -> Optional[str]:
        """获取当前图片路径"""
        return self._current_image_path
    
    def set_image(self, path: str) -> bool:
        """
        设置图片（用于编辑场景）
        
        Args:
            path: 图片路径
            
        Returns:
            是否加载成功
        """
        return self._load_image(path)
    
    def clear(self):
        """清空图片"""
        self._current_image_path = None
        self._image_label.clear()
        self._image_label.setVisible(False)
        self._view_btn.setVisible(False)
        self._hint_label.setText("📸 拖拽图片到此处\n或点击上传图片")
        self._upload_btn.setText("📁 选择图片")
        self.image_cleared.emit()
    
    def set_hint_text(self, text: str):
        """设置提示文字"""
        self._hint_label.setText(text)
    
    def mousePressEvent(self, event):
        """点击区域触发上传"""
        if not self._image_label.isVisible():
            self._on_select_clicked()
    
    def _on_select_clicked(self):
        """点击选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )
        
        if file_path:
            if self._load_image(file_path):
                self.image_selected.emit(file_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                if self._load_image(file_path):
                    self.image_selected.emit(file_path)
            else:
                self._hint_label.setText("❌ 不支持的文件格式\n请选择图片文件")
    
    def _load_image(self, path: str) -> bool:
        """
        加载图片预览
        
        Args:
            path: 图片路径
            
        Returns:
            是否加载成功
        """
        try:
            # 使用PIL加载图片，避免QPixmap的中文路径问题
            from PIL import Image
            import numpy as np
            from PyQt6.QtGui import QImage
            
            # 使用PIL读取图片
            pil_image = Image.open(path)
            
            # 转换为RGB模式（如果是RGBA或其他模式）
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为numpy数组
            img_array = np.array(pil_image)
            
            # 转换为QImage
            height, width, channel = img_array.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                img_array.data, width, height, 
                bytes_per_line, QImage.Format.Format_RGB888
            )
            
            # 转换为QPixmap
            pixmap = QPixmap.fromImage(q_image)
            
            # 缩放图片以适应预览区域
            scaled = pixmap.scaled(
                400, 280, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self._image_label.setPixmap(scaled)
            self._image_label.setVisible(True)
            self._view_btn.setVisible(True)
            self._hint_label.setText("✅ 图片已加载")
            self._upload_btn.setText("📁 更换图片")
            
            self._current_image_path = path
            return True
            
        except Exception as e:
            logger.error(f"图片加载失败: {e}", exc_info=True)
            self._hint_label.setText(f"❌ 图片加载失败\n{str(e)}")
            self._current_image_path = None
            return False
    
    def _view_full_image(self):
        """查看完整图片"""
        if self._current_image_path:
            from mistake_book.ui.dialogs.image_viewer import ImageViewerDialog
            viewer = ImageViewerDialog(self._current_image_path, self)
            viewer.exec()
