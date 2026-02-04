"""简单OCR识别测试 - 使用已下载的模型"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加src到路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("简单OCR识别测试")
print("=" * 60)

# 导入模块
print("\n[1] 导入模块...")
import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

import torch
from mistake_book.services.ocr_engine import EasyOCREngine
from pathlib import Path

print("   ✅ 模块导入成功")

# 创建测试图片
print("\n[2] 创建测试图片...")
img = Image.new('RGB', (600, 200), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 36)
except:
    font = ImageFont.load_default()

# 绘制简单文字
draw.text((50, 50), "这是测试文字", fill='black', font=font)
draw.text((50, 120), "Test 123", fill='black', font=font)

test_image = project_root / "test_simple.png"
img.save(test_image)
print(f"   ✅ 测试图片: {test_image}")

# 初始化OCR引擎
print("\n[3] 初始化OCR引擎...")
print("   提示: 正在加载模型，请稍候...")

try:
    engine = EasyOCREngine(langs=['ch_sim', 'en'])
    
    # 手动触发初始化
    print("   开始加载模型...")
    engine._lazy_init()
    
    if engine._initialized:
        print("   ✅ OCR引擎初始化成功")
    else:
        print("   ❌ OCR引擎初始化失败")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 执行识别
print("\n[4] 执行OCR识别...")
try:
    result = engine.recognize(test_image)
    
    print("\n" + "=" * 60)
    print("识别结果:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    if result and len(result.strip()) > 0:
        print("\n✅ OCR识别成功！")
        print(f"   识别出 {len(result.splitlines())} 行文字")
    else:
        print("\n⚠️  未识别出文字")
        
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
print(f"测试图片保存在: {test_image}")
