"""检查OCR状态 - 快速诊断工具"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("OCR状态检查工具")
print("=" * 60)

# 1. 检查Python版本
print("\n[1] Python版本")
print(f"   版本: {sys.version}")
print(f"   路径: {sys.executable}")

# 2. 检查torch
print("\n[2] PyTorch")
try:
    import torch
    print(f"   ✅ 已安装: {torch.__version__}")
except ImportError:
    print(f"   ❌ 未安装")
    print(f"   安装命令: pip install torch")

# 3. 检查easyocr
print("\n[3] EasyOCR")
try:
    import easyocr
    print(f"   ✅ 已安装: {easyocr.__version__}")
except ImportError:
    print(f"   ❌ 未安装")
    print(f"   安装命令: pip install easyocr")
except Exception as e:
    print(f"   ⚠️  导入失败: {e}")

# 4. 检查模型文件
print("\n[4] 模型文件")

# 检查环境变量
easyocr_path = os.environ.get('EASYOCR_MODULE_PATH')
if easyocr_path:
    print(f"   ℹ️  自定义路径: {easyocr_path}")
    model_dir = Path(easyocr_path) / "model"
else:
    print(f"   ℹ️  使用默认路径")
    model_dir = Path.home() / ".EasyOCR" / "model"

if model_dir.exists():
    print(f"   ✅ 模型目录存在: {model_dir}")
    
    # 检查各个模型文件
    models = {
        "craft_mlt_25k.pth": "检测模型",
        "zh_sim_g2.pth": "中文识别模型",
        "english_g2.pth": "英文识别模型"
    }
    
    for model_file, desc in models.items():
        model_path = model_dir / model_file
        if model_path.exists():
            size_mb = model_path.stat().st_size / 1024 / 1024
            print(f"   ✅ {desc}: {model_file} ({size_mb:.1f}MB)")
        else:
            print(f"   ❌ {desc}: {model_file} (未下载)")
    
    # 检查是否有临时文件
    temp_files = list(model_dir.glob("temp*"))
    if temp_files:
        print(f"   ⚠️  发现临时文件（可能是下载中断）:")
        for temp_file in temp_files:
            size_mb = temp_file.stat().st_size / 1024 / 1024
            print(f"      {temp_file.name} ({size_mb:.1f}MB)")
        print(f"   建议：删除临时文件后重新下载")
else:
    print(f"   ⚠️  模型目录不存在: {model_dir}")
    print(f"   说明：首次使用时会自动创建并下载模型")

# 5. 检查磁盘空间
print("\n[5] 磁盘空间")
try:
    import shutil
    total, used, free = shutil.disk_usage(Path.home())
    free_gb = free / 1024 / 1024 / 1024
    print(f"   可用空间: {free_gb:.1f}GB")
    if free_gb < 0.5:
        print(f"   ⚠️  磁盘空间不足，建议至少保留500MB")
    else:
        print(f"   ✅ 磁盘空间充足")
except Exception as e:
    print(f"   ⚠️  无法检查: {e}")

# 6. 测试OCR引擎创建
print("\n[6] OCR引擎测试")
try:
    # 添加src目录到Python路径
    # 从scripts目录向上两级到项目根目录，然后进入src
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_path = project_root / "src"
    
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        
        from mistake_book.services.ocr_engine import create_ocr_engine
        
        engine = create_ocr_engine()
        if engine:
            print(f"   ✅ OCR引擎创建成功")
            print(f"   类型: {engine.__class__.__name__}")
            print(f"   可用: {engine.is_available()}")
            print(f"   已初始化: {engine._initialized}")
            
            if not engine._initialized:
                print(f"   说明：模型将在首次使用时加载（延迟加载）")
        else:
            print(f"   ❌ OCR引擎创建失败")
    else:
        print(f"   ⚠️  找不到源代码目录: {src_path}")
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 7. 总结
print("\n" + "=" * 60)
print("诊断总结")
print("=" * 60)

print("\n如果所有检查都通过（✅），说明OCR功能可以正常使用。")
print("\n如果有警告（⚠️）或错误（❌），请根据提示进行修复。")
print("\n常见问题：")
print("  1. 模型未下载 → 首次使用时会自动下载")
print("  2. 临时文件存在 → 删除后重新下载")
print("  3. 磁盘空间不足 → 清理磁盘空间")
print("  4. 依赖未安装 → 运行 pip install easyocr")

print("\n详细文档：mistake_book/docs/ocr_quick_start.md")
print("=" * 60)
