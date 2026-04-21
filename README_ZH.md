# 📊 Macro Investment Assistant

<div align="center">

**面向中国市场的智能宏观投资分析平台**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Documentation](docs/INDEX.md) | [English](README.md) | [日本語](README_JA.md) | [Русский](README_RU.md)

</div>

---

## 🎯 项目简介

**Macro Investment Assistant** 是专为中国市场设计的智能投资决策辅助系统。结合多因子模型和宏观叙事分析，提供全面的投资洞察。

### 核心亮点

- 🇨 **中国优化**: 专为大陆网络环境设计，外网受限情况下仍可使用
- 📈 **多因子预测**: 整合宏观经济、市场情绪、资金流向
- 📰 **宏观叙事分析**: 政策→经济影响→资产价格→投资策略
- 📊 **每日简报**: 自动化投资报告（金价、基金、股票、新闻）
- 🔍 **预测验证**: 7/30/90 天准确率跟踪
- 🤖 **完整 API**: RESTful API 支持第三方集成

---

## 🌍 为什么需要这个项目？

### 问题

大多数投资分析工具面向全球市场，需要无限制的网络访问。中国大陆用户面临挑战：
- 国际金融数据 API 访问受限
- 海外服务网络延迟高
- 缺乏针对中国市场的分析

### 解决方案

这个项目**为中国而建，由中国而建**：
- ✅ **本地数据源**: 东方财富、AKShare、腾讯、新浪（全部国内）
- ✅ **离线优先**: 外网受限情况下仍可工作
- ✅ **聚焦中国市场**: A 股、国内金价、中国政策分析
- ✅ **中文支持**: 原生中文文档和技术支持

---

## 🚀 快速开始

### 安装（5 分钟）

```bash
# 克隆仓库
git clone https://github.com/anThreeBody/macro-investment-assistant.git
cd macro-investment-assistant

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装浏览器自动化
playwright install chromium

# 测试安装
python3 main.py --help
```

### 生成每日简报

```bash
# 一键生成简报
./run_daily.sh

# 或手动运行
python3 main.py brief
```

### 启动 API 服务

```bash
./api/start.sh
# 访问：http://localhost:8000/docs
```

---

## 📊 核心功能

### 1. 多因子预测模型

整合 4 个维度 10+ 因子：

| 维度 | 因子 | 权重 |
|------|------|------|
| **宏观经济** | GDP、CPI、PMI、利率 | 30% |
| **市场情绪** | 恐慌贪婪指数、VIX | 25% |
| **资金流向** | 北向资金、基金流向 | 25% |
| **技术面** | 价格趋势、成交量 | 20% |

### 2. 宏观叙事分析

自动政策分析 + 因果推理：

```
政策发布
    ↓
经济影响评估
    ↓
资产价格影响
    ↓
投资策略建议
```

**示例**：
```
📰 政策：央行降准 50 个基点
    ↓
💡 影响：流动性增加，借贷成本降低
    ↓
📈 资产：利好股票，利空债券收益率
    ↓
💼 策略：超配金融、可选消费
```

### 3. 每日投资简报

自动化综合报告包含：

- 📈 市场概览（上证、深证、创业板）
- 💰 金价（国际 + 国内）
- 📊 基金推荐（精选基金 + 分析）
- 📰 新闻摘要（5 大国内来源）
- 🔮 市场预测（方向 + 置信度）
- 📅 事件日历（未来 7 天）

### 4. 预测验证系统

透明的准确率跟踪：

| 周期 | 预测次数 | 正确次数 | 准确率 |
|------|---------|---------|--------|
| **7 天** | 5 | 3 | 60% |
| **30 天** | 22 | 13 | 59% |
| **90 天** | 65 | 38 | 58% |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                             │
│  CLI  │  Web 仪表盘  │  REST API  │  每日简报           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   业务逻辑层                             │
│  预测引擎  │  分析器  │  验证器  │  告警系统            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  数据源层（中国）                        │
│  东方财富  │  AKShare  │  腾讯  │  新浪  │  和讯      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                             │
│  SQLite 数据库  │  JSON 缓存  │  本地文件              │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
macro-investment-assistant/
├── 📄 核心文件
│   ├── main.py                 # 主入口
│   ├── run_daily.sh           # 每日运行脚本
│   ├── requirements.txt       # 依赖
│   └── config.yaml           # 配置文件
│
├── 🧠 分析模块
│   ├── analyzers/            # 分析引擎
│   │   ├── macro.py          # 宏观分析
│   │   ├── macro_narrative.py # 叙事分析 ⭐
│   │   └── fear_greed_index.py # 情绪指数
│   │
│   ├── predictors/           # 预测模型
│   │   ├── multi_factor.py   # 多因子预测
│   │   └── validator.py      # 预测验证
│   │
│   └── data_sources/         # 国内数据源
│       ├── gold_source.py    # 金价（东方财富）
│       ├── fund_source.py    # 基金净值（AKShare）
│       └── news_source.py    # 新闻（5 大来源）
│
├── 🌐 API 与 Web
│   ├── api/                  # REST API (FastAPI)
│   └── web/                  # Web 仪表盘
│
├── 📚 文档
│   ├── docs/                 # 技术文档
│   ├── README.md            # 英文文档
│   └── README_ZH.md         # 中文文档（当前）
│
└── 🧪 测试
    └── tests/               # 测试用例
```

---

## 📊 当前版本

**版本**: V8.4.5 (2026-04-15)

### 最新版本变更 (V8.4.5)

- ✅ **简化预测**: 取消震荡，只保留涨/跌（信号更清晰）
- ✅ **更敏感阈值**: 方向±0.5%（更敏感）
- ✅ **更精确区间**: 预测±1%（指导价值更高）
- ✅ **智能基金数据**: 自动检测 AKShare 列名（处理周末/假日）
- ✅ **实时北向资金**: 动态 API 获取（无硬编码）

[查看完整更新日志 →](docs/CHANGELOG.md)

---

## 🔧 使用示例

### 命令行

```bash
# 生成每日简报
python3 main.py brief

# 获取最新金价
python3 main.py gold

# 生成预测
python3 main.py predict

# 验证历史预测
python3 main.py verify

# 启动 API 服务
python3 main.py api
```

### 配置

编辑 `config.yaml`:

```yaml
data_sources:
  gold:
    primary: "eastmoney"    # 国内
    fallback: "jin10"       # 国内
  
  news:
    sources:
      - "tencent"           # 腾讯新闻
      - "baidu"             # 百度新闻
      - "sina"              # 新浪财经
      - "eastmoney"         # 东方财富
      - "hexun"             # 和讯网

prediction:
  direction_threshold: 0.005  # ±0.5%
  prediction_interval: 0.01   # ±1%
```

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [📖 文档索引](docs/INDEX.md) | 完整文档 |
| [📝 更新日志](docs/CHANGELOG.md) | 版本历史 |
| [🏗️ 架构设计](docs/ARCHITECTURE.md) | 系统设计 |
| [📊 版本历史](docs/VERSION_HISTORY.md) | 所有版本 |
| [🤝 贡献指南](CONTRIBUTING.md) | 参与贡献 |
| [🌐 API 文档](api/API_GUIDE.md) | API 说明 |

**语言版本**:
- [🇬🇧 English](README.md) - 英文版
- [🇨 中文](README_ZH.md) - 您在这里
- [🇯 日本語](README_JA.md) - 即将推出
- [🇷🇺 Русский](README_RU.md) - 即将推出

---

## 🧪 测试

```bash
# 运行所有测试
python3 -m pytest tests/

# 生成覆盖率报告
python3 -m pytest --cov=. tests/

# 特定测试
python3 -m pytest tests/test_gold_source.py
```

---

## 🤝 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

### 如何帮助

- 🐛 报告 Bug
- 💡 建议功能
- 📝 改进文档
- 🌍 翻译语言
- 💻 提交 PR

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

使用以下优秀的开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - API 框架
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [AKShare](https://akshare.akfamily.xyz/) - 中国金融数据
- [Matplotlib](https://matplotlib.org/) - 图表生成

---

<div align="center">

**如果您觉得这个项目有用，请给个 ⭐ Star 支持一下！**

为中国投资社区用心打造 ❤️

[↑ 返回顶部](#-macro-investment-assistant)

</div>
