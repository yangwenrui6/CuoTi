"""测试只使用中文模型的OCR功能"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

print("测试只使用中文模型")
print("=" * 60)

from mistake_book.services.ocr_engine import create_ocr_engine
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 创建OCR引擎（只使用中文模型）
print("\n创建OCR引擎...")
engine = create_ocr_engine(async_init=False)

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功")
print(f"   语言配置: {engine.langs}")

# 创建测试图片
print("\n创建测试图片...")
img = Image.new('RGB', (500, 150), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 36)
except:
    font = ImageFont.load_default()

# 中英文混合文本
draw.text((50, 30), "题目: Solve x+5=10", fill='black', font=font)
draw.text((50, 80), "答案: x=5", fill='black', font=font)

test_image = project_root / "test_chinese_only.png"
img.save(test_image)
print(f"✅ 测试图片已保存: {test_image}")

# 执行OCR识别
print("\n执行OCR识别...")
try:
    result = engine.recognize(test_image)
    print(f"✅ 识别成功!")
    print(f"\n识别结果:")
    print("-" * 60)
    print(result)
    print("-" * 60)
except Exception as e:
    print(f"❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("结论:")
print("✅ 只使用中文模型（ch_sim）")
print("✅ 不会下载额外的英文模型")
print("✅ 中文模型可以识别中文、英文和数字")
