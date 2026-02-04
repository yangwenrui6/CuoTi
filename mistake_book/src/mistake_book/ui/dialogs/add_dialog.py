"""添加错题对话框 - 支持拖拽、OCR识别"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QGroupBox, QWidget,
    QScrollArea, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from pathlib import Path
from typing import Optional


class DropZoneWidget(QWidget):
    """拖拽区域组件 - 支持拖拽和点击上传"""
    
    image_dropped = pyqtSignal(str)  # 图片路径信号
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(250)
        self.setStyleSheet("""
            DropZoneWidget {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
            DropZoneWidget:hover {
                background-color: #d5dbdb;
            }
        """)
        
        # 设置鼠标指针为手型（使用Qt的方式）
        from PyQt6.QtCore import Qt
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        
        # 提示文字
        self.label = QLabel("📸 拖拽图片到此处\n或点击上传图片\n自动识别文字到题目内容")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 14pt; color: #7f8c8d;")
        layout.addWidget(self.label)
        
        # 上传按钮
        self.upload_btn = QPushButton("📁 选择图片")
        self.upload_btn.setStyleSheet("""
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
        self.upload_btn.clicked.connect(self.select_image)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 图片预览
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setVisible(False)
        self.image_label.setStyleSheet("border: 1px solid #bdc3c7; background-color: white;")
        self.image_label.setMaximumHeight(300)
        layout.addWidget(self.image_label)
        
        # 查看大图按钮
        self.view_btn = QPushButton("🔍 查看大图")
        self.view_btn.setVisible(False)
        self.view_btn.clicked.connect(self.view_full_image)
        layout.addWidget(self.view_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.current_image_path = None
    
    def mousePressEvent(self, event):
        """点击区域触发上传"""
        if not self.image_label.isVisible():
            self.select_image()
    
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )
        
        if file_path:
            # 先尝试加载图片
            self.load_image(file_path)
            # 只有加载成功才发送信号
            if self.current_image_path:
                self.image_dropped.emit(file_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # 先尝试加载图片
                self.load_image(file_path)
                # 只有加载成功才发送信号
                if self.current_image_path:
                    self.image_dropped.emit(file_path)
            else:
                self.label.setText("❌ 不支持的文件格式\n请选择图片文件")
    
    def load_image(self, path: str):
        """加载图片预览"""
        try:
            self.current_image_path = path
            
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
            q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            # 转换为QPixmap
            pixmap = QPixmap.fromImage(q_image)
            
            # 缩放图片以适应预览区域
            scaled = pixmap.scaled(
                400, 280, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled)
            self.image_label.setVisible(True)
            self.view_btn.setVisible(True)
            self.label.setText("✅ 图片已加载")
            self.upload_btn.setText("📁 更换图片")
            
        except Exception as e:
            # 图片加载失败
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"图片加载失败: {e}")
            
            self.label.setText(f"❌ 图片加载失败\n{str(e)}")
            self.current_image_path = None
    
    def view_full_image(self):
        """查看完整图片"""
        if self.current_image_path:
            from mistake_book.ui.dialogs.image_viewer import ImageViewerDialog
            viewer = ImageViewerDialog(self.current_image_path, self)
            viewer.exec()


class TagSelector(QWidget):
    """标签选择器（带搜索）"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索或添加标签...")
        layout.addWidget(self.search_input)
        
        # 已选标签显示区
        self.selected_tags_label = QLabel("已选标签: 无")
        self.selected_tags_label.setWordWrap(True)
        layout.addWidget(self.selected_tags_label)
        
        self.selected_tags = []
    
    def get_tags(self):
        """获取选中的标签"""
        return self.selected_tags


class AddQuestionDialog(QDialog):
    """添加错题对话框 - 支持OCR和拖拽"""
    
    def __init__(self, question_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ 添加错题")
        self.setMinimumSize(800, 700)
        self.image_path = None
        
        # 注入服务
        self.question_service = question_service
        
        self.init_ui()
        
        # 检查OCR状态并更新提示
        self.update_ocr_status_hint()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 拖拽区域
        drop_group = QGroupBox("📷 图片上传")
        drop_layout = QVBoxLayout()
        
        self.drop_zone = DropZoneWidget()
        self.drop_zone.image_dropped.connect(self.on_image_dropped)
        drop_layout.addWidget(self.drop_zone)
        
        # OCR按钮 (用于重新识别)
        ocr_btn_layout = QHBoxLayout()
        self.ocr_btn = QPushButton("� 重新识别")
        self.ocr_btn.setEnabled(False)
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.ocr_btn.setToolTip("拖拽图片后会自动识别,点击此按钮可重新识别")
        ocr_btn_layout.addStretch()
        ocr_btn_layout.addWidget(self.ocr_btn)
        drop_layout.addLayout(ocr_btn_layout)
        
        drop_group.setLayout(drop_layout)
        layout.addWidget(drop_group)
        
        # 表单区域
        form_group = QGroupBox("📝 题目信息")
        form_layout = QVBoxLayout()
        
        # 科目
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("科目:"))
        self.subject_combo = QComboBox()
        self.subject_combo.addItems(["数学", "物理", "化学", "英语", "语文", "其他"])
        subject_layout.addWidget(self.subject_combo)
        form_layout.addLayout(subject_layout)
        
        # 题型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("题型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["单选题", "多选题", "填空题", "简答题", "计算题", "其他"])
        type_layout.addWidget(self.type_combo)
        form_layout.addLayout(type_layout)
        
        # 题目内容
        form_layout.addWidget(QLabel("题目内容:"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("输入题目内容...")
        self.content_edit.setMinimumHeight(100)
        form_layout.addWidget(self.content_edit)
        
        # 我的答案
        form_layout.addWidget(QLabel("我的答案:"))
        self.my_answer_edit = QTextEdit()
        self.my_answer_edit.setPlaceholderText("输入你的答案...")
        self.my_answer_edit.setMaximumHeight(60)
        form_layout.addWidget(self.my_answer_edit)
        
        # 正确答案
        form_layout.addWidget(QLabel("正确答案:"))
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("输入正确答案...")
        self.answer_edit.setMaximumHeight(60)
        form_layout.addWidget(self.answer_edit)
        
        # 解析
        form_layout.addWidget(QLabel("解析:"))
        self.explanation_edit = QTextEdit()
        self.explanation_edit.setPlaceholderText("输入解析...")
        self.explanation_edit.setMaximumHeight(80)
        form_layout.addWidget(self.explanation_edit)
        
        # 难度
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("难度:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["1星 ⭐", "2星 ⭐⭐", "3星 ⭐⭐⭐", "4星 ⭐⭐⭐⭐", "5星 ⭐⭐⭐⭐⭐"])
        self.difficulty_combo.setCurrentIndex(2)
        difficulty_layout.addWidget(self.difficulty_combo)
        form_layout.addLayout(difficulty_layout)
        
        # 标签选择器
        form_layout.addWidget(QLabel("标签:"))
        self.tag_selector = TagSelector()
        form_layout.addWidget(self.tag_selector)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_question)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def on_image_dropped(self, path: str):
        """图片拖拽事件 - 自动触发OCR识别"""
        self.image_path = path
        self.ocr_btn.setEnabled(True)
        
        # 只有在图片成功加载后才触发OCR识别
        # load_image会设置current_image_path，如果加载失败会设为None
        # 使用QTimer延迟检查，确保load_image已执行完毕
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(200, self._check_and_run_ocr)
    
    def _check_and_run_ocr(self):
        """检查图片是否加载成功，然后运行OCR"""
        if self.drop_zone.current_image_path:
            # 图片加载成功，触发OCR
            self.auto_run_ocr()
        else:
            # 图片加载失败，不触发OCR
            self.ocr_btn.setEnabled(False)
    
    def auto_run_ocr(self):
        """自动运行OCR识别 - 拖拽图片后自动触发"""
        if not self.image_path:
            return
        
        # 检查OCR引擎是否可用
        if not self.question_service.ocr_engine:
            self.drop_zone.label.setText("⚠️ OCR功能未启用\n请安装 paddleocr 或 pytesseract")
            return
        
        if not self.question_service.ocr_engine.is_available():
            self.drop_zone.label.setText("⚠️ OCR引擎不可用")
            return
        
        # 更新UI状态
        self.drop_zone.label.setText("🔄 正在识别文字...")
        self.ocr_btn.setText("识别中...")
        self.ocr_btn.setEnabled(False)
        
        # 使用QTimer延迟执行,避免阻塞UI
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._do_ocr_recognition)
    
    def _do_ocr_recognition(self):
        """执行OCR识别"""
        # 检查OCR引擎是否已初始化
        ocr_engine = self.question_service.ocr_engine
        
        # 如果引擎还没有初始化（reader为None），需要等待初始化
        if not ocr_engine._initialized:
            # 检查是否正在初始化
            if ocr_engine.is_initializing():
                # 正在后台初始化
                self.drop_zone.label.setText("⏳ OCR模型正在后台加载中...\n请稍候片刻")
                self.ocr_btn.setText("⏳ 加载中...")
                
                # 显示提示
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "OCR模型加载中",
                    "OCR模型正在后台下载和加载中（首次使用需要几分钟）\n\n"
                    "您可以选择：\n"
                    "• 等待加载完成后自动识别\n"
                    "• 取消并稍后重试\n\n"
                    "是否等待加载完成？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    self.drop_zone.label.setText("⚠️ 已取消，请稍后重试")
                    self.ocr_btn.setText("🔄 重新识别")
                    self.ocr_btn.setEnabled(True)
                    return
                
                # 等待初始化完成
                self.drop_zone.label.setText("⏳ 等待模型加载完成...")
                from PyQt6.QtCore import QTimer
                
                def check_init_status():
                    if ocr_engine._initialized:
                        # 初始化完成，开始识别
                        self.drop_zone.label.setText("🔄 正在识别文字...")
                        QTimer.singleShot(100, self._do_actual_recognition)
                    elif not ocr_engine.is_initializing():
                        # 初始化失败
                        self.drop_zone.label.setText("❌ 模型加载失败")
                        self.ocr_btn.setText("🔄 重新识别")
                        self.ocr_btn.setEnabled(True)
                    else:
                        # 继续等待
                        QTimer.singleShot(1000, check_init_status)
                
                QTimer.singleShot(1000, check_init_status)
                return
            else:
                # 还没开始初始化，提示用户等待后台加载
                self.drop_zone.label.setText("⏳ OCR模型正在后台加载中...\n请稍候片刻")
                self.ocr_btn.setText("⏳ 加载中...")
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "OCR模型加载中",
                    "OCR模型正在后台下载和加载中（首次使用需要几分钟）\n\n"
                    "请稍候片刻后重试，或等待状态栏显示\"OCR模型加载完成\"。"
                )
                
                self.drop_zone.label.setText("⚠️ 请稍后重试")
                self.ocr_btn.setText("🔄 重新识别")
                self.ocr_btn.setEnabled(True)
                return
        
        # 引擎已初始化，直接识别
        self._do_actual_recognition()
    
    def _do_actual_recognition(self):
        """实际执行OCR识别 - 在后台线程中执行"""
        from PyQt6.QtCore import QThread, pyqtSignal
        
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
                    success, message, recognized_text = self.question_service.recognize_image_with_retry(
                        Path(self.image_path)
                    )
                    self.finished.emit(success, message, recognized_text or "")
                except Exception as e:
                    self.finished.emit(False, f"识别出错：{str(e)}", "")
        
        # 创建并启动工作线程
        self.ocr_worker = OCRWorker(self.question_service, self.image_path)
        self.ocr_worker.finished.connect(self._on_ocr_finished)
        self.ocr_worker.start()
    
    def _on_ocr_finished(self, success: bool, message: str, recognized_text: str):
        """OCR识别完成回调"""
        try:
            if success and recognized_text:
                # 自动填充到题目内容
                self.content_edit.setPlainText(recognized_text)
                
                # 更新UI状态
                self.drop_zone.label.setText(f"✅ 识别成功 ({len(recognized_text.splitlines())} 行)")
                self.ocr_btn.setText("✅ 识别完成")
                
                # 自动聚焦到题目内容,方便用户编辑
                self.content_edit.setFocus()
            else:
                # 识别失败
                self.drop_zone.label.setText("❌ 识别失败,可手动输入")
                self.ocr_btn.setText("🔄 重新识别")
                
                # 显示详细错误
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
                else:
                    # 其他错误，不强制弹窗
                    pass
        except Exception as e:
            # 未预期的错误
            self.drop_zone.label.setText("❌ 识别失败")
            self.ocr_btn.setText("🔄 重新识别")
            QMessageBox.warning(self, "错误", f"OCR识别出错：{str(e)}")
        finally:
            self.ocr_btn.setEnabled(True)
    
    def run_ocr(self):
        """手动运行OCR识别 - 点击按钮触发，在后台线程执行"""
        if not self.image_path:
            return
        
        self.ocr_btn.setText("识别中...")
        self.ocr_btn.setEnabled(False)
        self.drop_zone.label.setText("🔄 正在识别文字...")
        
        # 使用后台线程执行OCR识别
        from PyQt6.QtCore import QThread, pyqtSignal
        
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
                    success, message, recognized_text = self.question_service.recognize_image_with_retry(
                        Path(self.image_path)
                    )
                    self.finished.emit(success, message, recognized_text or "")
                except Exception as e:
                    self.finished.emit(False, f"识别出错：{str(e)}", "")
        
        # 创建并启动工作线程
        self.manual_ocr_worker = OCRWorker(self.question_service, self.image_path)
        self.manual_ocr_worker.finished.connect(self._on_manual_ocr_finished)
        self.manual_ocr_worker.start()
    
    def _on_manual_ocr_finished(self, success: bool, message: str, recognized_text: str):
        """手动OCR识别完成回调"""
        if success and recognized_text:
            self.content_edit.setPlainText(recognized_text)
            self.ocr_btn.setText("✅ 识别完成")
            self.drop_zone.label.setText(f"✅ 识别成功 ({len(recognized_text.splitlines())} 行)")
            QMessageBox.information(self, "OCR识别", f"识别成功!\n\n共识别 {len(recognized_text.splitlines())} 行文字")
        else:
            self.ocr_btn.setText("❌ 识别失败")
            self.drop_zone.label.setText("❌ 识别失败,可手动输入")
            QMessageBox.warning(self, "OCR识别失败", message)
        
        self.ocr_btn.setEnabled(True)
    
    def save_question(self):
        """保存错题"""
        # 禁用保存按钮,防止重复点击
        self.save_btn.setEnabled(False)
        self.save_btn.setText("保存中...")
        
        # 收集数据
        question_data = {
            "subject": self.subject_combo.currentText(),
            "question_type": self.type_combo.currentText(),
            "content": self.content_edit.toPlainText().strip(),
            "my_answer": self.my_answer_edit.toPlainText().strip(),
            "answer": self.answer_edit.toPlainText().strip(),
            "explanation": self.explanation_edit.toPlainText().strip(),
            "difficulty": self.difficulty_combo.currentIndex() + 1,
            "image_path": self.image_path
        }
        
        # 验证必填字段
        if not question_data["content"]:
            QMessageBox.warning(self, "验证失败", "题目内容不能为空")
            # 恢复按钮状态
            self.save_btn.setEnabled(True)
            self.save_btn.setText("💾 保存")
            return
        
        if not question_data["answer"]:
            QMessageBox.warning(self, "验证失败", "正确答案不能为空")
            # 恢复按钮状态
            self.save_btn.setEnabled(True)
            self.save_btn.setText("💾 保存")
            return
        
        # 调用服务层保存
        success, message, question_id = self.question_service.create_question(question_data)
        
        if success:
            # 保存成功,关闭对话框
            self.accept()
        else:
            # 保存失败,显示错误并恢复按钮
            QMessageBox.warning(self, "保存失败", message)
            self.save_btn.setEnabled(True)
            self.save_btn.setText("💾 保存")

    
    def update_ocr_status_hint(self):
        """更新OCR状态提示"""
        if not self.question_service.ocr_engine:
            # OCR不可用
            self.drop_zone.label.setText(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "⚠️ OCR功能未启用"
            )
            return
        
        # 检查OCR是否正在初始化
        if hasattr(self.question_service.ocr_engine, 'is_initializing') and \
           self.question_service.ocr_engine.is_initializing():
            # 正在下载模型
            self.drop_zone.label.setText(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "⏳ OCR模型正在后台下载中...\n"
                "（首次使用需要几分钟）"
            )
        elif hasattr(self.question_service.ocr_engine, '_initialized') and \
             self.question_service.ocr_engine._initialized:
            # 已加载完成
            self.drop_zone.label.setText(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "✅ 自动识别文字到题目内容"
            )
        else:
            # 默认提示
            self.drop_zone.label.setText(
                "📸 拖拽图片到此处\n或点击上传图片\n"
                "自动识别文字到题目内容"
            )
