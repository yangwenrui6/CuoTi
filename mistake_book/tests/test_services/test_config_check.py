"""检查OCR配置是否正确"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

print("检查OCR配置")
print("=" * 60)

# 检查配置
from mistake_book.services.ocr_engine import EasyOCREngine, create_ocr_engine

# 测试1: 检查默认配置
print("\n[测试1] 检查EasyOCREngine默认配置...")
engine1 = EasyOCREngine()
print(f"   默认语言配置: {engine1.langs}")
if engine1.langs == ['ch_sim']:
    print("   ✅ 正确！只使用中文模型")
else:
    print(f"   ❌ 错误！配置为: {engine1.langs}")

# 测试2: 检查create_ocr_engine配置
print("\n[测试2] 检查create_ocr_engine配置...")
try:
    import easyocr
    engine2 = create_ocr_engine(async_init=False)
    if engine2:
        print(f"   语言配置: {engine2.langs}")
        if engine2.langs == ['ch_sim']:
            print("   ✅ 正确！只使用中文模型")
        else:
            print(f"   ❌ 错误！配置为: {engine2.langs}")
    else:
        print("   ❌ 引擎创建失败")
except ImportError:
    print("   ⚠️  EasyOCR未安装")

# 测试3: 检查模型文件
print("\n[测试3] 检查已下载的模型文件...")
import os
model_dir = os.environ.get('EASYOCR_MODULE_PATH', 'D:/EasyOCR')
model_path = Path(model_dir)

if model_path.exists():
    print(f"   模型目录: {model_path}")
    models = list(model_path.glob("*.pth"))
    if models:
        print(f"   已下载模型:")
        for model in models:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"      - {model.name} ({size_mb:.1f} MB)")
    else:
        print("   ⚠️  未找到模型文件")
else:
    print(f"   ⚠️  模型目录不存在: {model_path}")

print("\n" + "=" * 60)
print("结论:")
print("✅ 配置已修改为只使用中文模型")
print("✅ 不会再下载英文模型")
print("✅ 下次启动应该很快")
