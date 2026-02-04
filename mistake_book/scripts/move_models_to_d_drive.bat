@echo off
chcp 65001 >nul
echo ============================================================
echo 将EasyOCR模型移动到D盘
echo ============================================================
echo.

REM 检查C盘模型目录是否存在
set "SOURCE_DIR=%USERPROFILE%\.EasyOCR"
set "TARGET_DIR=D:\EasyOCR"

if not exist "%SOURCE_DIR%" (
    echo ⚠️  C盘模型目录不存在: %SOURCE_DIR%
    echo 说明：可能还没有下载过模型，或者已经移动过了
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b
)

echo ✅ 找到C盘模型目录: %SOURCE_DIR%
echo.

REM 显示C盘模型文件大小
echo [1] 检查C盘模型文件...
if exist "%SOURCE_DIR%\model" (
    dir "%SOURCE_DIR%\model" /s
    echo.
) else (
    echo ⚠️  模型文件夹不存在
    echo.
)

REM 询问是否继续
echo [2] 准备移动到: %TARGET_DIR%
echo.
set /p CONFIRM="确认移动吗？(Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 操作已取消
    pause
    exit /b
)

echo.
echo [3] 开始移动...

REM 创建目标目录
if not exist "%TARGET_DIR%" (
    echo 创建目标目录: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
)

REM 移动文件
echo 移动模型文件...
xcopy "%SOURCE_DIR%\*" "%TARGET_DIR%\" /E /I /Y

if %ERRORLEVEL% EQU 0 (
    echo ✅ 移动成功！
    echo.
    
    REM 询问是否删除C盘旧文件
    echo [4] 清理C盘旧文件
    set /p DELETE="是否删除C盘旧文件？(Y/N): "
    if /i "%DELETE%"=="Y" (
        echo 删除C盘旧文件...
        rmdir /s /q "%SOURCE_DIR%"
        echo ✅ 清理完成！
    ) else (
        echo ℹ️  保留C盘旧文件（可以手动删除）
    )
) else (
    echo ❌ 移动失败！
    echo 请检查权限或磁盘空间
)

echo.
echo ============================================================
echo 完成！
echo ============================================================
echo.
echo 提示：
echo 1. 程序已配置使用D盘路径（在main.py中）
echo 2. 下次启动程序时会自动使用D盘模型
echo 3. 如果要使用其他盘，请修改 main.py 中的路径
echo.
echo 按任意键退出...
pause >nul
