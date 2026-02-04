"""测试添加对话框前端"""

import sys
from pathlib import Path

# 添加src到路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("添加对话框前端测试")
print("=" * 60)

# 步骤1: 导入必要的模块
print("\n[步骤1] 导入模块...")
try:
    # 必须先导入torch（避免DLL冲突）
    import os
    os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
    
    import torch  # 先导入torch
    
    from PyQt6.QtWidgets import QApplication
    from mistake_book.ui.dialogs.add_dialog import AddQuestionDialog
    from mistake_book.services.ocr_engine import create_ocr_engine
    from mistake_book.services.question_service import QuestionService
    from mistake_book.core.data_manager import DataManager
    from mistake_book.database.db_manager import DatabaseManager
    from mistake_book.config.paths import get_app_paths
    print("   ✅ 模块导入成功")
except Exception as e:
    print(f"   ❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤2: 创建QApplication
print("\n[步骤2] 创建QApplication...")
try:
    app = QApplication(sys.argv)
    print("   ✅ QApplication创建成功")
except Exception as e:
    print(f"   ❌ 创建失败: {e}")
    sys.exit(1)

# 步骤3: 初始化服务
print("\n[步骤3] 初始化服务...")
try:
    paths = get_app_paths()
    db_manager = DatabaseManager(paths.database_file)
    data_manager = DataManager(db_manager)
    ocr_engine = create_ocr_engine(async_init=False)
    question_service = QuestionService(data_manager, ocr_engine)
    print("   ✅ 服务初始化成功")
    print(f"   - OCR引擎: {ocr_engine}")
    print(f"   - QuestionService: {question_service}")
except Exception as e:
    print(f"   ❌ 服务初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤4: 创建对话框
print("\n[步骤4] 创建添加对话框...")
try:
    dialog = AddQuestionDialog(question_service)
    print("   ✅ 对话框创建成功")
    print(f"   - 对话框标题: {dialog.windowTitle()}")
    print(f"   - 对话框大小: {dialog.size()}")
    print(f"   - drop_zone: {dialog.drop_zone}")
    print(f"   - ocr_btn: {dialog.ocr_btn}")
except Exception as e:
    print(f"   ❌ 对话框创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤5: 检查对话框组件
print("\n[步骤5] 检查对话框组件...")
try:
    print(f"   - DropZone label: {dialog.drop_zone.label.text()}")
    print(f"   - DropZone upload_btn: {dialog.drop_zone.upload_btn.text()}")
    print(f"   - OCR按钮状态: {'启用' if dialog.ocr_btn.isEnabled() else '禁用'}")
    print(f"   - OCR按钮文本: {dialog.ocr_btn.text()}")
    print("   ✅ 组件检查完成")
except Exception as e:
    print(f"   ❌ 组件检查失败: {e}")
    import traceback
    traceback.print_exc()

# 步骤6: 测试图片加载（如果有测试图片）
print("\n[步骤6] 测试图片加载...")
test_image = project_root / "test_image.png"
if test_image.exists():
    print(f"   找到测试图片: {test_image}")
    try:
        dialog.drop_zone.load_image(str(test_image))
        print(f"   ✅ 图片加载成功")
        print(f"   - current_image_path: {dialog.drop_zone.current_image_path}")
        print(f"   - label文本: {dialog.drop_zone.label.text()}")
    except Exception as e:
        print(f"   ❌ 图片加载失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ⚠️  未找到测试图片: {test_image}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n提示: 可以运行 dialog.show() 来显示对话框")
print("      但这会阻塞脚本，所以这里不自动显示")
