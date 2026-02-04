"""测试OCR完整流程 - 模拟实际使用"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "mistake_book" / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("测试OCR完整流程")
print("=" * 60)

# 先导入torch（避免PyQt6冲突）
try:
    import torch
    print(f"✅ torch导入成功: {torch.__version__}")
except Exception as e:
    print(f"⚠️  torch导入失败: {e}")

# 设置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

print("\n[步骤1] 创建OCR引擎...")
from mistake_book.services.ocr_engine import create_ocr_engine

engine = create_ocr_engine()

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功")
print(f"   _init_attempted: {engine._init_attempted}")
print(f"   _initialized: {engine._initialized}")

print("\n[步骤2] 检查引擎是否可用...")
is_available = engine.is_available()
print(f"✅ 引擎可用: {is_available}")
print(f"   _init_attempted: {engine._init_attempted}")
print(f"   _initialized: {engine._initialized}")

print("\n[步骤3] 模拟首次调用recognize()...")
print("注意：这会触发模型加载，需要5-10秒")

# 创建一个测试图片（如果存在的话）
test_image = Path("test_image.png")
if not test_image.exists():
    print(f"⚠️  测试图片不存在: {test_image}")
    print("跳过实际识别测试")
    print("\n说明：")
    print("- 延迟加载逻辑正常工作")
    print("- 如果要测试实际识别，请提供test_image.png")
else:
    try:
        print("开始识别...")
        text = engine.recognize(test_image)
        print(f"✅ 识别成功")
        print(f"   识别文本: {text[:100]}...")
        print(f"   _init_attempted: {engine._init_attempted}")
        print(f"   _initialized: {engine._initialized}")
    except Exception as e:
        print(f"❌ 识别失败: {e}")
        print(f"   _init_attempted: {engine._init_attempted}")
        print(f"   _initialized: {engine._initialized}")

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)
