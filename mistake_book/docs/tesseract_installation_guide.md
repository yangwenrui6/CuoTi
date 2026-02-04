# Tesseract OCR 安装指南

## 问题诊断
- ✅ pytesseract Python库已安装
- ❌ Tesseract程序本身未安装到 D:\Tesseract-OCR

## 解决方案：安装Tesseract程序

### 步骤1：下载正确的安装包

**重要：** 你需要下载的是 `.exe` 安装程序，不是GitHub源代码！

1. 访问官方Windows安装包页面：
   https://github.com/UB-Mannheim/tesseract/wiki

2. 下载最新版本（推荐）：
   - 文件名类似：`tesseract-ocr-w64-setup-5.3.3.20231005.exe`
   - 大小约：60-80 MB

### 步骤2：安装到D盘

1. 双击运行下载的 `.exe` 文件
2. 在安装路径选择界面，修改为：`D:\Tesseract-OCR`
3. **重要：** 在"选择组件"界面，勾选以下语言包：
   - ✅ Chinese (Simplified) - 简体中文
   - ✅ English - 英文
4. 点击"安装"完成

### 步骤3：验证安装

在PowerShell中运行：
```powershell
Test-Path "D:\Tesseract-OCR\tesseract.exe"
```

应该返回 `True`

再运行：
```powershell
& "D:\Tesseract-OCR\tesseract.exe" --version
```

应该显示版本信息

### 步骤4：测试OCR功能

重新启动你的错题本程序，拖拽图片测试OCR识别。

## 常见问题

### Q: 我下载的是源代码怎么办？
A: GitHub上的"Code"按钮下载的是源代码，需要编译。请访问上面的Wiki链接下载预编译的安装程序。

### Q: 安装后还是不能用？
A: 确保：
1. 安装路径正确：`D:\Tesseract-OCR\tesseract.exe` 存在
2. 已安装中文语言包（chi_sim）
3. 重启你的Python程序

### Q: 为什么选择Tesseract？
A: 
- ✅ 轻量级（约80MB）
- ✅ 开源免费
- ✅ 不需要GPU
- ✅ 支持中文
- ✅ 你的Python库已安装好

## 其他OCR引擎对比

| 引擎 | 状态 | 原因 |
|------|------|------|
| PaddleOCR | ❌ 不可用 | 不支持Python 3.14 |
| EasyOCR | ⚠️ 已安装但有错误 | DLL初始化失败（torch依赖问题）|
| Tesseract | ⏳ 待安装 | 只需安装程序即可 |

## 下载链接

**官方Windows安装包：**
https://github.com/UB-Mannheim/tesseract/wiki

**直接下载链接（可能需要更新）：**
https://digi.bib.uni-mannheim.de/tesseract/

选择最新的 `tesseract-ocr-w64-setup-*.exe` 文件
