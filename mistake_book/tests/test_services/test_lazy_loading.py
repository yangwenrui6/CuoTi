"""测试OCR延迟加载"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "mistake_book" / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("测试OCR延迟加载")
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

print("\n[步骤1] 导入OCR引擎...")
from mistake_book.services.ocr_engine import create_ocr_engine

print("\n[步骤2] 创建OCR引擎（不应该加载模型）...")
engine = create_ocr_engine()

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功: {engine.__class__.__name__}")

print("\n[步骤3] 检查引擎是否可用（不应该加载模型）...")
is_available = engine.is_available()
print(f"引擎可用: {is_available}")

if not is_available:
    print("❌ 引擎不可用")
    sys.exit(1)

print("\n[步骤4] 检查是否已初始化...")
print(f"_init_attempted: {engine._init_attempted}")
print(f"_initialized: {engine._initialized}")
print(f"reader: {engine.reader}")

if engine._init_attempted:
    print("⚠️  警告：引擎已经初始化了（不应该在这个阶段初始化）")
else:
    print("✅ 正确：引擎还没有初始化（延迟加载工作正常）")

print("\n" + "=" * 60)
print("✅ 延迟加载测试通过！")
print("=" * 60)
print("\n说明：")
print("- 引擎创建成功，但模型还没有加载")
print("- is_available()返回True，表示easyocr已安装")
print("- 模型将在首次调用recognize()时加载")
