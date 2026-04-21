# 贡献指南

感谢您对 Macro Investment Assistant 项目的关注！本文档将指导您如何为项目做出贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [社区](#社区)

---

## 行为准则

本项目采用开源社区行为准则。请保持尊重、包容和专业的态度参与项目讨论和开发。

---

## 如何贡献

### 报告问题

发现 Bug？请创建 Issue 并包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）
- 日志输出（如有）

### 提出新功能

欢迎提出新功能建议！请创建 Issue 说明：
- 功能描述
- 使用场景
- 预期效果
- 可能的实现方案

### 提交代码

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 开发环境设置

### 前置要求

- Python 3.9+
- pip
- Git

### 安装步骤

```bash
# 1. Clone 项目
git clone https://github.com/YOUR_USERNAME/macro-investment-assistant.git
cd macro-investment-assistant

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright
playwright install chromium

# 5. 运行测试
python3 -m pytest tests/
```

---

## 提交规范

### Commit Message 格式

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是 Bug 修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 示例

```
feat(predictor): 添加宏观叙事分析功能

- 实现 MacroNarrativeAnalyzer 类
- 集成到每日简报生成流程
- 添加相关政策新闻识别

Closes #123
```

```
fix(data-source): 修复基金净值获取失败问题

- 修复 AKShare 动态列名检测
- 添加周末/假日数据处理

Fixes #456
```

---

## Pull Request 流程

### PR 标题

使用清晰的标题描述更改内容，遵循 Commit Message 规范。

### PR 描述

请包含：
- 更改描述
- 相关 Issue 链接
- 测试截图或日志（如适用）
-  Checklist

### PR Checklist

- [ ] 代码通过测试
- [ ] 添加了必要的测试用例
- [ ] 文档已更新
- [ ] 遵循项目代码规范
- [ ] 无敏感信息泄露

### 代码审查

所有 PR 都需要经过代码审查。审查者会检查：
- 代码质量
- 功能正确性
- 测试覆盖率
- 文档完整性

---

## 社区

### 讨论

欢迎在 GitHub Discussions 中参与讨论：
- 功能建议
- 使用问题
- 最佳实践分享

### 联系方式

- GitHub Issues: [问题反馈](https://github.com/YOUR_USERNAME/macro-investment-assistant/issues)
- Email: [待添加]

---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

感谢您的贡献！🎉
