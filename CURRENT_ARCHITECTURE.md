# 投资分析系统 - 当前架构总览

**版本**: V8.1.0  
**更新日期**: 2026-03-31  
**系统健康度**: 99%  
**成熟度**: Level 4 (生产就绪)

---

## 🏗️ 四层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        投资预测系统 V8.1                         │
│                   Macro-Investment-Assistant                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  第 1 层：用户接口层 (User Interface)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  main.py   │  │  CLI 命令   │  │  Python API │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  第 2 层：业务编排层 (Business Orchestration)               │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              InvestmentSystem (main.py)            │  │  │
│  │  │  协调数据获取 → 分析 → 预测 → 输出 → 通知            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  第 3 层：核心功能层 (Core Functions)                       │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  数据源层    │  │  分析层      │  │  预测层      │  │  │
│  │  │  (12 模块)   │  │  (6 模块)    │  │  (5 模块)    │  │  │
│  │  │              │  │              │  │              │  │  │
│  │  │ gold_source  │  │ technical    │  │ multi_factor │  │  │
│  │  │ fund_source  │  │ sentiment    │  │ simple_ts    │  │  │
│  │  │ stock_source │  │ macro        │  │ validator    │  │  │
│  │  │ news_source  │  │ momentum     │  │              │  │  │
│  │  │ macro_source │  │              │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  数据管道    │  │  输出层      │  │  通知层      │  │  │
│  │  │  (3 模块)    │  │  (3 模块)    │  │  (3 模块)    │  │  │
│  │  │              │  │              │  │              │  │  │
│  │  │ cleaner      │  │ brief_gen    │  │ alert_       │  │  │
│  │  │ validator    │  │ chart_gen    │  │ notifier     │  │  │
│  │  │ storage      │  │              │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  第 4 层：基础设施层 (Infrastructure)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  SQLite    │  │ JSON 缓存   │  │  日志系统  │         │  │
│  │  │  (data/)   │  │  (data/)   │  │  (logs/)   │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 模块清单

### 第 1 层：用户接口层

| 模块 | 文件 | 行数 | 功能 |
|------|------|------|------|
| **主入口** | `main.py` | ~200 | CLI 命令、Python API |
| **运行脚本** | `run_daily_v8.sh` | ~50 | 每日自动运行 |

**CLI 命令**:
```bash
python3 main.py brief --verbose    # 生成每日简报
python3 main.py predict --verbose  # 生成预测
python3 main.py data --type gold   # 获取数据
```

---

### 第 2 层：业务编排层

| 模块 | 文件 | 功能 |
|------|------|------|
| **InvestmentSystem** | `main.py` | 协调完整流程 |
| **DataAPI** | `api/data_api.py` | 统一数据接口 |

**核心流程**:
```python
# 1. 获取数据
data = api.get_all_data()

# 2. 生成预测
prediction = predictor.predict(data)

# 3. 生成简报
brief = generator.generate(data, prediction)

# 4. 发送通知
notifier.send(brief)
```

---

### 第 3 层：核心功能层

#### 3.1 数据源层 (12 个模块)

| 模块 | 文件 | 数据源 | 缓存 |
|------|------|--------|------|
| **基础类** | `data_sources/base.py` | - | 通用缓存 |
| **金价** | `data_sources/gold_source.py` | AKShare | 60 秒 |
| **金价 (浏览器)** | `data_sources/gold_browser_source.py` | 金投网 | 60 秒 |
| **基金** | `data_sources/fund_source.py` | AKShare | 300 秒 |
| **股票** | `data_sources/stock_source.py` | AKShare | 60 秒 |
| **新闻** | `data_sources/news_source.py` | 百度 + 东财 | 600 秒 |
| **宏观** | `data_sources/macro_source.py` | AKShare | 300 秒 |
| **宏观 (API)** | `data_sources/macro_api_source.py` | Yahoo | 300 秒 |
| **宏观 (Web)** | `data_sources/macro_web_source.py` | Investing | 300 秒 |
| **Web 搜索** | `data_sources/web_source.py` | 百度搜索 | 600 秒 |
| **浏览器** | `data_sources/browser_source.py` | Playwright | 600 秒 |
| **降级数据** | `data_sources/fallback.py` | 内置默认值 | - |

**数据流向**:
```
AKShare (主) → Yahoo Finance (备) → Investing.com (补) 
    → Web Search (搜) → Browser (爬) → Fallback (兜底)
```

---

#### 3.2 分析层 (6 个模块)

| 模块 | 文件 | 权重 | 功能 |
|------|------|------|------|
| **基础类** | `analyzers/base.py` | - | 分析器基类 |
| **技术分析** | `analyzers/technical.py` | 25.5% | RSI、MACD、均线 |
| **情绪分析** | `analyzers/sentiment.py` | 21.25% | 新闻情感打分 |
| **宏观分析** | `analyzers/macro.py` | 21.25% | DXY、VIX、油价 |
| **动量分析** | `analyzers/momentum.py` | 17% | 价格动量、趋势 |

**分析结果**:
```python
{
    'score': 0.65,           # 综合得分 (0-1)
    'signal': '买入',         # 交易信号
    'indicators': {...},     # 详细指标
    'reasoning': '...'       # 分析逻辑
}
```

---

#### 3.3 预测层 (5 个模块)

| 模块 | 文件 | 权重 | 功能 |
|------|------|------|------|
| **基础类** | `predictors/base.py` | - | 预测器基类 |
| **多因子** | `predictors/multi_factor.py` | 85% | 四因子加权 |
| **时序预测** | `predictors/simple_ts_predictor.py` | 15% | 移动平均 |
| **验证器** | `predictors/validator.py` | - | 准确率追踪 |
| **集成** | `predictors/composite.py` | - | 组合预测 |

**预测权重**:
```
技术因子：25.5%
情绪因子：21.25%
宏观因子：21.25%
动量因子：17.0%
时序模型：15.0%
─────────────
总计：100%
```

**预测结果**:
```python
{
    'current_price': 486.2,
    'predicted_price': 492.5,
    'direction': 'up',
    'confidence': '中',
    'signal': '买入',
    'scores': {
        'technical': 0.65,
        'sentiment': 0.55,
        'macro': 0.70,
        'momentum': 0.60
    }
}
```

---

#### 3.4 数据管道层 (3 个模块)

| 模块 | 文件 | 功能 |
|------|------|------|
| **清洗** | `data_pipeline/cleaner.py` | 数据清洗、格式化 |
| **验证** | `data_pipeline/validator.py` | 阈值验证、质量评分 |
| **存储** | `data_pipeline/storage.py` | SQLite 存储、缓存 |

**数据质量评分**:
```
A 级 (优秀): 时效性 90% + 准确性 95% + 完整性 100%
B 级 (良好): 时效性 70% + 准确性 85% + 完整性 90%
C 级 (可用): 时效性 50% + 准确性 70% + 完整性 80%
D 级 (降级): 低于 C 级标准
```

---

#### 3.5 输出层 (3 个模块)

| 模块 | 文件 | 功能 |
|------|------|------|
| **简报生成** | `presenters/brief_generator.py` | Markdown 简报 |
| **图表生成** | `presenters/chart_generator.py` | 3 种图表 |
| **初始化** | `presenters/__init__.py` | 模块导出 |

**图表类型**:
1. **价格走势图** - 历史价格 + 预测区间
2. **预测对比图** - 预测 vs 实际
3. **因子热力图** - 各因子得分

---

#### 3.6 通知层 (3 个模块)

| 模块 | 文件 | 功能 |
|------|------|------|
| **基础类** | `notifiers/base.py` | 通知器基类 |
| **告警通知** | `notifiers/alert_notifier.py` | 价格突破、低置信度 |
| **初始化** | `notifiers/__init__.py` | 模块导出 |

**告警类型**:
- 🚨 价格突破告警 (>3%)
- ⚠️ 低置信度告警 (<40%)
- ❌ 系统错误告警

---

### 第 4 层：基础设施层

#### 4.1 数据存储

| 类型 | 路径 | 用途 |
|------|------|------|
| **SQLite** | `data/db/*.db` | 结构化数据存储 |
| **JSON 缓存** | `data/cache/*.json` | 临时数据缓存 |
| **日志** | `logs/*.log` | 系统日志 |

**数据库文件**:
```
data/db/
├── gold_prices.db      # 金价数据
├── fund_data.db        # 基金数据
├── stock_data.db       # 股票数据
├── macro_data.db       # 宏观数据
├── news_sentiment.db   # 新闻情绪
└── predictions.db      # 预测验证
```

---

#### 4.2 配置系统

| 文件 | 功能 |
|------|------|
| `config.yaml` | 集中配置管理 |
| `utils/config_loader.py` | 配置加载器 |
| `requirements.txt` | 依赖管理 |

**配置加载**:
```python
from utils.config_loader import get_config

# 获取配置
gold_ttl = get_config('data_sources.cache_ttl.gold', 60)
tech_weight = get_config('prediction.weights.technical', 0.255)
```

---

## 🔄 数据流

### 完整流程

```
用户请求
    ↓
┌─────────────────┐
│  1. main.py     │ CLI / API 接收请求
└─────────────────┘
    ↓
┌─────────────────┐
│  2. DataAPI     │ 协调数据获取
└─────────────────┘
    ↓
┌─────────────────┐
│  3. 数据源层    │ 12 个数据源模块
│     - gold      │ 多源 + 降级
│     - macro     │
│     - news      │
└─────────────────┘
    ↓
┌─────────────────┐
│  4. 数据管道    │ 清洗 → 验证 → 存储
└─────────────────┘
    ↓
┌─────────────────┐
│  5. 分析层      │ 4 个分析器并行
│     - technical │
│     - sentiment │
│     - macro     │
│     - momentum  │
└─────────────────┘
    ↓
┌─────────────────┐
│  6. 预测层      │ 多因子 (85%) + 时序 (15%)
└─────────────────┘
    ↓
┌─────────────────┐
│  7. 输出层      │ 简报 + 图表
└─────────────────┘
    ↓
┌─────────────────┐
│  8. 通知层      │ 告警推送 (可选)
└─────────────────┘
    ↓
用户接收结果
```

---

## 📊 系统统计

### 代码规模

| 模块 | 文件数 | 代码行数 |
|------|--------|----------|
| **数据源层** | 12 | ~1,800 |
| **分析层** | 6 | ~900 |
| **预测层** | 5 | ~750 |
| **数据管道** | 3 | ~450 |
| **输出层** | 3 | ~600 |
| **通知层** | 3 | ~300 |
| **API 层** | 1 | ~200 |
| **工具层** | 2 | ~150 |
| **主入口** | 1 | ~200 |
| **类型定义** | 1 | ~450 |
| **总计** | **37** | **~5,800** |

### 系统指标

| 指标 | 数值 |
|------|------|
| **Python 文件总数** | 102 个 |
| **核心模块数** | 37 个 |
| **数据源数量** | 11 个 |
| **预测模型数** | 2 个 |
| **数据库文件** | 6 个 |
| **系统健康度** | 99% |
| **成熟度等级** | Level 4 |

---

## 🎯 核心特性

### 1. 多源降级

```
AKShare (主) 
    ↓ ❌
Yahoo Finance (备) 
    ↓ ❌
Investing.com (补) 
    ↓ ❌
Web Search (搜) 
    ↓ ❌
Browser (爬) 
    ↓ ❌
Fallback (兜底) ✅
```

### 2. 多因子预测

```
技术因子 (25.5%) + 情绪因子 (21.25%) + 宏观因子 (21.25%) 
    + 动量因子 (17%) + 时序模型 (15%)
    = 综合预测 (100%)
```

### 3. 预测验证

```
今日预测 → 次日验证 → 准确率统计 → 权重优化
```

### 4. 配置驱动

```
config.yaml (配置) 
    ↓
utils/config_loader.py (加载)
    ↓
全系统使用 (动态调整)
```

---

## 📁 完整目录结构

```
Macro-Investment-Assistant/
├── 📄 main.py                          # 主入口
├── 📄 model_types.py                   # 类型定义
├── 📄 config.yaml                      # 配置文件
├── 📄 requirements.txt                 # 依赖管理
│
├── 📁 api/
│   └── data_api.py                     # 数据 API
│
├── 📁 data_sources/                    # 数据源层 (12 模块)
│   ├── base.py
│   ├── gold_source.py
│   ├── gold_browser_source.py
│   ├── fund_source.py
│   ├── stock_source.py
│   ├── news_source.py
│   ├── macro_source.py
│   ├── macro_api_source.py
│   ├── macro_web_source.py
│   ├── web_source.py
│   ├── browser_source.py
│   └── fallback.py
│
├── 📁 data_pipeline/                   # 数据管道 (3 模块)
│   ├── cleaner.py
│   ├── validator.py
│   └── storage.py
│
├── 📁 analyzers/                       # 分析层 (6 模块)
│   ├── base.py
│   ├── technical.py
│   ├── sentiment.py
│   ├── macro.py
│   └── momentum.py
│
├── 📁 predictors/                      # 预测层 (5 模块)
│   ├── base.py
│   ├── multi_factor.py
│   ├── simple_ts_predictor.py
│   ├── validator.py
│   └── composite.py
│
├── 📁 presenters/                      # 输出层 (3 模块)
│   ├── brief_generator.py
│   ├── chart_generator.py
│   └── __init__.py
│
├── 📁 notifiers/                       # 通知层 (3 模块)
│   ├── base.py
│   ├── alert_notifier.py
│   └── __init__.py
│
├── 📁 utils/                           # 工具层 (2 模块)
│   ├── config_loader.py
│   └── __init__.py
│
├── 📁 data/                            # 数据目录
│   ├── db/                             # SQLite 数据库
│   └── cache/                          # JSON 缓存
│
├── 📁 logs/                            # 日志目录
├── 📁 daily_brief/                     # 简报输出
├── 📁 charts/                          # 图表输出
│
├── 📁 docs/                            # 文档目录
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   ├── AI_MODEL_GUIDE.md
│   ├── ALERT_SYSTEM_GUIDE.md
│   └── INTRADAY_ANALYSIS.md
│
├── 📁 examples/                        # 示例代码
│   ├── 01_basic_usage.py
│   ├── 02_data_fetching.py
│   ├── 03_prediction.py
│   ├── 04_brief_generation.py
│   ├── 05_custom_analysis.py
│   └── README.md
│
└── 📁 archive/                         # 归档目录
    └── phase_docs/                     # 历史文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 运行系统

```bash
# 生成每日简报
python3 main.py brief --verbose

# 生成预测
python3 main.py predict --verbose

# 获取数据
python3 main.py data --type gold
```

### 3. 使用 Python API

```python
from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor
from presenters.brief_generator import BriefGenerator

api = DataAPI()
predictor = MultiFactorPredictor()
gen = BriefGenerator()

data = api.get_all_data()
prediction = predictor.predict(data)
brief = gen.generate(data, prediction)
print(brief)
```

---

## 📞 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **架构详解** | `docs/ARCHITECTURE.md` | 完整架构说明 |
| **用户指南** | `docs/USER_GUIDE.md` | 使用手册 |
| **快速参考** | `docs/QUICK_REFERENCE.md` | 速查卡 |
| **AI 集成** | `docs/AI_MODEL_GUIDE.md` | AI 模型指南 |
| **执行报告** | `WEEK1_EXECUTION_REPORT.md` | 本周进展 |

---

**架构版本**: V8.1.0  
**最后更新**: 2026-03-31  
**维护者**: Investment Analyst
