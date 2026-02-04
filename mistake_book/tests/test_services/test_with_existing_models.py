"""使用现有模型测试OCR"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

print("=" * 60)
print("使用现有模型测试OCR")
print("=" * 60)

# 设置环境
import os
os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'

print("\n[1] 检查现有模型...")
model_dir = Path("D:/EasyOCR/model")
if model_dir.exists():
    models = list(model_dir.glob("*.pth"))
    print(f"   找到 {len(models)} 个模型文件:")
    for model in models:
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"   - {model.name} ({size_mb:.1f} MB)")
else:
    print("   ❌ 模型目录不存在")
    sys.exit(1)

print("\n[2] 导入EasyOCR...")
try:
    import torch
    import easyocr
    print("   ✅ EasyOCR导入成功")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

print("\n[3] 创建Reader（只使用中文）...")
print("   提示: 只使用中文可以避免下载英文模型")
try:
    # 只使用中文，不使用英文
    reader = easyocr.Reader(
        ['ch_sim'],  # 只用中文
        gpu=False,
        verbose=True,
        model_storage_directory='D:/EasyOCR'
    )
    print("   ✅ Reader创建成功（只使用中文）")
except Exception as e:
    print(f"   ❌ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4] 创建测试图片...")
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (400, 150), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 40)
except:
    font = ImageFont.load_default()

draw.text((50, 50), "测试文字", fill='black', font=font)

test_image = project_root / "test_chinese_only.png"
img.save(test_image)
print(f"   ✅ 测试图片: {test_image}")

print("\n[5] 执行OCR识别...")
try:
    import numpy as np
    img_array = np.array(Image.open(test_image))
    result = reader.readtext(img_array)
    
    print("\n" + "=" * 60)
    print("识别结果:")
    print("=" * 60)
    
    if result:
        for detection in result:
            text = detection[1]
            confidence = detection[2]
            print(f"   文字: {text}")
            print(f"   置信度: {confidence:.2f}")
        print("=" * 60)
        print("\n✅ OCR识别成功！")
    else:
        print("   (未识别出文字)")
        print("=" * 60)
        
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
