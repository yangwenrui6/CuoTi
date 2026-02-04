"""测试OCR完整流程 - 包括实际图片识别"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "mistake_book" / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("测试OCR完整流程（包括实际识别）")
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

if not is_available:
    print("❌ 引擎不可用，请检查easyocr是否已安装")
    sys.exit(1)

print("\n[步骤3] 创建测试图片...")
# 创建一个简单的测试图片（白底黑字）
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建白色背景
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("msyh.ttc", 40)  # 微软雅黑
    except:
        # 如果没有字体，使用默认字体
        font = ImageFont.load_default()
    
    draw.text((20, 30), "测试文字 Test", fill='black', font=font)
    
    # 保存图片
    test_image_path = Path("test_ocr_image.png")
    img.save(test_image_path)
    print(f"✅ 测试图片已创建: {test_image_path}")
    
except Exception as e:
    print(f"⚠️  创建测试图片失败: {e}")
    print("请手动提供一个测试图片")
    sys.exit(1)

print("\n[步骤4] 首次调用recognize()...")
print("注意：这会触发模型加载，需要5-10秒")
print("请耐心等待...")

try:
    print(f"\n开始识别图片: {test_image_path}")
    print(f"识别前状态:")
    print(f"   _init_attempted: {engine._init_attempted}")
    print(f"   _initialized: {engine._initialized}")
    
    text = engine.recognize(test_image_path)
    
    print(f"\n✅ 识别成功！")
    print(f"识别后状态:")
    print(f"   _init_attempted: {engine._init_attempted}")
    print(f"   _initialized: {engine._initialized}")
    print(f"   reader: {engine.reader is not None}")
    print(f"\n识别结果:")
    print(f"   {text}")
    
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    print(f"识别后状态:")
    print(f"   _init_attempted: {engine._init_attempted}")
    print(f"   _initialized: {engine._initialized}")
    print(f"   reader: {engine.reader}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[步骤5] 第二次调用recognize()...")
print("注意：模型已加载，应该很快")

try:
    text = engine.recognize(test_image_path)
    print(f"✅ 第二次识别成功！")
    print(f"识别结果: {text}")
except Exception as e:
    print(f"❌ 第二次识别失败: {e}")

# 清理测试图片
try:
    test_image_path.unlink()
    print(f"\n✅ 测试图片已删除")
except:
    pass

print("\n" + "=" * 60)
print("✅ 完整流程测试完成")
print("=" * 60)
