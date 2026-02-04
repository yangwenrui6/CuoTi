"""编译Qt资源文件"""

from pathlib import Path
import subprocess


def compile_ui_files():
    """编译.ui文件为.py"""
    ui_dir = Path("resources/ui")
    output_dir = Path("src/mistake_book/ui/resources/ui_compiled")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for ui_file in ui_dir.glob("*.ui"):
        output_file = output_dir / f"{ui_file.stem}_ui.py"
        subprocess.run([
            "pyuic6",
            str(ui_file),
            "-o",
            str(output_file)
        ])
        print(f"编译: {ui_file.name} -> {output_file.name}")


def compile_qrc_file():
    """编译.qrc资源文件"""
    qrc_file = Path("resources/app.qrc")
    output_file = Path("src/mistake_book/ui/resources/resources_rc.py")
    
    if qrc_file.exists():
        subprocess.run([
            "pyrcc6",
            str(qrc_file),
            "-o",
            str(output_file)
        ])
        print(f"编译: {qrc_file.name} -> {output_file.name}")


if __name__ == "__main__":
    print("开始编译资源文件...")
    compile_ui_files()
    compile_qrc_file()
    print("编译完成！")
