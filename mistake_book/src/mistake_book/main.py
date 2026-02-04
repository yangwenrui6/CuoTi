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
from mistake_book.ui.main_window import MainWindow
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
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
