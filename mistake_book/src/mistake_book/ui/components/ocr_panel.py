"""OCR识别面板组件"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OCRWorker(QThread):
    """OCR识别工作线程"""
    finished = pyqtSignal(bool, str, str)  # success, message, text
    
    def __init__(self, question_service, image_path):
        super().__init__()
        self.question_service = question_service
        self.image_path = image_path
    
    def run(self):
        """在后台线程中执行OCR识别"""
        try:
            success, message, recognized_text = \
                self.question_service.recognize_image_with_retry(
                    Path(self.image_path)
                )
            self.finished.emit(success, message, recognized_text or "")
        except Exception as e:
            self.finished.emit(False, f"识别出错：{str(e)}", "")


class OCRPanel(QWidget):
    """OCR识别面板"""
    
    # 信号
    recognition_started = pyqtSignal()           # 开始识别
    recognition_completed = pyqtSignal(str)      # 识别完成(文本)
    recognition_failed = pyqtSignal(str)         # 识别失败(错误信息)
    
    def __init__(self, question_service, parent=None):
        """
        初始化OCR面板
        
        Args:
            question_service: QuestionService实例（包含OCR引擎）
        """
        super().__init__(parent)
        self._question_service = question_service
        self._is_recognizing = False
        self._current_image_path: Optional[str] = None
        self._worker: Optional[OCRWorker] = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 状态标签
        self._status_label = QLabel("等待图片...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("font-size: 11pt; color: #7f8c8d;")
        layout.addWidget(self._status_label)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 重新识别按钮
        self._recognize_btn = QPushButton("🔄 重新识别")
        self._recognize_btn.setEnabled(False)
        self._recognize_btn.clicked.connect(self._on_recognize_clicked)
        self._recognize_btn.setToolTip("拖拽图片后会自动识别，点击此按钮可重新识别")
        btn_layout.addWidget(self._recognize_btn)
        
        layout.addLayout(btn_layout)
    
    def recognize_image(self, image_path: str):
        """
        识别图片
        
        Args:
            image_path: 图片路径
        """
        self._current_image_path = image_path
        self._recognize_btn.setEnabled(True)
        
        # 自动触发识别
        self._do_recognition()
    
    def set_status(self, status: str):
        """设置状态文本"""
        self._status_label.setText(status)
    
    def is_recognizing(self) -> bool:
        """是否正在识别"""
        return self._is_recognizing
    
    def _on_recognize_clicked(self):
        """手动点击识别按钮"""
        if self._current_image_path:
            self._do_recognition()
    
    def _do_recognition(self):
        """执行OCR识别"""
        if not self._current_image_path:
            return
        
        # 检查OCR引擎是否可用
        if not self._question_service.ocr_engine:
            self.set_status("⚠️ OCR功能未启用")
            self.recognition_failed.emit("OCR功能未启用")
            return
        
        if not self._question_service.ocr_engine.is_available():
            self.set_status("⚠️ OCR引擎不可用")
            self.recognition_failed.emit("OCR引擎不可用")
            return
        
        # 检查OCR引擎是否已初始化
        ocr_engine = self._question_service.ocr_engine
        
        if not ocr_engine._initialized:
            if ocr_engine.is_initializing():
                # 正在初始化
                self.set_status("⏳ OCR模型正在后台加载中...")
                self._recognize_btn.setText("⏳ 加载中...")
                self._recognize_btn.setEnabled(False)
                
                # 等待初始化完成
                from PyQt6.QtCore import QTimer
                
                def check_init_status():
                    if ocr_engine._initialized:
                        # 初始化完成，开始识别
                        self.set_status("🔄 正在识别文字...")
                        QTimer.singleShot(100, self._start_recognition)
                    elif not ocr_engine.is_initializing():
                        # 初始化失败
                        self.set_status("❌ 模型加载失败")
                        self._recognize_btn.setText("🔄 重新识别")
                        self._recognize_btn.setEnabled(True)
                        self.recognition_failed.emit("模型加载失败")
                    else:
                        # 继续等待
                        QTimer.singleShot(1000, check_init_status)
                
                QTimer.singleShot(1000, check_init_status)
                return
            else:
                # 还未开始初始化
                self.set_status("⏳ OCR模型正在后台加载中...")
                self._recognize_btn.setText("⏳ 加载中...")
                self._recognize_btn.setEnabled(False)
                self.recognition_failed.emit("OCR模型正在加载中，请稍后重试")
                return
        
        # 引擎已初始化，开始识别
        self._start_recognition()
    
    def _start_recognition(self):
        """启动识别工作线程"""
        self._is_recognizing = True
        self.set_status("🔄 正在识别文字...")
        self._recognize_btn.setText("识别中...")
        self._recognize_btn.setEnabled(False)
        
        self.recognition_started.emit()
        
        # 创建并启动工作线程
        self._worker = OCRWorker(
            self._question_service, 
            self._current_image_path
        )
        self._worker.finished.connect(self._on_recognition_finished)
        self._worker.start()
    
    def _on_recognition_finished(self, success: bool, message: str, text: str):
        """OCR识别完成回调"""
        self._is_recognizing = False
        
        if success and text:
            # 识别成功
            line_count = len(text.splitlines())
            self.set_status(f"✅ 识别成功 ({line_count} 行)")
            self._recognize_btn.setText("✅ 识别完成")
            self._recognize_btn.setEnabled(True)
            self.recognition_completed.emit(text)
        else:
            # 识别失败
            self.set_status("❌ 识别失败")
            self._recognize_btn.setText("🔄 重新识别")
            self._recognize_btn.setEnabled(True)
            self.recognition_failed.emit(message)
