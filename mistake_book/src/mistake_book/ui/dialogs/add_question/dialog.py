"""添加错题对话框 - UI组装器"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from mistake_book.ui.components import ImageUploader, OCRPanel, QuestionForm


class AddQuestionDialog(QDialog):
    """添加错题对话框 - 使用可复用组件"""
    
    def __init__(self, controller, parent=None):
        """
        初始化对话框
        
        Args:
            controller: AddQuestionController实例
        """
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("➕ 添加错题")
        self.setMinimumSize(800, 700)
        
        # 创建组件
        self.image_uploader = ImageUploader()
        self.ocr_panel = OCRPanel(controller.question_service)
        self.question_form = QuestionForm()
        
        self._init_ui()
        self._connect_signals()
        
        # 更新OCR状态提示
        self._update_ocr_hint()
    
    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 滚动区域内容容器
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        
        # 图片上传区域
        upload_group = QGroupBox("📷 图片上传")
        upload_layout = QVBoxLayout()
        upload_layout.addWidget(self.image_uploader)
        upload_layout.addWidget(self.ocr_panel)
        upload_group.setLayout(upload_layout)
        content_layout.addWidget(upload_group)
        
        # 表单区域
        form_group = QGroupBox("📝 题目信息")
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.question_form)
        form_group.setLayout(form_layout)
        content_layout.addWidget(form_group)
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 按钮（固定在底部，不滚动）
        self._add_buttons(main_layout)
    
    def _add_buttons(self, layout):
        """添加底部按钮"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        # 保存按钮
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save_clicked)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 图片选择 -> 控制器处理 -> OCR识别
        self.image_uploader.image_selected.connect(
            self._on_image_selected
        )
        
        # OCR完成 -> 填充表单
        self.ocr_panel.recognition_completed.connect(
            self._on_ocr_completed
        )
        
        # OCR失败 -> 显示提示
        self.ocr_panel.recognition_failed.connect(
            self._on_ocr_failed
        )
    
    def _on_image_selected(self, image_path: str):
        """图片选择事件"""
        # 通知控制器
        self.controller.on_image_selected(image_path)
        
        # 触发OCR识别
        self.ocr_panel.recognize_image(image_path)
    
    def _on_ocr_completed(self, text: str):
        """OCR识别完成"""
        # 通过控制器处理文本
        processed_text = self.controller.on_ocr_completed(text)
        
        # 填充到表单
        self.question_form.set_content(processed_text)
        
        # 聚焦到题目内容，方便用户编辑
        self.question_form.focus_content()
    
    def _on_ocr_failed(self, message: str):
        """OCR识别失败"""
        # 如果是严重错误，显示对话框
        if "下载模型" in message or "网络" in message:
            QMessageBox.warning(
                self, 
                "OCR初始化提示", 
                f"{message}\n\n"
                "提示：\n"
                "• 首次使用需要下载模型文件（约100-200MB）\n"
                "• 请确保网络连接稳定\n"
                "• 下载完成后会自动保存，下次使用不需要重新下载\n\n"
                "如果下载失败，请检查网络连接后重试。"
            )
    
    def _on_save_clicked(self):
        """保存按钮点击"""
        # 禁用保存按钮，防止重复点击
        self.save_btn.setEnabled(False)
        self.save_btn.setText("保存中...")
        
        try:
            # 验证表单
            valid, error_msg = self.question_form.validate()
            if not valid:
                QMessageBox.warning(self, "验证失败", error_msg)
                return
            
            # 获取表单数据
            data = self.question_form.get_data()
            data['image_path'] = self.image_uploader.get_image_path()
            
            # 调用控制器保存
            success, message = self.controller.save_question(data)
            
            if success:
                # 保存成功，关闭对话框
                self.accept()
            else:
                # 保存失败，显示错误
                QMessageBox.warning(self, "保存失败", message)
                
        finally:
            # 恢复按钮状态
            self.save_btn.setEnabled(True)
            self.save_btn.setText("💾 保存")
    
    def _update_ocr_hint(self):
        """更新OCR状态提示"""
        if not self.controller.question_service.ocr_engine:
            # OCR不可用
            self.image_uploader.set_hint_text(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "⚠️ OCR功能未启用"
            )
            return
        
        # 检查OCR是否正在初始化
        ocr_engine = self.controller.question_service.ocr_engine
        if hasattr(ocr_engine, 'is_initializing') and ocr_engine.is_initializing():
            # 正在下载模型
            self.image_uploader.set_hint_text(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "⏳ OCR模型正在后台下载中...\n"
                "（首次使用需要几分钟）"
            )
        elif hasattr(ocr_engine, '_initialized') and ocr_engine._initialized:
            # 已加载完成
            self.image_uploader.set_hint_text(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "✅ 自动识别文字到题目内容"
            )
        else:
            # 默认提示
            self.image_uploader.set_hint_text(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "自动识别文字到题目内容"
            )
