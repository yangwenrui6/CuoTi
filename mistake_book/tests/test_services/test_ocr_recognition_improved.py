"""测试改进后的OCR识别效果"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

print("测试改进后的OCR识别")
print("=" * 60)

from mistake_book.services.ocr_engine import create_ocr_engine
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 创建OCR引擎
print("\n[1] 创建OCR引擎...")
engine = create_ocr_engine(async_init=False)

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功")

# 创建测试图片 - 包含多行文字
print("\n[2] 创建测试图片（多行文字）...")
img = Image.new('RGB', (800, 400), color='white')
draw = ImageDraw.Draw(img)

try:
    font_large = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 32)
    font_small = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 24)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 绘制多行文字
texts = [
    ("题目：", 50, 30, font_large),
    ("已知函数 f(x) = x² + 2x + 1", 50, 80, font_small),
    ("求：f(x) 的最小值", 50, 120, font_small),
    ("", 50, 160, font_small),
    ("解答：", 50, 200, font_large),
    ("f(x) = (x + 1)²", 50, 250, font_small),
    ("最小值为 0", 50, 290, font_small),
]

for text, x, y, font in texts:
    if text:  # 跳过空行
        draw.text((x, y), text, fill='black', font=font)

test_image = project_root / "test_ocr_multiline.png"
img.save(test_image)
print(f"✅ 测试图片已保存: {test_image}")

# 执行OCR识别
print("\n[3] 执行OCR识别...")
try:
    result = engine.recognize(test_image)
    
    print(f"\n✅ 识别成功!")
    print(f"\n识别结果:")
    print("-" * 60)
    print(result)
    print("-" * 60)
    
    # 统计识别结果
    lines = result.split('\n')
    print(f"\n识别统计:")
    print(f"  总行数: {len(lines)}")
    print(f"  非空行: {len([l for l in lines if l.strip()])}")
    
    # 检查关键词是否被识别
    keywords = ["题目", "函数", "最小值", "解答"]
    found_keywords = [kw for kw in keywords if kw in result]
    print(f"  关键词识别: {len(found_keywords)}/{len(keywords)}")
    print(f"  已识别: {', '.join(found_keywords)}")
    
    if len(found_keywords) >= len(keywords) * 0.7:
        print("\n✅ 识别效果良好（70%以上关键词被识别）")
    else:
        print("\n⚠️ 识别效果一般（部分关键词未识别）")
        
except Exception as e:
    print(f"❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
