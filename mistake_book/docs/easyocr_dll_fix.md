# EasyOCR DLL错误修复指南

## 问题描述
EasyOCR已安装，但启动时报错：
```
DLL load failed while importing _C: DLL 初始化失败
```

这是因为EasyOCR依赖的PyTorch需要Visual C++运行库。

## 解决方案

### 方法1：安装Visual C++ Redistributable（推荐）

1. 下载Microsoft Visual C++ Redistributable：
   https://aka.ms/vs/17/release/vc_redist.x64.exe

2. 双击安装

3. 重启电脑

4. 重新测试EasyOCR

### 方法2：降级torch版本

```powershell
pip uninstall torch torchvision
pip install torch==2.0.1 torchvision==0.15.2
```

### 方法3：使用CPU版本的torch

```powershell
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## 验证修复

运行以下Python代码测试：
```python
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
print("EasyOCR初始化成功！")
```

## 为什么会出现这个问题？

- EasyOCR依赖PyTorch
- PyTorch的C++扩展需要Visual C++运行库
- Windows系统可能缺少这些运行库

## 优缺点

### 优点
- ✅ 纯Python安装，无需额外程序
- ✅ 识别效果好
- ✅ 支持多种语言

### 缺点
- ❌ 依赖较多（torch等）
- ❌ 首次使用需下载模型（约100MB）
- ❌ 可能遇到DLL问题

## 建议

如果DLL问题难以解决，建议使用Tesseract（更简单可靠）。
