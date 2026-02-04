"""测试OCR后台线程执行"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

print("测试OCR后台线程执行")
print("=" * 60)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from mistake_book.services.question_service import QuestionService
from mistake_book.database.db_manager import DatabaseManager
from PIL import Image, ImageDraw, ImageFont
import time

# 创建测试图片
print("\n[1] 创建测试图片...")
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 36)
except:
    font = ImageFont.load_default()
draw.text((50, 30), "测试文字", fill='black', font=font)
test_image = project_root / "test_thread.png"
img.save(test_image)
print(f"✅ 测试图片已创建: {test_image}")

# 创建应用
app = QApplication(sys.argv)

# 初始化服务
print("\n[2] 初始化服务...")
db_manager = DatabaseManager()
question_service = QuestionService(db_manager)
print("✅ 服务初始化完成")

# 测试后台线程执行
print("\n[3] 测试后台线程OCR识别...")

class OCRWorker(QThread):
    """OCR识别工作线程"""
    finished = pyqtSignal(bool, str, str)
    
    def __init__(self, question_service, image_path):
        super().__init__()
        self.question_service = question_service
        self.image_path = image_path
    
    def run(self):
        """在后台线程中执行OCR识别"""
        print("   [线程] 开始OCR识别...")
        start_time = time.time()
        
        try:
            success, message, recognized_text = self.question_service.recognize_image_with_retry(
                Path(self.image_path)
            )
            
            elapsed = time.time() - start_time
            print(f"   [线程] OCR识别完成，耗时: {elapsed:.2f}秒")
            
            self.finished.emit(success, message, recognized_text or "")
        except Exception as e:
            print(f"   [线程] OCR识别失败: {e}")
            self.finished.emit(False, f"识别出错：{str(e)}", "")

def on_finished(success, message, text):
    """识别完成回调"""
    print("\n[4] 识别结果:")
    print(f"   成功: {success}")
    print(f"   消息: {message}")
    if text:
        print(f"   文字: {text}")
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("✅ OCR识别在后台线程中执行，不会阻塞UI")
    app.quit()

# 创建并启动工作线程
worker = OCRWorker(question_service, test_image)
worker.finished.connect(on_finished)

print("   启动后台线程...")
worker.start()

print("   ✅ 主线程继续运行，UI不会被阻塞")
print("   ⏳ 等待后台线程完成...")

# 运行应用
sys.exit(app.exec())
