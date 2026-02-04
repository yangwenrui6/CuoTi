"""PyInstaller打包配置"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    "src/mistake_book/__main__.py",
    "--name=错题本",
    "--windowed",
    "--onefile",
    "--icon=resources/images/icon.ico",
    "--add-data=resources:resources",
    "--hidden-import=PyQt6",
    "--hidden-import=sqlalchemy",
    "--clean",
])
