@echo off
echo ========================================
echo 错题本 - 快速安装脚本
echo ========================================
echo.

echo [1/3] 检查Python版本...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)
echo.

echo [2/3] 安装依赖包...
pip install -r dependencies\requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo.

echo [3/3] 安装完成
echo.

echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 运行应用: python run.py
echo.
pause
