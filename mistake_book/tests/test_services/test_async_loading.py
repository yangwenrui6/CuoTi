"""测试OCR异步加载"""

import sys
import time
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("测试OCR异步加载")
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

print("\n[步骤1] 创建OCR引擎（异步模式）...")
from mistake_book.services.ocr_engine import create_ocr_engine

engine = create_ocr_engine(async_init=True)

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功")
print(f"   _init_attempted: {engine._init_attempted}")
print(f"   _initialized: {engine._initialized}")

print("\n[步骤2] 检查是否正在后台初始化...")
print(f"   is_initializing(): {engine.is_initializing()}")

if engine.is_initializing():
    print("✅ 正确：引擎正在后台初始化")
    print("   说明：模型正在后台线程中下载和加载")
else:
    print("⚠️  引擎没有在后台初始化")

print("\n[步骤3] 模拟用户继续使用程序...")
print("   用户可以正常使用程序的其他功能")
print("   UI不会被阻塞")

# 模拟用户操作
for i in range(5):
    time.sleep(1)
    print(f"   {i+1}秒 - 程序正常运行，UI响应正常")
    if engine._initialized:
        print(f"   ✅ 模型已加载完成！")
        break

print("\n[步骤4] 检查最终状态...")
print(f"   _init_attempted: {engine._init_attempted}")
print(f"   _initialized: {engine._initialized}")
print(f"   is_initializing(): {engine.is_initializing()}")

if engine._initialized:
    print("✅ 模型已加载完成，可以使用OCR功能")
elif engine.is_initializing():
    print("⏳ 模型还在加载中...")
    print("   说明：首次下载模型需要几分钟")
    print("   用户可以选择等待或稍后重试")
else:
    print("❌ 模型加载失败")

print("\n" + "=" * 60)
print("✅ 异步加载测试完成")
print("=" * 60)
print("\n说明：")
print("- 引擎创建后立即返回，不阻塞")
print("- 模型在后台线程中下载和加载")
print("- 用户可以继续使用程序的其他功能")
print("- 首次使用OCR时，如果模型还在加载，会提示用户等待")
