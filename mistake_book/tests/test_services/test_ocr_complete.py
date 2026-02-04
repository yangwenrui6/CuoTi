"""完整OCR识别测试 - 创建文字图片并识别"""

import sys
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont

# 添加src到路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("完整OCR识别测试")
print("=" * 60)

# 步骤1: 导入模块
print("\n[步骤1] 导入模块...")
try:
    import os
    os.environ['EASYOCR_MODULE_PATH'] = 'D:/EasyOCR'
    
    import torch  # 先导入torch
    
    from mistake_book.services.ocr_engine import create_ocr_engine
    from mistake_book.services.question_service import QuestionService
    from mistake_book.core.data_manager import DataManager
    from mistake_book.database.db_manager import DatabaseManager
    from mistake_book.config.paths import get_app_paths
    print("   ✅ 模块导入成功")
except Exception as e:
    print(f"   ❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤2: 创建包含文字的测试图片
print("\n[步骤2] 创建包含文字的测试图片...")
try:
    # 创建一个白色背景的图片
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        # Windows系统字体
        font_large = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 40)
        font_small = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 30)
    except:
        try:
            # 备用字体
            font_large = ImageFont.truetype("arial.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except:
            # 使用默认字体
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 绘制文字
    test_text = [
        "这是一道数学题",
        "求解方程: x^2 + 2x + 1 = 0",
        "This is a test question",
        "Solve: 2x + 5 = 15"
    ]
    
    y_position = 50
    for text in test_text:
        draw.text((50, y_position), text, fill='black', font=font_small)
        y_position += 80
    
    # 保存测试图片
    test_image_path = project_root / "test_ocr_image.png"
    img.save(test_image_path)
    print(f"   ✅ 测试图片创建成功: {test_image_path}")
    print(f"   包含文字:")
    for text in test_text:
        print(f"      - {text}")
    
except Exception as e:
    print(f"   ❌ 创建测试图片失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤3: 初始化服务
print("\n[步骤3] 初始化服务...")
try:
    paths = get_app_paths()
    db_manager = DatabaseManager(paths.database_file)
    data_manager = DataManager(db_manager)
    
    # 创建OCR引擎（同步模式，会立即初始化）
    print("   正在创建OCR引擎...")
    ocr_engine = create_ocr_engine(async_init=False)
    
    if not ocr_engine:
        print("   ❌ OCR引擎创建失败")
        sys.exit(1)
    
    print(f"   ✅ OCR引擎创建成功")
    print(f"      - 引擎类型: {type(ocr_engine).__name__}")
    print(f"      - 可用性: {ocr_engine.is_available()}")
    
    question_service = QuestionService(data_manager, ocr_engine)
    print("   ✅ 服务初始化成功")
    
except Exception as e:
    print(f"   ❌ 服务初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤4: 测试OCR识别
print("\n[步骤4] 测试OCR识别...")
print("   提示: 首次使用需要下载模型（约100-200MB），请耐心等待...")
print("   如果下载时间过长，可以按Ctrl+C取消")
print()

try:
    # 使用question_service的recognize_image_with_retry方法
    print("   开始识别...")
    success, message, recognized_text = question_service.recognize_image_with_retry(
        test_image_path
    )
    
    print("\n" + "=" * 60)
    print("识别结果")
    print("=" * 60)
    print(f"成功: {success}")
    print(f"消息: {message}")
    print(f"\n识别的文字:")
    print("-" * 60)
    if recognized_text:
        print(recognized_text)
    else:
        print("(无)")
    print("-" * 60)
    
    # 对比原文
    print(f"\n原始文字:")
    print("-" * 60)
    for text in test_text:
        print(text)
    print("-" * 60)
    
    if success and recognized_text:
        print("\n✅ OCR识别成功！")
        
        # 简单的相似度检查
        original_chars = set(''.join(test_text).replace(' ', '').lower())
        recognized_chars = set(recognized_text.replace(' ', '').replace('\n', '').lower())
        common_chars = original_chars & recognized_chars
        
        if len(original_chars) > 0:
            similarity = len(common_chars) / len(original_chars) * 100
            print(f"   字符匹配度: {similarity:.1f}%")
    else:
        print("\n❌ OCR识别失败")
        print(f"   原因: {message}")
    
except KeyboardInterrupt:
    print("\n\n⚠️  用户中断了测试")
    print("   提示: 如果是因为模型下载时间过长，可以:")
    print("   1. 检查网络连接")
    print("   2. 稍后重试")
    print("   3. 手动下载模型（参考文档）")
except Exception as e:
    print(f"\n❌ OCR识别失败: {e}")
    import traceback
    traceback.print_exc()

# 步骤5: 清理
print("\n[步骤5] 清理...")
try:
    # 询问是否删除测试图片
    print(f"   测试图片保存在: {test_image_path}")
    print("   可以手动查看或删除")
except Exception as e:
    print(f"   ⚠️  清理失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
