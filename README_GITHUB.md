# 📊 Macro Investment Assistant

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**智能宏观投资分析系统 | AI-Powered Macro Investment Analysis Platform**

基于多因子模型和宏观叙事分析的智能化投资决策辅助系统，提供每日投资简报、市场情绪分析、预测验证等功能。

---

## 🌟 特性亮点

### 核心功能

- 📈 **多因子预测模型** - 整合宏观经济、市场情绪、资金流向等多维度数据
- 📰 **宏观叙事分析** - 自动识别政策类型，推导资产价格影响
- 📊 **每日投资简报** - 自动生成包含金价、基金、股票、新闻的综合报告
- 🔍 **预测验证系统** - 持续跟踪预测准确率，7/30/90 天统计分析
- 😱 **恐慌贪婪指数** - 5 指标加权综合市场情绪
- 📅 **重大事件日历** - 未来 7 天重要经济事件提醒
- 🤖 **API 服务** - RESTful API 支持第三方集成

### 数据源

| 类别 | 数据源 | 更新频率 |
|------|--------|----------|
| 金价 | 东方财富、金投网 | 实时 |
| 基金 | AKShare | 每日 |
| 股票 | 东方财富 | 实时 |
| 新闻 | 腾讯、百度、新浪、东方财富、和讯 | 每小时 |
| 宏观数据 | 美联储、统计局 | 按发布 |

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- macOS / Linux / Windows
- 网络访问（获取实时数据）

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

# 4. 安装 Playwright 浏览器
playwright install chromium

# 5. 测试运行
python3 main.py --help
```

### 生成每日简报

```bash
# 一键生成每日简报
./run_daily.sh

# 或手动运行
python3 main.py brief
```

### 查看 API 文档

```bash
# 启动 API 服务
./api/start.sh

# 访问文档
open http://localhost:8000/docs
```

---

## 📁 项目结构

```
macro-investment-assistant/
├── main.py                 # 主入口
├── run_daily.sh           # 每日运行脚本
├── requirements.txt       # Python 依赖
├── config.yaml           # 配置文件
│
├── analyzers/            # 分析模块
│   ├── macro.py          # 宏观分析
│   ├── macro_narrative.py # 宏观叙事分析
│   ├── fear_greed_index.py # 恐慌贪婪指数
│   └── ...
│
├── data_sources/         # 数据源模块
│   ├── gold_source.py    # 金价数据
│   ├── fund_source.py    # 基金数据
│   ├── news_source.py    # 新闻数据
│   └── ...
│
├── predictors/           # 预测模块
│   ├── multi_factor.py   # 多因子预测
│   ├── validator.py      # 预测验证
│   └── ...
│
├── presenters/           # 展示模块
│   ├── brief_generator_enhanced.py # 简报生成
│   └── ...
│
├── api/                  # API 服务
│   ├── main.py          # FastAPI 应用
│   └── ...
│
├── web/                  # Web 仪表盘
│   └── dashboard.html
│
├── docs/                 # 文档
│   ├── INDEX.md         # 文档索引
│   ├── CHANGELOG.md     # 更新日志
│   └── ...
│
└── tests/               # 测试用例
```

---

## 📊 系统版本

**当前版本**: V8.4.5 (2026-04-15)

### 最新版本变更

#### V8.4.5 - 预测逻辑优化版

**核心变更**:
- ✅ 取消震荡预测，只保留上涨/下跌
- ✅ 方向阈值从 ±1% 调整为 ±0.5%
- ✅ 预测区间从 ±2% 缩小到 ±1%
- ✅ 基金净值智能列名检测
- ✅ 北向资金实时获取（不再硬编码）

**效果对比**:
```
预测方向：上涨/下跌/震荡 → 上涨/下跌（更明确）
预测区间：±2% (4.2% 跨度) → ±1% (2.0% 跨度)（更精确）
基金净值：多只 0.0 → 全部有效（更可靠）
北向资金：固定 35.8 亿 → 实时获取（更真实）
```

[查看完整版本历史 →](docs/VERSION_HISTORY.md)

---

## 🔧 使用指南

### 命令行接口

```bash
# 查看帮助
python3 main.py --help

# 生成每日简报
python3 main.py brief

# 获取金价
python3 main.py gold

# 生成预测
python3 main.py predict

# 验证预测
python3 main.py verify

# 启动 API
python3 main.py api
```

### 配置选项

编辑 `config.yaml` 配置文件：

```yaml
# 数据源配置
data_sources:
  gold:
    primary: "eastmoney"
    fallback: "jin10"
  
  news:
    sources:
      - "tencent"
      - "baidu"
      - "sina"
      - "eastmoney"
      - "hexun"

# 预测配置
prediction:
  direction_threshold: 0.005  # ±0.5%
  prediction_interval: 0.01   # ±1%
  
# 告警配置
alerts:
  enabled: true
  price_change_threshold: 2.0  # 2%
```

---

## 📈 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                              │
│  CLI  │  Web Dashboard  │  API  │  Daily Brief          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    业务逻辑层                              │
│  预测引擎  │  分析器  │  验证器  │  告警系统              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据源层                                │
│  金价  │  基金  │  股票  │  新闻  │  宏观数据            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据存储层                              │
│  SQLite  │  JSON Cache  │  Logs                         │
└─────────────────────────────────────────────────────────┘
```

[查看完整架构文档 →](docs/ARCHITECTURE.md)

---

## 🧪 测试

```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试
python3 -m pytest tests/test_gold_source.py

# 生成覆盖率报告
python3 -m pytest --cov=. tests/
```

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [README.md](README.md) | 快速开始 |
| [docs/INDEX.md](docs/INDEX.md) | 完整文档索引 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 更新日志 |
| [docs/VERSION_HISTORY.md](docs/VERSION_HISTORY.md) | 版本历史 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统架构 |
| [docs/CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [api/API_GUIDE.md](api/API_GUIDE.md) | API 文档 |

---

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与项目开发。

### 贡献者

<!-- 这里会自动显示贡献者头像 -->
<!-- readme: contributors -start -->
<!-- readme: contributors -end -->

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- 📧 Email: [待添加]
- 💬 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/macro-investment-assistant/issues)
- 📖 Wiki: [项目 Wiki](https://github.com/YOUR_USERNAME/macro-investment-assistant/wiki)

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - API 框架
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [AKShare](https://akshare.akfamily.xyz/) - 金融数据接口
- [Matplotlib](https://matplotlib.org/) - 图表生成

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

[↑ 返回顶部](#-macro-investment-assistant)

</div>
