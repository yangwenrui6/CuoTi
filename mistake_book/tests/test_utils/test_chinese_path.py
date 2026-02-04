"""测试中文路径的OCR识别"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "mistake_book" / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("测试中文路径的OCR识别")
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

# 导入OCR引擎
from mistake_book.services.ocr_engine import OCREngineFactory

print("\n[步骤1] 创建OCR引擎...")
engine = OCREngineFactory.create_engine(prefer_engine="easyocr")

if not engine or not engine.is_available():
    print("❌ OCR引擎不可用")
    sys.exit(1)

print(f"✅ OCR引擎创建成功: {engine.__class__.__name__}")

# 测试中文路径
print("\n[步骤2] 测试中文路径识别...")
test_path = Path(r"C:\Users\Lenovo\Desktop\微信图片_20260203111314_1079_272.png")

if not test_path.exists():
    print(f"⚠️  测试文件不存在: {test_path}")
    print("请提供一个存在的图片路径进行测试")
    sys.exit(0)

print(f"测试文件: {test_path}")
print(f"文件存在: {test_path.exists()}")

try:
    print("\n开始识别...")
    result = engine.recognize(test_path)
    print(f"\n✅ 识别成功！")
    print(f"识别结果:\n{result}")
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
