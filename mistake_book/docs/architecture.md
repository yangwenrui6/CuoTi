# 架构设计

## 分层架构

### 1. 界面层 (UI Layer)
- 采用MVVM模式
- ViewModel负责数据绑定
- View只负责显示

### 2. 业务逻辑层 (Core Layer)
- 无GUI依赖
- 可独立测试
- 包含复习算法、数据管理等

### 3. 数据持久层 (Database Layer)
- SQLAlchemy ORM
- 事务管理
- 数据库备份

### 4. 服务层 (Services Layer)
- OCR识别
- 系统通知
- 云同步（预留）

## 设计原则

- 单一职责
- 依赖注入
- 接口抽象
