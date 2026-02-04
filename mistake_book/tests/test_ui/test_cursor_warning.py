"""测试cursor警告是否修复"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "mistake_book" / "src"
sys.path.insert(0, str(src_path))

print("测试cursor警告修复...")

# 先导入torch
try:
    import torch
except:
    pass

from PyQt6.QtWidgets import QApplication
from mistake_book.ui.dialogs.add_dialog import DropZoneWidget

app = QApplication(sys.argv)

# 创建DropZoneWidget
widget = DropZoneWidget()
widget.show()

print("✅ DropZoneWidget创建成功")
print("如果没有看到 'Unknown property cursor' 警告，说明修复成功")

# 不进入事件循环，直接退出
app.quit()
