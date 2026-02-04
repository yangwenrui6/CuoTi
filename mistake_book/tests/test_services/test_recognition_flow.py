"""测试OCR识别完整流程"""

import sys
from pathlib import Path

# 添加src到路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("OCR识别流程测试")
print("=" * 60)

# 步骤1: 导入必要的模块
print("\n[步骤1] 导入模块...")
try:
    from mistake_book.services.ocr_engine import create_ocr_engine
    from mistake_book.services.question_service import QuestionService
    from mistake_book.core.data_manager import DataManager
    from mistake_book.database.db_manager import DatabaseManager
    from mistake_book.config.paths import get_app_paths
    print("   ✅ 模块导入成功")
except Exception as e:
    print(f"   ❌ 模块导入失败: {e}")
    sys.exit(1)

# 步骤2: 创建OCR引擎
print("\n[步骤2] 创建OCR引擎...")
try:
    engine = create_ocr_engine(async_init=False)
    if engine:
        print(f"   ✅ OCR引擎创建成功: {type(engine).__name__}")
        print(f"   ✅ 引擎可用性: {engine.is_available()}")
    else:
        print("   ❌ OCR引擎创建失败")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤3: 初始化服务
print("\n[步骤3] 初始化服务...")
try:
    paths = get_app_paths()
    db_manager = DatabaseManager(paths.database_file)
    data_manager = DataManager(db_manager)
    question_service = QuestionService(data_manager, engine)
    print("   ✅ 服务初始化成功")
    print(f"   - QuestionService.ocr_engine: {question_service.ocr_engine}")
    print(f"   - OCR引擎可用: {question_service.ocr_engine.is_available() if question_service.ocr_engine else False}")
except Exception as e:
    print(f"   ❌ 服务初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤4: 检查OCR引擎状态
print("\n[步骤4] 检查OCR引擎详细状态...")
try:
    print(f"   - _init_attempted: {engine._init_attempted}")
    print(f"   - _initialized: {engine._initialized}")
    print(f"   - reader: {engine.reader}")
    print(f"   - is_available(): {engine.is_available()}")
    
    if hasattr(engine, 'is_initializing'):
        print(f"   - is_initializing(): {engine.is_initializing()}")
except Exception as e:
    print(f"   ⚠️  状态检查出错: {e}")

# 步骤5: 测试识别（如果有测试图片）
print("\n[步骤5] 测试识别功能...")
test_image = project_root / "test_image.png"
if test_image.exists():
    print(f"   找到测试图片: {test_image}")
    try:
        success, message, text = question_service.recognize_image_with_retry(test_image)
        print(f"   识别结果:")
        print(f"   - 成功: {success}")
        print(f"   - 消息: {message}")
        print(f"   - 文本: {text[:100] if text else None}...")
    except Exception as e:
        print(f"   ❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ⚠️  未找到测试图片: {test_image}")
    print("   提示: 可以放一张图片到项目根目录命名为 test_image.png 进行测试")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
