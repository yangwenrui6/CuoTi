#!/bin/bash

echo "========================================"
echo "错题本 - 快速安装脚本"
echo "========================================"
echo ""

echo "[1/3] 检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi
echo ""

echo "[2/3] 安装依赖包..."
pip3 install -r dependencies/requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi
echo ""

echo "[3/3] 安装完成"
echo ""

echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "运行应用: python3 run.py"
echo ""
