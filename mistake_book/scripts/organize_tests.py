"""组织测试文件到对应的子目录"""

import shutil
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
tests_dir = project_root / "tests"

# 创建子目录
(tests_dir / "test_services").mkdir(exist_ok=True)
(tests_dir / "test_ui").mkdir(exist_ok=True)

# 定义文件映射
file_mappings = {
    # Services层测试（OCR相关）
    "test_services": [
        "test_ocr_simple.py",
        "test_ocr_complete.py",
        "test_ocr_full_flow.py",
        "test_ocr_thread.py",
        "test_ocr_with_image.py",
        "test_chinese_only_model.py",
        "test_with_existing_models.py",
        "test_config_check.py",
        "test_async_loading.py",
        "test_lazy_loading.py",
        "test_recognition_flow.py",
    ],
    # UI层测试
    "test_ui": [
        "test_add_dialog.py",
        "test_image_loading.py",
        "test_cursor_warning.py",
    ],
    # 集成测试（保留在根目录）
    # "test_full_integration.py" - 保留在tests/根目录
}

# 移动文件
for target_dir, files in file_mappings.items():
    target_path = tests_dir / target_dir
    for filename in files:
        source = tests_dir / filename
        if source.exists():
            dest = target_path / filename
            print(f"移动: {filename} -> {target_dir}/")
            shutil.move(str(source), str(dest))
        else:
            print(f"跳过: {filename} (文件不存在)")

# 创建__init__.py文件
for subdir in ["test_services", "test_ui", "test_core", "test_database", "test_utils"]:
    init_file = tests_dir / subdir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""测试模块"""\n')
        print(f"创建: {subdir}/__init__.py")

print("\n✅ 测试文件组织完成！")
print("\n新的测试目录结构：")
print("tests/")
print("├── test_services/    # 服务层测试（OCR相关）")
print("├── test_ui/          # UI层测试")
print("├── test_core/        # 核心层测试")
print("├── test_database/    # 数据库层测试")
print("├── test_utils/       # 工具层测试")
print("└── test_full_integration.py  # 集成测试")
