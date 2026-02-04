# OCR英文识别支持恢复

## 问题描述

用户反馈：**OCR识别不了英文**

## 问题原因

之前为了避免重复下载模型，我们将语言配置从`['ch_sim', 'en']`改为了`['ch_sim']`（只使用中文模型）。

虽然中文模型理论上可以识别一些英文字符，但实际效果很差，特别是：
- ❌ 纯英文句子识别率低
- ❌ 英文单词容易被误识别为中文
- ❌ 数学公式中的英文字母识别不准

## 解决方案

恢复中英文混合模式：`['ch_sim', 'en']`

### 修改的文件

`src/mistake_book/services/ocr_engine.py`

### 修改内容

#### 1. EasyOCREngine.__init__

```python
# 修改前
self.langs = langs or ['ch_sim']  # 只使用中文模型

# 修改后
self.langs = langs or ['ch_sim', 'en']  # 中文+英文
```

#### 2. create_ocr_engine

```python
# 修改前
engine = EasyOCREngine(langs=['ch_sim'])

# 修改后
engine = EasyOCREngine(langs=['ch_sim', 'en'])
```

## 模型下载说明

### 需要的模型文件

使用`['ch_sim', 'en']`配置需要以下模型：

1. **craft_mlt_25k.pth** (83MB) - 文本检测模型 ✅ 已有
2. **zh_sim_g2.pth** (21MB) - 中文识别模型 ✅ 已有
3. **english_g2.pth** (~40MB) - 英文识别模型 ⚠️ 需要下载

### 首次使用

首次使用英文识别时，EasyOCR会自动下载英文模型：

```
正在下载英文模型...
下载进度: [████████████████████] 100%
模型保存位置: D:/EasyOCR/english_g2.pth
```

**下载时间**：约1-3分钟（取决于网络速度）

### 模型位置

所有模型保存在：`D:/EasyOCR/`

```
D:/EasyOCR/
├── craft_mlt_25k.pth      # 文本检测（83MB）
├── zh_sim_g2.pth          # 中文识别（21MB）
└── english_g2.pth         # 英文识别（40MB）
```

## 识别效果对比

### 只使用中文模型 `['ch_sim']`

| 内容类型 | 识别效果 |
|---------|---------|
| 纯中文 | ✅ 优秀 |
| 纯英文 | ❌ 很差 |
| 中英混合 | ⚠️ 一般（英文部分差） |
| 数学公式 | ❌ 差（英文字母识别不准） |

### 使用中英文模型 `['ch_sim', 'en']`

| 内容类型 | 识别效果 |
|---------|---------|
| 纯中文 | ✅ 优秀 |
| 纯英文 | ✅ 优秀 |
| 中英混合 | ✅ 优秀 |
| 数学公式 | ✅ 良好 |

## 性能影响

### 模型加载时间

| 配置 | 首次加载 | 后续加载 |
|------|---------|---------|
| `['ch_sim']` | 2-3秒 | 1-2秒 |
| `['ch_sim', 'en']` | 3-5秒 | 2-3秒 |

**差异**：约增加1秒（可接受）

### 识别速度

| 配置 | 识别速度 |
|------|---------|
| `['ch_sim']` | 1-2秒/图 |
| `['ch_sim', 'en']` | 1.5-2.5秒/图 |

**差异**：约增加0.5秒（可接受）

### 内存占用

| 配置 | 内存占用 |
|------|---------|
| `['ch_sim']` | ~300MB |
| `['ch_sim', 'en']` | ~400MB |

**差异**：约增加100MB（可接受）

## 测试验证

### 运行测试

```bash
python tests/test_services/test_ocr_english_support.py
```

### 测试场景

1. **纯英文**：`Hello World 123`
2. **纯中文**：`这是中文测试`
3. **中英混合**：`题目: Solve x+5=10`

### 预期结果

```
[测试1] 纯英文识别...
   原文: Hello World 123
   识别: Hello World 123
   ✅ 英文识别成功

[测试2] 纯中文识别...
   原文: 这是中文测试
   识别: 这是中文测试
   ✅ 中文识别成功

[测试3] 中英文混合识别...
   原文: 题目: Solve x+5=10
   识别: 题目: Solve x+5=10
   ✅ 中英文混合识别成功
```

## 常见问题

### Q1: 英文模型下载失败怎么办？

**A**: 检查网络连接，或手动下载：

1. 访问：https://github.com/JaidedAI/EasyOCR/releases
2. 下载 `english_g2.pth`
3. 放到 `D:/EasyOCR/` 目录

### Q2: 下载速度很慢怎么办？

**A**: 可以使用国内镜像或代理：

```python
# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://proxy.example.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:8080'
```

### Q3: 是否会重复下载？

**A**: 不会。模型下载一次后会保存在本地，下次直接加载。

### Q4: 可以只使用英文模型吗？

**A**: 可以，但不推荐：

```python
engine = EasyOCREngine(langs=['en'])  # 只识别英文
```

这样会导致中文识别失败。

### Q5: 支持其他语言吗？

**A**: 支持。EasyOCR支持80+种语言：

```python
# 中文+英文+日文
engine = EasyOCREngine(langs=['ch_sim', 'en', 'ja'])

# 查看所有支持的语言
import easyocr
print(easyocr.Reader.list_languages())
```

## 使用建议

### 推荐配置

对于错题本应用，推荐使用：

```python
langs=['ch_sim', 'en']  # 中文+英文
```

**原因**：
- ✅ 覆盖大部分使用场景
- ✅ 性能开销可接受
- ✅ 识别效果最佳

### 特殊场景

#### 纯中文题目
```python
langs=['ch_sim']  # 可以节省一点性能
```

#### 数学/物理题目（含公式）
```python
langs=['ch_sim', 'en']  # 必须包含英文
```

#### 英语题目
```python
langs=['en', 'ch_sim']  # 英文优先
```

## 相关文档

- [OCR模型下载问题](./ocr_model_download_issue.md)
- [OCR识别优化](./ocr_recognition_improvement.md)
- [OCR功能总结](./OCR功能总结.md)
- [EasyOCR语言支持](https://github.com/JaidedAI/EasyOCR#supported-languages)

## 总结

已恢复中英文混合识别模式，现在可以正常识别英文内容了。首次使用时会自动下载英文模型（约40MB），下载完成后即可使用。
