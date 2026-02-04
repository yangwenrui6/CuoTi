"""图片查看器对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path


class ImageViewerDialog(QDialog):
    """图片查看器 - 显示完整图片"""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("查看图片")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_image()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 图片显示区域（带滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2c3e50;")
        
        scroll.setWidget(self.image_label)
        layout.addWidget(scroll)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 文件信息
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #7f8c8d;")
        btn_layout.addWidget(self.info_label)
        
        btn_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def load_image(self):
        """加载图片"""
        try:
            pixmap = QPixmap(self.image_path)
            
            if pixmap.isNull():
                self.image_label.setText("❌ 无法加载图片")
                return
            
            # 显示原始大小，但限制最大尺寸
            max_width = 1200
            max_height = 900
            
            if pixmap.width() > max_width or pixmap.height() > max_height:
                pixmap = pixmap.scaled(
                    max_width, max_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            self.image_label.setPixmap(pixmap)
            
            # 显示文件信息
            path = Path(self.image_path)
            file_size = path.stat().st_size / 1024  # KB
            self.info_label.setText(
                f"📁 {path.name} | "
                f"📏 {pixmap.width()}×{pixmap.height()} | "
                f"💾 {file_size:.1f} KB"
            )
            
        except Exception as e:
            self.image_label.setText(f"❌ 加载失败: {e}")
