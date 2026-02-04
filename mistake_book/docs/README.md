# 📚 文档索引

欢迎查阅错题本项目文档！

## 📖 文档列表

### 🏗️ 架构与设计

1. **[architecture.md](architecture.md)** - 整体架构设计
   - 分层架构说明
   - MVVM模式
   - 设计原则

2. **[backend_services.md](backend_services.md)** - 后端服务架构
   - 数据持久层
   - 业务逻辑层
   - 外部服务层
   - 服务调用流程

3. **[database_design.md](database_design.md)** - 数据库设计
   - ER图
   - 表结构详解
   - 索引策略
   - 数据操作示例

4. **[gui_design.md](gui_design.md)** - GUI界面设计
   - 三栏布局
   - 组件详解
   - 交互流程
   - 无障碍设计

5. **[integration.md](integration.md)** - 前后端集成
   - 依赖注入
   - 数据流向
   - 错误处理
   - 使用示例

6. **[refactoring_services.md](refactoring_services.md)** - 服务层重构
   - 重构动机
   - 服务层设计
   - 代码对比
   - 最佳实践

7. **[ui_optimization.md](ui_optimization.md)** - UI层优化重构
   - 优化目标
   - 架构改进
   - UIService设计
   - 代码对比
   - 优化效果

8. **[core_layer_analysis.md](core_layer_analysis.md)** - Core层使用情况分析
   - 已使用模块分析
   - 未使用模块分析
   - 使用率统计
   - 改进建议

9. **[data_flow_fix.md](data_flow_fix.md)** - 数据流修复文档
   - 问题分析
   - 修复方案
   - 数据流验证
   - 测试验证

10. **[ui_refresh_fix.md](ui_refresh_fix.md)** - UI刷新问题修复
   - 问题描述
   - 根本原因
   - 修复方案
   - 测试验证

11. **[database_cache_fix.md](database_cache_fix.md)** - 数据库缓存问题修复
   - SQLAlchemy缓存机制
   - 问题分析
   - 修复方案（expire_all）
   - 性能考虑

### ✨ 功能文档

12. **[view_detail_feature.md](view_detail_feature.md)** - 查看错题详情功能
   - 功能概述
   - 架构设计
   - 实现细节
   - 使用流程

13. **[delete_question_feature.md](delete_question_feature.md)** - 删除错题功能
   - 功能概述
   - 架构设计
   - 安全考虑
   - 完整流程

14. **[card_click_interaction.md](card_click_interaction.md)** - 卡片点击交互优化
   - 优化目标
   - 实现方案
   - 代码变更

15. **[view_state_persistence.md](view_state_persistence.md)** - 视图状态持久化
   - 问题描述
   - 解决方案
   - 实现细节

16. **[navigation_selection_persistence.md](navigation_selection_persistence.md)** - 导航选中状态持久化
   - 问题分析
   - 解决方案
   - 实现逻辑

17. **[prevent_duplicate_save.md](prevent_duplicate_save.md)** - 防止重复保存
   - 问题描述
   - 解决方案
   - 用户体验改进

18. **[ocr_implementation.md](ocr_implementation.md)** - OCR功能实现
   - 架构设计
   - 三种OCR引擎
   - 图像预处理
   - 使用指南

19. **[auto_ocr_on_drop.md](auto_ocr_on_drop.md)** - 拖拽图片自动OCR
   - 功能说明
   - 实现细节
   - 用户体验

20. **[ocr_status_and_solutions.md](ocr_status_and_solutions.md)** - OCR引擎状态与解决方案
   - 当前状态诊断
   - 三种解决方案
   - 安装指南
   - 常见问题

21. **[tesseract_installation_guide.md](tesseract_installation_guide.md)** - Tesseract安装指南
   - 详细安装步骤
   - 验证方法
   - 常见问题

22. **[easyocr_dll_fix.md](easyocr_dll_fix.md)** - EasyOCR DLL错误修复
   - 问题诊断
   - 修复方法
   - 验证测试

23. **[easyocr_pyqt6_fix.md](easyocr_pyqt6_fix.md)** - ✅ EasyOCR与PyQt6冲突修复 ⭐ 重要
   - 问题根本原因
   - DLL加载顺序
   - 完整解决方案

24. **[chinese_path_fix.md](chinese_path_fix.md)** - ✅ 中文路径OCR识别修复 ⭐ 重要
   - OpenCV中文路径问题
   - numpy数组解决方案
   - 临时文件方案

25. **[image_upload_and_preview.md](image_upload_and_preview.md)** - ✅ 图片上传和预览功能 ⭐ 新增
   - 点击上传图片
   - 图片预览显示
   - 查看完整图片

26. **[image_loading_fix.md](image_loading_fix.md)** - ✅ 图片加载中文路径修复 ⭐ 新增
   - QPixmap中文路径问题
   - 使用PIL解决方案
   - 错误处理优化
   - 用户体验改进

27. **[ocr_simplification.md](ocr_simplification.md)** - OCR引擎简化说明
   - 删除PaddleOCR和Tesseract
   - 只保留EasyOCR
   - 代码简化70%

27. **[ocr_quick_start.md](ocr_quick_start.md)** - ✅ OCR功能快速开始 ⭐ 推荐
   - EasyOCR使用指南
   - 拖拽识别教程
   - 常见问题解答

28. **[ocr_lazy_loading.md](ocr_lazy_loading.md)** - ✅ OCR延迟加载优化 ⭐ 新增
   - 延迟加载原理
   - 技术实现细节
   - 性能提升效果
   - 使用流程说明

29. **[move_models_to_other_drive.md](move_models_to_other_drive.md)** - ✅ 模型路径配置 ⭐ 新增
   - 配置模型保存到其他盘符
   - 节省C盘空间
   - 环境变量设置

30. **[ocr_async_loading.md](ocr_async_loading.md)** - ✅ OCR异步加载 ⭐ 新增
   - 后台线程加载模型
   - UI不阻塞，保持响应
   - 用户体验显著提升
   - 线程安全实现

31. **[ocr_status_notification.md](ocr_status_notification.md)** - ✅ OCR状态通知 ⭐ 新增
   - 模型下载状态提示
   - 加载完成通知
   - 状态栏实时显示
   - 用户体验优化

32. **[ocr_model_path_fix.md](ocr_model_path_fix.md)** - ✅ OCR模型路径修复 ⭐ 新增
   - 模型路径配置问题修复
   - 显式传入model_storage_directory
   - 确保使用指定盘符

33. **[ocr_recognition_fix.md](ocr_recognition_fix.md)** - ✅ OCR识别流程修复 ⭐ 新增
   - 引擎状态管理问题修复
   - 前端识别逻辑优化
   - 异常情况处理完善
   - 用户体验改进

34. **[OCR使用指南.md](OCR使用指南.md)** - ✅ OCR使用快速指南 ⭐ 推荐
   - 快速开始步骤
   - 首次使用注意事项
   - 常见问题解答
   - 手动下载模型
   - 诊断工具使用

34. **[OCR功能总结.md](OCR功能总结.md)** - ✅ OCR功能完整总结 ⭐ 推荐
   - 所有OCR功能汇总
   - 问题修复记录
   - 优化历程总结
   - 完整技术方案

35. **[移动模型到D盘说明.md](移动模型到D盘说明.md)** - ✅ 移动模型操作说明 ⭐ 推荐
   - 详细操作步骤
   - 中文说明文档
   - 适合普通用户

### 👥 用户文档

23. **[user_manual.md](user_manual.md)** - 用户手册
   - 功能说明
   - 使用指南
   - 常见问题

### 🔧 开发文档

24. **[dev_setup.md](dev_setup.md)** - 开发环境搭建
   - 环境要求
   - 安装步骤
   - 开发工具

## 🗺️ 文档导航

### 新手入门
1. 先看 [README.md](../README.md) 了解项目
2. 查看 [user_manual.md](user_manual.md) 学习使用
3. 阅读 [gui_design.md](gui_design.md) 了解界面
4. **✅ 想用OCR功能？** 查看 [OCR使用指南.md](OCR使用指南.md) ⭐ 最推荐
5. **OCR详细教程？** 查看 [ocr_quick_start.md](ocr_quick_start.md)
6. **遇到OCR问题？** 查看 [ocr_status_and_solutions.md](ocr_status_and_solutions.md)
7. **了解延迟加载？** 查看 [ocr_lazy_loading.md](ocr_lazy_loading.md)
8. **模型路径配置？** 查看 [move_models_to_other_drive.md](move_models_to_other_drive.md) 或 [移动模型到D盘说明.md](移动模型到D盘说明.md)
9. **OCR功能总结？** 查看 [OCR功能总结.md](OCR功能总结.md)

### 开发者
1. 阅读 [architecture.md](architecture.md) 理解架构
2. 查看 [backend_services.md](backend_services.md) 了解后端
3. 参考 [database_design.md](database_design.md) 理解数据结构
4. 查看 [integration.md](integration.md) 了解前后端集成
5. 学习 [refactoring_services.md](refactoring_services.md) 了解服务层设计
6. 阅读 [ui_optimization.md](ui_optimization.md) 了解UI层优化
7. 查看 [core_layer_analysis.md](core_layer_analysis.md) 了解Core层使用情况
8. 阅读问题修复文档：
   - [data_flow_fix.md](data_flow_fix.md) - 数据流问题
   - [ui_refresh_fix.md](ui_refresh_fix.md) - UI刷新问题
   - [database_cache_fix.md](database_cache_fix.md) - 数据库缓存问题
9. 参考功能文档了解具体实现：
   - [view_detail_feature.md](view_detail_feature.md)
   - [delete_question_feature.md](delete_question_feature.md)
   - [card_click_interaction.md](card_click_interaction.md)
   - [view_state_persistence.md](view_state_persistence.md)
   - [navigation_selection_persistence.md](navigation_selection_persistence.md)
   - [prevent_duplicate_save.md](prevent_duplicate_save.md)
   - [ocr_implementation.md](ocr_implementation.md)
   - [auto_ocr_on_drop.md](auto_ocr_on_drop.md)
10. **OCR相关问题：**
   - [ocr_status_and_solutions.md](ocr_status_and_solutions.md) - 状态诊断和解决方案
   - [tesseract_installation_guide.md](tesseract_installation_guide.md) - Tesseract安装
   - [easyocr_dll_fix.md](easyocr_dll_fix.md) - EasyOCR修复
11. 按照 [dev_setup.md](dev_setup.md) 搭建环境

### 维护者
1. 所有开发者文档
2. 重点关注 [database_design.md](database_design.md) 的维护章节
3. 了解 [backend_services.md](backend_services.md) 的扩展建议

## 📂 文档结构

```
docs/
├── README.md                              # 本文件 - 文档索引
├── architecture.md                        # 架构设计
├── backend_services.md                    # 后端服务
├── database_design.md                     # 数据库设计
├── gui_design.md                          # GUI设计
├── integration.md                         # 前后端集成
├── refactoring_services.md                # 服务层重构
├── ui_optimization.md                     # UI层优化
├── core_layer_analysis.md                 # Core层分析
├── data_flow_fix.md                       # 数据流修复
├── ui_refresh_fix.md                      # UI刷新修复
├── database_cache_fix.md                  # 数据库缓存修复
├── view_detail_feature.md                 # 查看详情功能
├── delete_question_feature.md             # 删除错题功能
├── card_click_interaction.md              # 卡片点击交互
├── view_state_persistence.md              # 视图状态持久化
├── navigation_selection_persistence.md    # 导航选中持久化
├── prevent_duplicate_save.md              # 防止重复保存
├── ocr_implementation.md                  # OCR功能实现
├── ocr_simplification.md                  # OCR引擎简化
├── auto_ocr_on_drop.md                    # 拖拽自动OCR
├── ocr_quick_start.md                     # OCR快速开始 ⭐
├── ocr_lazy_loading.md                    # OCR延迟加载优化 ⭐
├── move_models_to_other_drive.md          # 模型路径配置 ⭐
├── ocr_async_loading.md                   # OCR异步加载 ⭐
├── ocr_status_notification.md             # OCR状态通知 ⭐
├── ocr_model_path_fix.md                  # OCR模型路径修复 ⭐
├── ocr_recognition_fix.md                 # OCR识别流程修复 ⭐
├── ocr_status_and_solutions.md            # OCR状态与解决方案
├── easyocr_pyqt6_fix.md                   # EasyOCR与PyQt6冲突修复 ⭐
├── easyocr_dll_fix.md                     # EasyOCR DLL修复
├── chinese_path_fix.md                    # 中文路径OCR识别修复 ⭐
├── image_upload_and_preview.md            # 图片上传和预览功能 ⭐
├── image_loading_fix.md                   # 图片加载中文路径修复 ⭐
├── OCR使用指南.md                         # OCR使用快速指南 ⭐ 最推荐
├── OCR功能总结.md                         # OCR功能完整总结 ⭐ 推荐
├── 移动模型到D盘说明.md                   # 移动模型操作说明 ⭐ 推荐
├── tesseract_installation_guide.md        # Tesseract安装指南
├── user_manual.md                         # 用户手册
└── dev_setup.md                           # 开发环境
```

## 🔗 相关链接

- [项目结构](../PROJECT_STRUCTURE.md) - 完整目录结构
- [安装指南](../README.md#快速开始) - 快速开始
- [依赖说明](../dependencies/README.md) - 依赖配置

## 💡 文档贡献

如果发现文档有误或需要补充，欢迎：
1. 提交 Issue
2. 发起 Pull Request
3. 联系维护者

## 📝 文档更新日志

- 2024-01 - 创建完整文档体系
- 添加架构、后端、数据库、GUI、集成文档
- 添加服务层重构文档
- 添加查看详情功能文档
- 添加删除错题功能文档
- 添加UI层优化重构文档
- 添加Core层使用情况分析文档
- 添加数据流修复文档
- 添加UI刷新问题修复文档
- 添加数据库缓存问题修复文档
- 添加卡片点击交互优化文档
- 添加视图状态持久化文档
- 添加导航选中状态持久化文档
- 添加防止重复保存文档
- 添加OCR功能实现文档
- 添加拖拽自动OCR文档
- 2026-02-04 - 添加OCR问题诊断和解决方案文档
  - ocr_status_and_solutions.md - OCR状态诊断和三种解决方案
  - tesseract_installation_guide.md - Tesseract详细安装指南
  - easyocr_dll_fix.md - EasyOCR DLL错误修复指南
  - ✅ ocr_quick_start.md - OCR功能快速开始指南（EasyOCR已可用）
  - ✅ easyocr_pyqt6_fix.md - EasyOCR与PyQt6冲突问题修复（已解决）
  - ✅ chinese_path_fix.md - 中文路径OCR识别问题修复（已解决）
  - ✅ image_upload_and_preview.md - 图片上传和预览功能（新增）
  - ✅ image_loading_fix.md - 图片加载中文路径修复（新增，QPixmap问题）
  - ✅ ocr_lazy_loading.md - OCR延迟加载优化（新增，启动速度提升10倍）
  - ✅ move_models_to_other_drive.md - 模型路径配置到其他盘符（新增）
  - ✅ ocr_async_loading.md - OCR异步加载优化（新增，UI不阻塞）
  - ✅ ocr_status_notification.md - OCR状态通知优化（新增，用户体验提升）
  - ✅ ocr_model_path_fix.md - OCR模型路径修复（新增，确保使用指定盘符）
  - ✅ ocr_recognition_fix.md - OCR识别流程修复（新增，状态管理优化）
  - ✅ OCR使用指南.md - OCR使用快速指南（最推荐）
  - ✅ OCR功能总结.md - OCR功能完整总结（所有功能汇总）
  - ✅ 移动模型到D盘说明.md - 移动模型操作说明（中文说明）
  - ocr_simplification.md - OCR引擎简化说明（只保留EasyOCR）
- 完善用户手册和开发指南
