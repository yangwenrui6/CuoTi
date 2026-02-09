"""部署验证脚本 - 检查部署环境是否正确配置"""

import sys
import os
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_python_version():
    """检查Python版本"""
    print("\n" + "="*60)
    print("检查Python版本...")
    print("="*60)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python版本: {version_str} (符合要求)")
        return True
    else:
        print_error(f"Python版本: {version_str} (需要3.9+)")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n" + "="*60)
    print("检查依赖包...")
    print("="*60)
    
    required_packages = {
        'PyQt6': 'PyQt6',
        'sqlalchemy': 'SQLAlchemy',
        'PIL': 'Pillow',
        'platformdirs': 'platformdirs',
    }
    
    optional_packages = {
        'easyocr': 'EasyOCR',
        'torch': 'PyTorch',
    }
    
    all_ok = True
    
    # 检查必需包
    print("\n必需依赖:")
    for module, name in required_packages.items():
        try:
            __import__(module)
            print_success(f"{name} 已安装")
        except ImportError:
            print_error(f"{name} 未安装")
            all_ok = False
    
    # 检查可选包
    print("\n可选依赖:")
    for module, name in optional_packages.items():
        try:
            __import__(module)
            print_success(f"{name} 已安装")
        except ImportError:
            print_warning(f"{name} 未安装（OCR功能不可用）")
        except Exception as e:
            print_warning(f"{name} 已安装但加载失败（{str(e)[:50]}...）")
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    print("\n" + "="*60)
    print("检查项目结构...")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    required_dirs = [
        'src/mistake_book',
        'src/mistake_book/ui',
        'src/mistake_book/ui/components',
        'src/mistake_book/ui/dialogs',
        'src/mistake_book/ui/main_window',
        'src/mistake_book/ui/factories',
        'src/mistake_book/ui/events',
        'src/mistake_book/services',
        'src/mistake_book/core',
        'src/mistake_book/database',
        'tests',
        'docs',
        'resources',
        'scripts',
        'dependencies',
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print_success(f"{dir_path}/ 存在")
        else:
            print_error(f"{dir_path}/ 不存在")
            all_ok = False
    
    return all_ok

def check_key_files():
    """检查关键文件"""
    print("\n" + "="*60)
    print("检查关键文件...")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    required_files = [
        'run.py',
        'src/mistake_book/main.py',
        'src/mistake_book/ui/main_window/window.py',
        'src/mistake_book/ui/main_window/controller.py',
        'src/mistake_book/ui/factories/dialog_factory.py',
        'src/mistake_book/ui/events/event_bus.py',
        'dependencies/requirements.txt',
        'README.md',
        'DEPLOYMENT.md',
    ]
    
    all_ok = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"{file_path} 存在")
        else:
            print_error(f"{file_path} 不存在")
            all_ok = False
    
    return all_ok

def check_ui_components():
    """检查UI组件"""
    print("\n" + "="*60)
    print("检查UI组件...")
    print("="*60)
    
    try:
        # 添加src到路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / 'src'))
        
        components = [
            'mistake_book.ui.components.image_uploader',
            'mistake_book.ui.components.ocr_panel',
            'mistake_book.ui.components.question_form',
            'mistake_book.ui.components.filter_panel',
            'mistake_book.ui.components.statistics_panel',
            'mistake_book.ui.components.navigation_tree',
        ]
        
        all_ok = True
        for component in components:
            try:
                __import__(component)
                print_success(f"{component.split('.')[-1]} 可导入")
            except Exception as e:
                print_error(f"{component.split('.')[-1]} 导入失败: {e}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_error(f"检查UI组件时出错: {e}")
        return False

def check_dialogs():
    """检查对话框"""
    print("\n" + "="*60)
    print("检查对话框...")
    print("="*60)
    
    try:
        dialogs = [
            'mistake_book.ui.dialogs.add_question',
            'mistake_book.ui.dialogs.detail',
            'mistake_book.ui.dialogs.review',
            'mistake_book.ui.dialogs.review_module_selector',
            'mistake_book.ui.dialogs.review_history_dialog',
        ]
        
        all_ok = True
        for dialog in dialogs:
            try:
                __import__(dialog)
                print_success(f"{dialog.split('.')[-1]} 可导入")
            except Exception as e:
                print_error(f"{dialog.split('.')[-1]} 导入失败: {e}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_error(f"检查对话框时出错: {e}")
        return False

def check_services():
    """检查服务层"""
    print("\n" + "="*60)
    print("检查服务层...")
    print("="*60)
    
    try:
        services = [
            'mistake_book.services.question_service',
            'mistake_book.services.review_service',
            'mistake_book.services.ui_service',
            'mistake_book.services.ocr_engine',
        ]
        
        all_ok = True
        for service in services:
            try:
                __import__(service)
                print_success(f"{service.split('.')[-1]} 可导入")
            except Exception as e:
                print_error(f"{service.split('.')[-1]} 导入失败: {e}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_error(f"检查服务层时出错: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("错题本 v2.0 部署验证")
    print("="*60)
    
    results = {
        'Python版本': check_python_version(),
        '依赖包': check_dependencies(),
        '项目结构': check_project_structure(),
        '关键文件': check_key_files(),
        'UI组件': check_ui_components(),
        '对话框': check_dialogs(),
        '服务层': check_services(),
    }
    
    # 总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: 通过")
        else:
            print_error(f"{check}: 失败")
    
    # 最终结果
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print_success("✨ 所有检查通过！部署环境配置正确。")
        print_info("可以运行: python run.py")
    else:
        print_error("❌ 部署验证失败，请检查上述错误。")
        print_info("请参考 DEPLOYMENT.md 进行修复")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
