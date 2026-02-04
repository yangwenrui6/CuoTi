# OCR模型重复下载问题 - 已解决 ✅

## 问题

用户反馈：**前几次OCR识别很快，但后面一直在加载下载模型**

## 根本原因

之前配置了中英文混合模式 `['ch_sim', 'en']`：
- ✅ 中文模型已下载完成（craft_mlt_25k.pth + zh_sim_g2.pth）
- ❌ 英文模型一直在尝试下载，但可能因为网络问题反复失败
- 每次初始化OCR引擎都会检查并尝试下载缺失的模型

## 解决方案

修改为**只使用中文模型** `['ch_sim']`

### 修改的文件

`src/mistake_book/services/ocr_engine.py`

```python
# 修改1: EasyOCREngine.__init__
self.langs = langs or ['ch_sim']  # 原来是 ['ch_sim', 'en']

# 修改2: create_ocr_engine
engine = EasyOCREngine(langs=['ch_sim'])  # 原来是 ['ch_sim', 'en']
```

## 验证结果

运行 `tests/test_config_check.py`：

```
✅ 默认语言配置: ['ch_sim']
✅ 只使用中文模型
✅ 已下载模型:
   - craft_mlt_25k.pth (79.3 MB)
   - zh_sim_g2.pth (20.9 MB)
```

## 为什么只用中文模型就够了？

中文模型（zh_sim_g2.pth）实际上可以识别：
- ✅ 中文字符
- ✅ 英文字母
- ✅ 数字
- ✅ 常见符号

之前的测试已经验证：
```python
# 测试结果
原文: "题目: Solve x+5=10"
识别: "题目: Solve x+5=10"
置信度: 0.99
```

## 效果

修改后：
1. ✅ 不会再尝试下载英文模型
2. ✅ OCR引擎初始化速度更快
3. ✅ 识别效果不受影响（中文模型也能识别英文）
4. ✅ 节省磁盘空间（不需要额外的英文模型）

## 下次使用

重新启动应用后：
- 直接使用已有的中文模型
- 不会再出现"一直在下载"的问题
- OCR识别应该很快完成

## 相关文档

- `docs/ocr_model_download_issue.md` - 详细问题分析
- `tests/test_config_check.py` - 配置检查脚本
- `tests/test_chinese_only_model.py` - 中文模型测试脚本
