# 错题本 v2.0 部署检查清单

## 📋 部署前检查

### 环境检查
- [ ] Python 3.9+ 已安装
- [ ] pip 已更新到最新版本
- [ ] Git 已安装（如果从源码安装）
- [ ] 磁盘空间充足（至少2GB）

### 依赖检查
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version

# 检查Git版本（可选）
git --version
```

## 🚀 快速部署（用户）

### Windows用户
- [ ] 下载项目或克隆仓库
- [ ] 双击运行 `install.bat`
- [ ] 等待安装完成（约2-5分钟）
- [ ] 运行 `python run.py` 启动应用
- [ ] 验证应用正常启动

### macOS/Linux用户
- [ ] 下载项目或克隆仓库
- [ ] 运行 `chmod +x install.sh`
- [ ] 运行 `./install.sh`
- [ ] 等待安装完成（约2-5分钟）
- [ ] 运行 `python run.py` 启动应用
- [ ] 验证应用正常启动

## 👨‍💻 开发环境部署

### 1. 获取代码
- [ ] 克隆仓库: `git clone https://github.com/yangwenrui6/CuoTi.git`
- [ ] 进入目录: `cd CuoTi/mistake_book`

### 2. 创建虚拟环境
- [ ] 创建: `python -m venv venv`
- [ ] 激活 (Windows): `venv\Scripts\activate`
- [ ] 激活 (macOS/Linux): `source venv/bin/activate`
- [ ] 验证: `which python` 或 `where python`

### 3. 安装依赖
- [ ] 基础依赖: `pip install -r dependencies/requirements.txt`
- [ ] 开发依赖: `pip install -r dependencies/requirements-dev.txt`
- [ ] 验证: `pip list`

### 4. 运行测试
- [ ] 所有测试: `pytest tests/`
- [ ] UI测试: `pytest tests/test_ui/`
- [ ] 服务测试: `pytest tests/test_services/`
- [ ] 验证: 所有测试通过

### 5. 启动应用
- [ ] 运行: `python run.py`
- [ ] 验证: 应用窗口正常显示
- [ ] 测试: 添加错题功能
- [ ] 测试: 复习功能
- [ ] 测试: OCR功能（可选）

## 📦 打包部署

### 1. 准备打包
- [ ] 确保所有测试通过
- [ ] 更新版本号（如需要）
- [ ] 更新CHANGELOG.md
- [ ] 提交所有更改

### 2. 执行打包
- [ ] 运行: `python scripts/build_exe.py`
- [ ] 等待打包完成（约5-10分钟）
- [ ] 检查: `dist/` 目录下有可执行文件

### 3. 测试可执行文件
- [ ] 运行可执行文件
- [ ] 测试基本功能
- [ ] 测试OCR功能
- [ ] 测试复习功能
- [ ] 检查日志文件

### 4. 分发准备
- [ ] 创建发布说明
- [ ] 准备安装文档
- [ ] 打包资源文件
- [ ] 创建安装包（可选）

## 🔍 功能验证

### 基础功能
- [ ] 应用启动正常
- [ ] 主窗口显示正常
- [ ] 导航树加载正常
- [ ] 筛选面板工作正常
- [ ] 统计面板显示正常

### 错题管理
- [ ] 添加错题功能
- [ ] 查看错题详情
- [ ] 编辑错题信息
- [ ] 删除错题功能
- [ ] 搜索错题功能

### 复习功能
- [ ] 模块选择器显示
- [ ] 选择科目和题型
- [ ] 复习对话框显示
- [ ] 掌握度评分功能
- [ ] 复习历史查看
- [ ] 继续复习功能

### OCR功能（可选）
- [ ] OCR引擎初始化
- [ ] 拖拽图片识别
- [ ] 点击上传识别
- [ ] 中文识别正常
- [ ] 英文识别正常
- [ ] 混合文本识别

### UI组件
- [ ] ImageUploader组件
- [ ] OCRPanel组件
- [ ] QuestionForm组件
- [ ] FilterPanel组件
- [ ] StatisticsPanel组件
- [ ] NavigationTree组件

### 对话框
- [ ] 添加错题对话框
- [ ] 详情对话框
- [ ] 复习对话框
- [ ] 模块选择器
- [ ] 复习历史对话框

## 🐛 常见问题检查

### 安装问题
- [ ] Python版本正确（3.9+）
- [ ] pip可以正常使用
- [ ] 网络连接正常
- [ ] 磁盘空间充足

### 运行问题
- [ ] 虚拟环境已激活
- [ ] 依赖已正确安装
- [ ] 数据库文件可访问
- [ ] 日志文件可写入

### OCR问题
- [ ] EasyOCR已安装
- [ ] 模型文件已下载
- [ ] 模型路径正确
- [ ] 内存充足（2GB+）

### 打包问题
- [ ] PyInstaller已安装
- [ ] 所有依赖已安装
- [ ] 资源文件路径正确
- [ ] 隐藏导入配置正确

## 📊 性能检查

### 启动性能
- [ ] 启动时间 < 3秒
- [ ] 内存占用 < 150MB
- [ ] CPU占用正常

### 运行性能
- [ ] UI响应流畅
- [ ] 搜索速度快
- [ ] 复习流程顺畅
- [ ] OCR识别速度可接受

### 打包体积
- [ ] Windows: < 150MB
- [ ] macOS: < 150MB
- [ ] Linux: < 150MB

## 📝 文档检查

### 用户文档
- [ ] README.md 更新
- [ ] QUICKSTART.md 准确
- [ ] DEPLOYMENT.md 完整
- [ ] 常见问题已覆盖

### 开发文档
- [ ] PROJECT_STRUCTURE.md 更新
- [ ] CONTRIBUTING.md 清晰
- [ ] API文档完整
- [ ] 测试文档完善

### 更新日志
- [ ] CHANGELOG.md 更新
- [ ] 版本号正确
- [ ] 更新内容详细
- [ ] 发布日期准确

## ✅ 最终检查

### 代码质量
- [ ] 所有测试通过
- [ ] 代码格式化完成
- [ ] 代码检查通过
- [ ] 无明显Bug

### 文档完整性
- [ ] 所有文档已更新
- [ ] 链接正确有效
- [ ] 示例代码可运行
- [ ] 截图清晰准确

### 发布准备
- [ ] 版本号已更新
- [ ] 更新日志已完成
- [ ] 发布说明已准备
- [ ] 分发渠道已确定

## 🎯 部署完成标志

- ✅ 所有检查项通过
- ✅ 应用正常运行
- ✅ 功能完整可用
- ✅ 文档准确完整
- ✅ 性能符合预期

## 📞 问题反馈

如果遇到问题：
1. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 常见问题
2. 查看 [docs/](docs/) 相关文档
3. 提交 GitHub Issue
4. 联系维护者

---

**版本**: v2.0.0  
**最后更新**: 2026年2月9日  
**维护者**: Kiro AI Assistant

