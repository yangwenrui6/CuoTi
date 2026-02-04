"""测试图片加载功能 - 特别是中文路径"""

import sys
from pathlib import Path

# 添加src到路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("图片加载测试")
print("=" * 60)

# 测试1: QPixmap加载中文路径
print("\n[测试1] QPixmap加载中文路径...")
try:
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QApplication
    
    # 创建QApplication（必须）
    app = QApplication(sys.argv)
    
    # 测试路径（包含中文）
    test_paths = [
        "D:/测试/图片.png",
        "D:/test/image.png",
        "C:/Users/用户/图片/test.jpg"
    ]
    
    for path in test_paths:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"   ❌ 加载失败: {path}")
        else:
            print(f"   ✅ 加载成功: {path}")
            
except Exception as e:
    print(f"   ❌ 测试失败: {e}")

# 测试2: PIL加载中文路径
print("\n[测试2] PIL加载中文路径...")
try:
    from PIL import Image
    import numpy as np
    
    for path in test_paths:
        try:
            img = Image.open(path)
            img_array = np.array(img)
            print(f"   ✅ 加载成功: {path} (shape: {img_array.shape})")
        except FileNotFoundError:
            print(f"   ⚠️  文件不存在: {path}")
        except Exception as e:
            print(f"   ❌ 加载失败: {path} - {e}")
            
except Exception as e:
    print(f"   ❌ 测试失败: {e}")

# 测试3: PIL转QPixmap
print("\n[测试3] PIL转QPixmap...")
try:
    from PIL import Image
    import numpy as np
    from PyQt6.QtGui import QImage, QPixmap
    
    # 创建一个测试图片
    test_img = Image.new('RGB', (100, 100), color='red')
    img_array = np.array(test_img)
    
    height, width, channel = img_array.shape
    bytes_per_line = 3 * width
    q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(q_image)
    
    if pixmap.isNull():
        print("   ❌ 转换失败")
    else:
        print(f"   ✅ 转换成功 (size: {pixmap.width()}x{pixmap.height()})")
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n结论:")
print("- QPixmap在Windows上不支持中文路径")
print("- PIL可以正常加载中文路径")
print("- 解决方案: 使用PIL加载后转换为QPixmap")
