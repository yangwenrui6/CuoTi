"""PyInstaller打包配置 - UI重构后更新"""

import PyInstaller.__main__
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent

# 收集所有UI组件和对话框
hiddenimports = [
    # PyQt6核心
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    
    # UI组件
    'mistake_book.ui.components.image_uploader',
    'mistake_book.ui.components.ocr_panel',
    'mistake_book.ui.components.question_form',
    'mistake_book.ui.components.filter_panel',
    'mistake_book.ui.components.statistics_panel',
    'mistake_book.ui.components.navigation_tree',
    
    # 对话框
    'mistake_book.ui.dialogs.add_question',
    'mistake_book.ui.dialogs.detail',
    'mistake_book.ui.dialogs.review',
    'mistake_book.ui.dialogs.review_module_selector',
    'mistake_book.ui.dialogs.review_history_dialog',
    
    # 主窗口
    'mistake_book.ui.main_window.window',
    'mistake_book.ui.main_window.controller',
    'mistake_book.ui.main_window.panels',
    
    # 工厂和事件
    'mistake_book.ui.factories.dialog_factory',
    'mistake_book.ui.events.event_bus',
    'mistake_book.ui.events.events',
    
    # 服务层
    'mistake_book.services.question_service',
    'mistake_book.services.review_service',
    'mistake_book.services.ui_service',
    'mistake_book.services.ocr_engine',
    
    # 核心层
    'mistake_book.core.data_manager',
    'mistake_book.core.review_scheduler',
    
    # 数据库
    'mistake_book.database.db_manager',
    'mistake_book.database.models',
    
    # Pillow图片处理
    'PIL',
    'PIL.Image',
]

# 打包参数
args = [
    str(project_root / 'run.py'),
    '--name=错题本',
    '--windowed',
    '--onefile',
    '--clean',
    
    # 添加数据文件
    f'--add-data={project_root / "resources"}{sys.platform == "win32" and ";" or ":"}resources',
    
    # 隐藏导入
    *[f'--hidden-import={imp}' for imp in hiddenimports],
    
    # 排除不需要的模块（减小体积）
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=scipy',
    
    # 输出目录
    '--distpath=dist',
    '--workpath=build',
    '--specpath=build',
]

# 如果有图标文件，添加图标
icon_path = project_root / 'resources' / 'images' / 'icon.ico'
if icon_path.exists():
    args.append(f'--icon={icon_path}')

print("=" * 60)
print("开始打包错题本应用...")
print("=" * 60)
print(f"项目根目录: {project_root}")
print(f"Python版本: {sys.version}")
print("=" * 60)

# 运行PyInstaller
PyInstaller.__main__.run(args)

print("=" * 60)
print("打包完成！")
print(f"可执行文件位置: {project_root / 'dist' / '错题本.exe'}")
print("=" * 60)
