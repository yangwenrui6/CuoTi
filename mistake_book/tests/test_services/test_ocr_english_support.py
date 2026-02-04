"""测试OCR英文识别支持"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

print("测试OCR中英文混合识别")
print("=" * 60)

from mistake_book.services.ocr_engine import create_ocr_engine
from PIL import Image, ImageDraw, ImageFont

# 创建OCR引擎
print("\n[1] 创建OCR引擎...")
engine = create_ocr_engine(async_init=False)

if not engine:
    print("❌ OCR引擎创建失败")
    sys.exit(1)

print(f"✅ OCR引擎创建成功")
print(f"   语言配置: {engine.langs}")

# 测试1: 纯英文
print("\n[测试1] 纯英文识别...")
img1 = Image.new('RGB', (500, 100), color='white')
draw1 = ImageDraw.Draw(img1)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
except:
    font = ImageFont.load_default()

draw1.text((50, 30), "Hello World 123", fill='black', font=font)
test1 = project_root / "test_english.png"
img1.save(test1)

try:
    result1 = engine.recognize(test1)
    print(f"   原文: Hello World 123")
    print(f"   识别: {result1}")
    if "Hello" in result1 or "hello" in result1.lower():
        print("   ✅ 英文识别成功")
    else:
        print("   ❌ 英文识别失败")
except Exception as e:
    print(f"   ❌ 识别出错: {e}")

# 测试2: 纯中文
print("\n[测试2] 纯中文识别...")
img2 = Image.new('RGB', (400, 100), color='white')
draw2 = ImageDraw.Draw(img2)
try:
    font_cn = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 36)
except:
    font_cn = ImageFont.load_default()

draw2.text((50, 30), "这是中文测试", fill='black', font=font_cn)
test2 = project_root / "test_chinese.png"
img2.save(test2)

try:
    result2 = engine.recognize(test2)
    print(f"   原文: 这是中文测试")
    print(f"   识别: {result2}")
    if "中文" in result2:
        print("   ✅ 中文识别成功")
    else:
        print("   ❌ 中文识别失败")
except Exception as e:
    print(f"   ❌ 识别出错: {e}")

# 测试3: 中英文混合
print("\n[测试3] 中英文混合识别...")
img3 = Image.new('RGB', (600, 150), color='white')
draw3 = ImageDraw.Draw(img3)

draw3.text((50, 30), "题目: Solve x+5=10", fill='black', font=font_cn)
draw3.text((50, 80), "答案: x=5", fill='black', font=font_cn)
test3 = project_root / "test_mixed.png"
img3.save(test3)

try:
    result3 = engine.recognize(test3)
    print(f"   原文: 题目: Solve x+5=10")
    print(f"         答案: x=5")
    print(f"   识别: {result3}")
    
    has_chinese = "题目" in result3 or "答案" in result3
    has_english = "Solve" in result3 or "solve" in result3.lower()
    
    if has_chinese and has_english:
        print("   ✅ 中英文混合识别成功")
    elif has_chinese:
        print("   ⚠️ 只识别了中文")
    elif has_english:
        print("   ⚠️ 只识别了英文")
    else:
        print("   ❌ 识别失败")
except Exception as e:
    print(f"   ❌ 识别出错: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("\n说明:")
print("- 如果英文识别失败，可能需要下载英文模型")
print("- 首次使用会自动下载，请耐心等待")
print("- 模型位置: D:/EasyOCR/")
