# UI层重构 - 实施任务

## 概述

本任务列表将UI层重构分解为可执行的编码任务。每个任务都是增量式的，确保代码始终处于可工作状态。

## 任务列表

- [x] 1. 创建基础组件 - ImageUploader
  - 创建 `ui/components/` 目录结构
  - 实现 `ImageUploader` 组件，支持拖拽、点击上传、图片预览
  - 使用PIL处理中文路径问题
  - 提供 `image_selected` 信号接口
  - _Requirements: 2.1, 3.2_

- [x] 1.1 为ImageUploader编写单元测试
  - 测试组件独立实例化
  - 测试图片加载和信号发送
  - 测试中文路径处理
  - _Requirements: 3.1_

- [x] 2. 创建OCRPanel组件
  - 实现 `OCRPanel` 组件，封装OCR识别UI
  - 在后台线程执行OCR识别
  - 提供 `recognition_completed` 和 `recognition_failed` 信号
  - 处理OCR引擎未初始化的情况
  - _Requirements: 2.2, 3.2_

- [x] 2.1 为OCRPanel编写单元测试
  - 测试组件独立实例化
  - 测试mock OCR服务
  - 测试信号发送
  - _Requirements: 3.1, 3.3_

- [x] 3. 创建QuestionForm组件
  - 实现 `QuestionForm` 组件，包含所有题目输入字段
  - 实现 `get_data()` 和 `set_data()` 方法
  - 实现 `validate()` 方法进行数据验证
  - 提供 `data_changed` 信号
  - _Requirements: 2.3, 3.2_

- [x] 3.1 为QuestionForm编写单元测试
  - **Property 12: QuestionForm数据往返一致性**
  - **Validates: Requirements 2.3**
  - 测试 set_data() 后 get_data() 返回相同数据
  - 测试表单验证逻辑
  - _Requirements: 3.1_

- [x] 4. 创建FilterPanel组件
  - 实现 `FilterPanel` 组件，包含科目、难度、掌握度筛选
  - 从UIService获取筛选选项
  - 提供 `filter_changed` 信号
  - 实现 `get_filters()` 和 `reset_filters()` 方法
  - _Requirements: 2.3, 3.2_

- [x] 4.1 为FilterPanel编写单元测试
  - 测试组件独立实例化
  - 测试筛选条件获取
  - 测试信号发送
  - _Requirements: 3.1_

- [x] 5. 创建StatisticsPanel组件
  - 实现 `StatisticsPanel` 组件，显示统计信息
  - 从UIService获取统计数据
  - 实现 `update_statistics()` 方法
  - _Requirements: 2.3, 3.2_

- [x] 5.1 为StatisticsPanel编写单元测试
  - 测试组件独立实例化
  - 测试统计数据显示
  - _Requirements: 3.1_

- [x] 6. 创建NavigationTree组件
  - 实现 `NavigationTree` 组件，显示科目、标签、掌握度分类
  - 从UIService获取导航数据
  - 提供 `item_selected` 信号
  - 实现 `refresh()` 方法保持选中状态
  - _Requirements: 2.3, 3.2_

- [x] 6.1 为NavigationTree编写单元测试
  - 测试组件独立实例化
  - 测试导航数据加载
  - 测试选中项信号
  - _Requirements: 3.1_

- [x] 7. Checkpoint - 验证所有组件
  - 确保所有组件测试通过
  - 验证组件可以独立实例化
  - 检查代码质量（行数、复杂度）
  - 询问用户是否有问题

- [x] 8. 创建AddQuestionController
  - 创建 `ui/dialogs/add_question/` 目录
  - 实现 `AddQuestionController` 类
  - 实现 `on_image_selected()` 方法
  - 实现 `on_ocr_completed()` 方法
  - 实现 `save_question()` 方法，调用QuestionService
  - 集成EventBus发布QuestionAddedEvent
  - _Requirements: 1.3, 4.2, 4.3_

- [x] 8.1 为AddQuestionController编写单元测试
  - **Property 10: Controller可独立测试**
  - **Validates: Requirements 3.1, 3.3**
  - 测试使用mock服务
  - 测试保存逻辑
  - 测试事件发布
  - _Requirements: 3.1, 3.3_

- [x] 9. 创建AddQuestionDialog
  - 实现 `AddQuestionDialog` 类，使用新组件
  - 组装ImageUploader、OCRPanel、QuestionForm
  - 连接信号到Controller方法
  - 实现保存按钮逻辑
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 4.1_

- [x] 9.1 为AddQuestionDialog编写集成测试
  - 测试对话框与Controller集成
  - 测试组件信号连接
  - 测试完整的添加流程
  - _Requirements: 3.1_

- [x] 10. 创建DetailDialogController
  - 创建 `ui/dialogs/detail/` 目录
  - 实现 `DetailDialogController` 类
  - 实现 `has_changes()` 方法
  - 实现 `save_changes()` 方法
  - 集成EventBus发布QuestionUpdatedEvent
  - _Requirements: 1.3, 4.2, 4.3_

- [x] 10.1 为DetailDialogController编写单元测试
  - 测试使用mock服务
  - 测试变化检测
  - 测试保存逻辑
  - _Requirements: 3.1, 3.3_

- [x] 11. 创建DetailDialog
  - 实现 `DetailDialog` 类，使用Controller
  - 实现可编辑的题目内容、答案、解析
  - 实现保存和关闭逻辑
  - 处理未保存变化的提示
  - _Requirements: 1.1, 4.1_

- [x] 12. 创建ReviewDialogController
  - 创建 `ui/dialogs/review/` 目录
  - 实现 `ReviewDialogController` 类
  - 实现 `get_current_question()` 方法
  - 实现 `submit_review()` 方法
  - 实现 `get_progress()` 方法
  - 集成EventBus发布ReviewCompletedEvent
  - _Requirements: 1.3, 4.2, 4.3_

- [x] 12.1 为ReviewDialogController编写单元测试
  - 测试使用mock服务
  - 测试复习流程
  - 测试进度跟踪
  - _Requirements: 3.1, 3.3_

- [x] 13. 创建ReviewDialog
  - 实现 `ReviewDialog` 类，使用Controller
  - 实现题目显示和答案提交
  - 实现进度显示
  - 实现质量评分按钮
  - _Requirements: 1.1, 4.1_

- [x] 14. Checkpoint - 验证所有对话框
  - 确保所有对话框测试通过
  - 验证Dialog-Controller分离
  - 检查代码质量（行数、复杂度）
  - 询问用户是否有问题

- [x] 15. 创建MainWindowController
  - 创建 `ui/main_window/` 目录
  - 实现 `MainWindowController` 类
  - 实现视图状态管理（current_view_type, current_filters）
  - 实现 `load_questions()` 方法
  - 实现 `on_search()` 方法
  - 实现 `on_nav_filter_changed()` 方法
  - 实现 `on_filter_changed()` 方法
  - 实现 `refresh_current_view()` 方法
  - 实现 `show_add_dialog()` 和 `start_review()` 方法
  - 订阅EventBus事件（QuestionAdded, Updated, Deleted）
  - _Requirements: 1.3, 4.2, 4.3_

- [x] 15.1 为MainWindowController编写单元测试
  - 测试使用mock服务
  - 测试视图状态管理
  - 测试事件订阅和处理
  - _Requirements: 3.1, 3.3_

- [x] 16. 创建PanelFactory
  - 实现 `PanelFactory` 类
  - 实现 `create_navigation_panel()` 方法
  - 实现 `create_card_panel()` 方法
  - 实现 `create_right_panel()` 方法
  - _Requirements: 1.3, 2.1, 2.2, 2.3_

- [x] 17. 创建MainWindow
  - 实现 `MainWindow` 类，使用Controller和PanelFactory
  - 创建工具栏和菜单
  - 组装三栏布局（导航、卡片、筛选统计）
  - 连接信号到Controller方法
  - _Requirements: 1.1, 4.1_

- [x] 17.1 为MainWindow编写集成测试
  - 测试主窗口与Controller集成
  - 测试面板创建和布局
  - 测试信号连接
  - _Requirements: 3.1_

- [x] 18. Checkpoint - 验证主窗口
  - 确保主窗口测试通过
  - 验证所有面板正常工作
  - 检查代码质量（行数、复杂度）
  - 询问用户是否有问题

- [x] 19. 创建EventBus
  - 创建 `ui/events/` 目录
  - 实现 `EventBus` 单例类
  - 实现 `subscribe()` 方法
  - 实现 `unsubscribe()` 方法
  - 实现 `publish()` 方法
  - 添加错误处理，避免单个处理器失败影响其他处理器
  - _Requirements: 4.2_

- [x] 19.1 为EventBus编写单元测试
  - **Property 7: 事件总线解耦通信**
  - **Validates: Requirements 4.2**
  - 测试订阅和发布
  - 测试多个订阅者
  - 测试错误处理
  - _Requirements: 4.2_

- [x] 20. 定义所有事件类型
  - 在 `ui/events/events.py` 中定义Event基类
  - 定义QuestionAddedEvent
  - 定义QuestionUpdatedEvent
  - 定义QuestionDeletedEvent
  - 定义ReviewCompletedEvent
  - 定义OCRCompletedEvent
  - 使用dataclass装饰器
  - _Requirements: 4.2_

- [x] 21. 创建DialogFactory
  - 创建 `ui/factories/` 目录
  - 实现 `DialogFactory` 类
  - 实现 `create_add_question_dialog()` 方法
  - 实现 `create_detail_dialog()` 方法
  - 实现 `create_review_dialog()` 方法
  - 实现 `create_review_module_selector()` 方法
  - 注入服务和EventBus依赖
  - _Requirements: 4.1, 4.3_

- [x] 21.1 为DialogFactory编写单元测试
  - **Property 6: 工厂模式创建对话框**
  - **Validates: Requirements 4.1**
  - 测试对话框创建
  - 测试依赖注入
  - _Requirements: 4.1_

- [x] 22. 更新main.py使用新架构
  - 创建服务实例（QuestionService, ReviewService, UIService）
  - 创建EventBus实例
  - 创建DialogFactory实例
  - 创建MainWindowController实例
  - 创建MainWindow实例
  - 启动应用
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 23. Checkpoint - 验证完整集成
  - 确保应用可以启动
  - 测试添加错题流程
  - 测试查看详情流程
  - 测试复习流程
  - 测试筛选和搜索
  - 询问用户是否有问题

- [x] 24. 编写属性测试 - 组件独立性
  - **Property 1: 组件可独立实例化**
  - **Validates: Requirements 3.2**
  - 使用Hypothesis生成随机测试数据
  - 测试所有组件可以独立实例化
  - 运行至少100次迭代
  - _Requirements: 3.2_

- [x] 25. 编写属性测试 - 依赖注入
  - **Property 2: 组件接受依赖注入**
  - **Validates: Requirements 4.3**
  - 测试组件接受mock服务
  - 测试组件不在内部创建服务
  - _Requirements: 4.3_

- [x] 26. 编写属性测试 - 组件复用
  - **Property 3: 组件可在多处复用**
  - **Validates: Requirements 2.1, 2.2, 2.3**
  - 测试组件可以多次实例化
  - 测试实例间互不干扰
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 27. 编写代码质量检查脚本
  - **Property 4: 组件文件行数限制**
  - **Property 5: 方法行数限制**
  - **Validates: Requirements 1.1, 1.2**
  - 编写脚本检查所有文件行数
  - 编写脚本检查所有方法行数
  - 生成报告
  - _Requirements: 1.1, 1.2_

- [x] 28. 编写属性测试 - Dialog-Controller分离
  - **Property 8: Dialog只包含UI代码**
  - **Property 9: Controller处理业务逻辑**
  - **Validates: Requirements 1.3**
  - 通过代码分析验证Dialog不包含业务逻辑
  - 通过代码分析验证Controller不包含UI代码
  - _Requirements: 1.3_

- [x] 29. 编写属性测试 - 信号接口
  - **Property 11: 组件提供清晰信号接口**
  - **Validates: Requirements 2.1, 2.2, 2.3**
  - 测试所有组件通过信号暴露状态变化
  - 测试信号参数类型正确
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 30. 运行完整测试套件
  - 运行所有单元测试
  - 运行所有属性测试
  - 运行所有集成测试
  - 生成覆盖率报告
  - 确保覆盖率达标（组件>70%, Controller>80%）

- [x] 31. 代码审查和优化
  - 审查所有新代码
  - 检查代码质量指标
  - 优化性能瓶颈
  - 添加必要的注释和文档字符串

- [x] 32. 编写组件使用文档
  - 为每个组件编写使用示例
  - 编写迁移指南
  - 更新README
  - 更新CHANGELOG

- [x] 33. 标记旧代码为deprecated
  - 在旧的main_window.py添加deprecation警告
  - 在旧的add_dialog.py添加deprecation警告
  - 在旧的detail_dialog.py添加deprecation警告
  - 提供迁移路径说明

- [x] 34. 最终验收测试
  - 完整的端到端测试
  - 性能测试（UI响应时间、内存使用）
  - 用户验收测试
  - 确保所有功能正常工作

- [x] 35. 清理和发布
  - 删除旧代码（在确认新版本稳定后）
  - 更新版本号
  - 更新文档
  - 发布新版本

## 注意事项

- 标记 `*` 的任务为可选测试任务，可以跳过以加快MVP开发
- 每个任务都引用了具体的需求编号，确保可追溯性
- Checkpoint任务用于验证阶段性成果，确保增量开发
- 属性测试任务明确标注了对应的设计属性编号
- 所有任务都是编码任务，可以由代码生成LLM执行

## 成功标准

- ✅ 所有组件文件不超过200行
- ✅ 所有方法不超过30行
- ✅ 测试覆盖率达标
- ✅ 所有12个属性测试通过
- ✅ 应用功能完整且稳定
- ✅ 性能指标达标

