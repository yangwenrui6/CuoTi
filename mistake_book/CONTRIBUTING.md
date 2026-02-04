# 贡献指南

感谢你考虑为错题本项目做出贡献！

## 🤝 如何贡献

### 报告Bug

如果你发现了bug，请：
1. 检查 [Issues](https://github.com/yangwenrui6/CuoTi/issues) 是否已有相同问题
2. 如果没有，创建新Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 系统环境（OS、Python版本等）
   - 错误日志（如果有）

### 提出新功能

1. 先在Issues中讨论你的想法
2. 等待维护者反馈
3. 获得批准后再开始开发

### 提交代码

1. **Fork项目**
   ```bash
   # 在GitHub上Fork项目
   # 克隆你的Fork
   git clone https://github.com/你的用户名/CuoTi.git
   cd CuoTi/mistake_book
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **开发**
   ```bash
   # 安装开发依赖
   pip install -r dependencies/requirements-dev.txt
   
   # 进行开发
   # ...
   
   # 运行测试
   pytest tests/
   
   # 代码格式化
   black src/
   
   # 代码检查
   flake8 src/
   ```

4. **提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   # 或
   git commit -m "fix: 修复某个bug"
   ```

5. **推送并创建PR**
   ```bash
   git push origin feature/your-feature-name
   # 在GitHub上创建Pull Request
   ```

## 📝 代码规范

### Commit Message规范

使用约定式提交（Conventional Commits）：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat(review): 添加复习历史功能

- 实现复习记录保存
- 添加历史记录查看界面
- 支持从历史记录开始复习

Closes #123
```

### Python代码规范

- 遵循 [PEP 8](https://pep8.org/)
- 使用类型注解
- 编写文档字符串（docstring）
- 函数/方法保持简洁（<50行）
- 使用有意义的变量名

**示例**：
```python
def calculate_next_review(
    interval: int,
    repetitions: int,
    easiness_factor: float,
    result: ReviewResult
) -> tuple[int, int, float]:
    """
    计算下次复习时间
    
    Args:
        interval: 当前间隔天数
        repetitions: 重复次数
        easiness_factor: 难度因子
        result: 复习结果
    
    Returns:
        (新间隔, 新重复次数, 新难度因子)
    """
    # 实现...
    return new_interval, new_reps, new_ef
```

### 文件组织

- 每个模块一个文件
- 相关功能放在同一目录
- 使用`__init__.py`导出公共接口
- 测试文件与源文件对应

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_services/test_review_service.py

# 生成覆盖率报告
pytest --cov=src tests/
```

### 编写测试

- 为新功能编写测试
- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`
- 使用pytest fixtures

**示例**：
```python
def test_save_review_record(review_service):
    """测试保存复习记录"""
    # Arrange
    question_id = 1
    result = ReviewResult.GOOD
    
    # Act
    success, message, _ = review_service.process_review_result(
        question_id, result
    )
    
    # Assert
    assert success is True
    assert "成功" in message
```

## 📖 文档

### 更新文档

- 新功能需要更新相关文档
- 在`docs/`目录添加说明文档
- 更新`README.md`（如果需要）
- 更新`CHANGELOG.md`

### 文档格式

- 使用Markdown格式
- 添加代码示例
- 包含截图（如果适用）
- 保持简洁清晰

## 🎨 UI/UX贡献

### 设计原则

- 简洁直观
- 一致性
- 可访问性
- 响应式

### 提交设计

1. 在Issue中描述设计想法
2. 提供设计稿或原型
3. 说明设计理由
4. 等待反馈

## 🐛 Bug修复流程

1. 在Issue中确认bug
2. 创建修复分支
3. 编写测试重现bug
4. 修复bug
5. 确保测试通过
6. 提交PR

## ✅ PR检查清单

提交PR前确认：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] Commit message符合规范
- [ ] 代码已格式化（black）
- [ ] 通过代码检查（flake8）

## 📞 联系方式

- GitHub Issues: https://github.com/yangwenrui6/CuoTi/issues
- 邮箱: [维护者邮箱]

## 📄 许可证

贡献的代码将采用项目的MIT许可证。

---

再次感谢你的贡献！🎉
