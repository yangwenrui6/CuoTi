"""QApplication入口 + 全局异常捕获"""

import sys
import os

# ===== 配置模型存储路径（在导入任何库之前） =====
# 将EasyOCR模型和PyTorch缓存移到D盘，节省C盘空间
# 如果你想使用其他盘，修改下面的路径即可
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
os.environ['TORCH_HOME'] = 'D:/PyTorch'

# 禁用PyTorch的pin_memory警告（因为我们使用CPU模式）
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# 设置PyTorch使用CPU（避免GPU相关警告）
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*pin_memory.*')

# 重要：在导入PyQt6之前先导入torch
# 这可以避免PyQt6和torch的DLL冲突问题
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
except Exception:
    _TORCH_AVAILABLE = False

from PyQt6.QtWidgets import QApplication
from mistake_book.config.paths import get_app_paths
from mistake_book.database.db_manager import DatabaseManager
from mistake_book.core.data_manager import DataManager
from mistake_book.core.review_scheduler import ReviewScheduler
from mistake_book.services import QuestionService, ReviewService, UIService
from mistake_book.ui.main_window.window import MainWindow
from mistake_book.ui.main_window.controller import MainWindowController
from mistake_book.ui.factories.dialog_factory import DialogFactory
from mistake_book.ui.events.event_bus import EventBus
from mistake_book.utils.logger import setup_logger

logger = setup_logger()


def exception_hook(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))


def main():
    """应用程序入口"""
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    app.setApplicationName("错题本")
    app.setOrganizationName("MistakeBook")
    
    # 初始化数据层
    paths = get_app_paths()
    db_manager = DatabaseManager(paths.database_file)
    data_manager = DataManager(db_manager)
    scheduler = ReviewScheduler()
    
    # 初始化服务层
    # OCR引擎将在后台异步初始化，不阻塞UI
    from mistake_book.services.ocr_engine import create_ocr_engine
    ocr_engine = create_ocr_engine(async_init=True)
    question_service = QuestionService(data_manager, ocr_engine)
    review_service = ReviewService(data_manager, scheduler)
    ui_service = UIService(data_manager)
    
    services = {
        'question_service': question_service,
        'review_service': review_service,
        'ui_service': ui_service
    }
    
    # 创建事件总线
    event_bus = EventBus()
    
    # 创建对话框工厂
    dialog_factory = DialogFactory(services, event_bus)
    
    # 创建主窗口控制器
    controller = MainWindowController(services, dialog_factory, event_bus)
    
    # 创建主窗口
    window = MainWindow(controller)
    window.show()
    
    logger.info("应用程序启动成功")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
