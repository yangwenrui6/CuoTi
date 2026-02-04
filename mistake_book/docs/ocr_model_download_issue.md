# OCR模型重复下载问题解决方案

## 问题描述

用户反馈：前几次OCR识别很快，但后面一直在加载下载模型。

## 问题原因

1. **配置了中英文混合模式**：`['ch_sim', 'en']`
2. **中文模型已下载完成**：
   - `craft_mlt_25k.pth` (83MB) - 文本检测模型 ✅
   - `zh_sim_g2.pth` (21MB) - 中文识别模型 ✅
3. **英文模型下载失败**：每次初始化都会尝试下载英文识别模型，但可能因为网络问题一直失败

## 已有模型

位置：`D:\EasyOCR\`

```
craft_mlt_25k.pth  (83MB)  - 文本检测模型
zh_sim_g2.pth      (21MB)  - 中文识别模型
```

## 解决方案

### 方案1：只使用中文模型（推荐）✅

**优点**：
- 不需要下载额外模型
- 启动更快
- 中文模型也能识别英文和数字

**修改内容**：

已修改 `src/mistake_book/services/ocr_engine.py`：

```python
# 修改前
self.langs = langs or ['ch_sim', 'en']

# 修改后
self.langs = langs or ['ch_sim']  # 只使用中文模型
```

```python
# 修改前
engine = EasyOCREngine(langs=['ch_sim', 'en'])

# 修改后
engine = EasyOCREngine(langs=['ch_sim'])  # 只使用中文模型
```

### 方案2：继续使用中英文混合

如果确实需要更好的英文识别效果，需要：

1. 等待英文模型下载完成（可能需要较长时间）
2. 或者手动下载英文模型文件放到 `D:\EasyOCR\` 目录

## 测试验证

创建测试文件 `tests/test_chinese_only_model.py` 来验证只使用中文模型的效果。

## 使用建议

1. **推荐使用方案1**（只使用中文模型）
2. 中文模型可以识别：
   - 中文字符 ✅
   - 英文字母 ✅
   - 数字 ✅
   - 常见符号 ✅
3. 如果遇到纯英文识别效果不佳，再考虑方案2

## 下次启动

修改后，下次启动应用时：
- 不会再尝试下载英文模型
- 直接使用已有的中文模型
- OCR识别速度会更快

## 相关文件

- `src/mistake_book/services/ocr_engine.py` - OCR引擎实现
- `tests/test_chinese_only_model.py` - 测试脚本
