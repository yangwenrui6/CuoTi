# 快速开始指南

## 🎯 5分钟快速部署

### Windows用户

1. **安装Python**（如果还没有）
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **下载项目**
   ```cmd
   git clone https://github.com/yangwenrui6/CuoTi.git
   cd CuoTi\mistake_book
   ```

3. **一键安装**
   ```cmd
   install.bat
   ```

4. **运行应用**
   ```cmd
   python run.py
   ```

### macOS/Linux用户

```bash
# 1. 下载项目
git clone https://github.com/yangwenrui6/CuoTi.git
cd CuoTi/mistake_book

# 2. 一键安装
chmod +x install.sh
./install.sh

# 3. 运行应用
python run.py
```

---

## ✅ 验证安装

运行后应该看到：
- ✅ 主窗口打开
- ✅ 可以添加错题
- ✅ 可以开始复习

---

## 🔧 可选：启用OCR功能

```bash
# 安装OCR依赖
pip install easyocr

# 首次使用会自动下载模型（约200MB）
# 拖拽图片到添加错题界面即可识别文字
```

---

## 📖 下一步

- 阅读 [用户手册](docs/user_manual.md) 了解所有功能
- 查看 [部署指南](DEPLOYMENT.md) 了解详细配置
- 遇到问题？查看 [常见问题](DEPLOYMENT.md#常见问题)

---

## 🆘 需要帮助？

- 查看完整文档：[DEPLOYMENT.md](DEPLOYMENT.md)
- 提交问题：https://github.com/yangwenrui6/CuoTi/issues
