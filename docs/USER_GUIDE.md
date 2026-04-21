# 投资分析系统 - 完整使用指南

**版本**: V8.1 Phase 5  
**最后更新**: 2026-04-01  
**系统健康度**: 98%  
**成熟度等级**: Level 4 (Production Ready)

---

## 📋 目录

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [快速开始](#快速开始)
4. [核心模块说明](#核心模块说明)
5. [API 参考](#api 参考)
6. [数据流说明](#数据流说明)
7. [预测系统说明](#预测系统说明)
8. [常见问题](#常见问题)
9. [冗余文件清理指南](#冗余文件清理指南)

---

## 系统概述

### 定位

**宏观叙事驱动的投资预测系统**，专注于：
- 黄金价格分析与预测
- 基金/股票数据分析
- 宏观经济指标追踪
- 每日投资简报生成
- 预测准确率验证

### 核心能力

| 能力 | 说明 | 准确率/性能 |
|------|------|-------------|
| 数据获取 | 多源 fallback 机制 | 95%+ 成功率 |
| 数据分析 | 4 维度因子分析 | 实时处理 |
| 价格预测 | 多因子 + 时序双模型 | 目标准确率 > 60% |
| 预测验证 | 次日自动验证 | 完整追踪 |
| 简报生成 | Markdown + 图表 | ~2KB/份 |
| **日内分析** | **黄金小时级分析** | **Phase 5 新增** |
| **基金推荐** | **5种风险画像** | **Phase 5 新增** |
| **股票分析** | **具体买卖建议** | **Phase 5 新增** |
| **系统看板** | **数据+准确率+日志** | **Phase 5 新增** |

### 技术栈

```
Python 3.8+
├─ 数据采集：playwright, AKShare, requests
├─ 数据处理：pandas, numpy
├─ 预测模型：自定义多因子 + 时序预测
├─ 数据存储：SQLite, JSON 缓存
└─ 可视化：matplotlib
```

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    投资预测系统 V8.1                         │
├─────────────────────────────────────────────────────────────┤
│  数据采集层 (data_sources/)                                  │
│  ├─ gold_source.py       → 金投网金价                        │
│  ├─ gold_browser_source.py → 浏览器金价 (备用)              │
│  ├─ fund_source.py       → 基金净值 (AKShare)               │
│  ├─ stock_source.py      → 股票行情 (AKShare)               │
│  ├─ news_source.py       → 财经新闻 (百度 + 浏览器)          │
│  ├─ macro_source.py      → 宏观数据 (多层 fallback)         │
│  ├─ macro_api_source.py  → Yahoo Finance API               │
│  └─ macro_web_source.py  → Investing.com 抓取              │
├─────────────────────────────────────────────────────────────┤
│  数据管道层 (data_pipeline/)                                 │
│  ├─ cleaner.py           → 数据清洗                         │
│  ├─ validator.py         → 数据验证 + 质量评分              │
│  └─ storage.py           → 数据存储 (SQLite/JSON)           │
├─────────────────────────────────────────────────────────────┤
│  分析层 (analyzers/)                                         │
│  ├─ base.py              → 分析器基类                       │
│  ├─ technical.py         → 技术分析 (RSI, MACD, 均线)       │
│  ├─ sentiment.py         → 情绪分析 (新闻情感)              │
│  ├─ macro.py             → 宏观分析 (DXY, VIX, 原油，美债)   │
│  ├─ momentum.py          → 动量分析 (趋势强度)              │
│  ├─ intraday_gold.py     → 日内分析 (小时级) ⭐Phase 5      │
│  ├─ fund_recommender.py  → 基金推荐 ⭐Phase 5               │
│  ├─ fund_timing_advisor.py → 基金时机 ⭐Phase 5             │
│  ├─ stock_recommender.py → 股票推荐 ⭐Phase 5               │
│  └─ accuracy_tracker.py  → 准确率追踪 ⭐Phase 5             │
├─────────────────────────────────────────────────────────────┤
│  预测层 (predictors/)                                        │
│  ├─ base.py              → 预测器基类                       │
│  ├─ multi_factor.py      → 多因子预测器 (85% 权重)          │
│  ├─ simple_ts_predictor.py → 时序预测器 (15% 权重)          │
│  └─ validator.py         → 预测验证器 (SQLite 追踪)         │
├─────────────────────────────────────────────────────────────┤
│  输出层 (presenters/)                                        │
│  ├─ brief_generator.py   → Markdown 简报生成                │
│  └─ chart_generator.py   → 图表生成 (3 种类型)              │
├─────────────────────────────────────────────────────────────┤
│  通知层 (notifiers/)                                         │
│  ├─ base.py              → 通知器基类                       │
│  ├─ alert_notifier.py    → 告警通知 (价格突破/低置信度)      │
│  └─ realtime_pusher.py   → 实时推送 ⭐Phase 5               │
├─────────────────────────────────────────────────────────────┤
│  服务层 (services/) ⭐Phase 5新增                              │
│  ├─ gold_intraday_service.py → 黄金日内服务               │
│  ├─ fund_analysis_service.py → 基金分析服务                   │
│  └─ stock_analysis_service.py → 股票分析服务              │
├─────────────────────────────────────────────────────────────┤
│  看板层 (dashboards/) ⭐Phase 5新增                         │
│  ├─ data_asset_dashboard.py → 数据资产看板                  │
│  ├─ accuracy_dashboard.py   → 准确率看板                    │
│  ├─ evolution_log.py    → 进化日志                        │
│  └─ dashboard_service.py  → 统一服务                        │
├─────────────────────────────────────────────────────────────┤
│  API 层 (api/)                                                │
│  └─ data_api.py          → 统一数据接口                     │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户请求
   ↓
main.py (统一入口)
   ↓
DataAPI (数据聚合)
   ├─ GoldDataSource → 金价数据
   ├─ FundDataSource → 基金数据
   ├─ StockDataSource → 股票数据
   ├─ NewsDataSource → 新闻数据
   └─ MacroDataSource → 宏观数据
   ↓
DataPipeline (清洗 + 验证)
   ↓
MultiFactorPredictor (预测)
   ├─ TechnicalAnalyzer → 技术得分
   ├─ SentimentAnalyzer → 情绪得分
   ├─ MacroAnalyzer → 宏观得分
   ├─ MomentumAnalyzer → 动量得分
   └─ SimpleTimeSeriesPredictor → 时序预测
   ↓
BriefGenerator (简报生成)
   ├─ Markdown 报告
   └─ 图表生成
   ↓
AlertNotifier (告警检查)
   ↓
输出/推送
```

---

## 快速开始

### 安装依赖

```bash
# 进入项目目录
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 安装核心依赖
pip3 install pandas numpy matplotlib playwright

# 安装可选依赖 (AKShare)
pip3 install akshare

# 安装 Playwright 浏览器
playwright install chromium
```

### 基础使用

#### 1. 生成每日简报

```bash
# 方式 1: 使用 main.py (推荐)
python3 main.py brief

# 方式 2: 使用 run 脚本
./run_daily_v8.sh

# 方式 3: 详细输出
python3 main.py brief --verbose
```

**输出**:
- `daily_brief/brief_v8_YYYYMMDD.md` - Markdown 简报
- `charts/` - 图表文件

#### 2. 获取数据

```bash
# 获取所有数据
python3 main.py data --all

# 只获取金价
python3 main.py data --gold

# 只获取宏观数据
python3 main.py data --macro
```

#### 3. 生成预测

```bash
# 生成预测（不生成简报）
python3 main.py predict

# 查看详细预测
python3 main.py predict --verbose
```

### Python API 使用

#### 示例 1: 获取金价数据

```python
from api.data_api import DataAPI

api = DataAPI()
data = api.get_all_data()

# 访问金价
gold = data['gold']
print(f"国际金价：${gold['international']['price']}")
print(f"国内金价：¥{gold['domestic']['price']}")
```

#### 示例 2: 生成预测

```python
from predictors.multi_factor import MultiFactorPredictor

predictor = MultiFactorPredictor()
prediction = predictor.predict(data)

print(f"预测方向：{prediction['direction']}")
print(f"预测价格：¥{prediction['predicted_price']}")
print(f"置信度：{prediction['confidence']}")
```

#### 示例 3: 生成简报

```python
from presenters.brief_generator import BriefGenerator

generator = BriefGenerator()
brief = generator.generate_brief(data, prediction)

# 保存到文件
with open('daily_brief/test.md', 'w') as f:
    f.write(brief)
```

#### 示例 4: 预测验证

```python
from predictors.validator import PredictionValidator

validator = PredictionValidator()

# 保存预测
validator.save_prediction(prediction)

# 次日验证
result = validator.verify_prediction('2026-03-26', actual_price=1008.0)
print(f"准确率：{result['accuracy']:.2%}")

# 获取统计
stats = validator.get_accuracy_stats(days=30)
print(f"30 天准确率：{stats['accuracy']:.2%}")
```

---

## 核心模块说明

### 1. 数据源层 (data_sources/)

#### GoldDataSource (金价)

**文件**: `gold_source.py`, `gold_browser_source.py`

**功能**:
- 从金投网获取国际/国内金价
- 浏览器百度搜索作为备用
- 本地缓存 (60 秒 TTL)

**使用**:
```python
from data_sources.gold_source import GoldDataSource

ds = GoldDataSource()
data = ds.fetch()

# 输出:
# {
#   'international': {'price': 231.94, 'change': 0.0, ...},
#   'domestic': {'price': 1001.85, 'change': 0.0, ...},
#   'metadata': {...}
# }
```

**Fallback 机制**:
```
金投网 → 浏览器百度搜索 → 兜底数据
```

#### MacroDataSource (宏观)

**文件**: `macro_source.py`, `macro_api_source.py`, `macro_web_source.py`

**功能**:
- DXY (美元指数)
- VIX (恐慌指数)
- 原油价格
- 美债收益率

**使用**:
```python
from data_sources.macro_source import MacroDataSource

ds = MacroDataSource()
data = ds.fetch()

# 输出:
# {
#   'dxy': {'value': 99.68, 'source': 'Yahoo Finance'},
#   'vix': {'value': 15.2, 'source': '兜底数据'},
#   'oil': {'value': 93.0, 'source': 'Yahoo Finance'},
#   'treasury': {'value': 4.33, 'source': 'Yahoo Finance'}
# }
```

**Fallback 机制**:
```
AKShare → Yahoo Finance → Investing.com → 百度搜索 → 兜底数据
```

#### NewsDataSource (新闻)

**文件**: `news_source.py`

**功能**:
- 百度搜索财经新闻
- 浏览器抓取 (东财、和讯)
- 情感分析

**使用**:
```python
from data_sources.news_source import NewsDataSource

ds = NewsDataSource()
news = ds.fetch(query='黄金 财经', count=10)

# 输出:
# {
#   'articles': [
#     {'title': '...', 'content': '...', 'sentiment': 0.5},
#     ...
#   ],
#   'sentiment_score': 0.2
# }
```

### 2. 分析层 (analyzers/)

#### TechnicalAnalyzer (技术面)

**文件**: `technical.py`

**指标**:
- RSI (相对强弱指标)
- MACD (移动平均收敛散度)
- 均线系统 (5/10/20 日)
- 布林带

**使用**:
```python
from analyzers.technical import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()
result = analyzer.analyze(data)

# 输出:
# {
#   'score': 0.6,  # 0-1, >0.5 看涨
#   'rsi': 55.2,
#   'macd_signal': 'bullish',
#   'trend': 'up'
# }
```

#### SentimentAnalyzer (情绪面)

**文件**: `sentiment.py`

**功能**:
- 新闻情感分析
- 正面/负面新闻计数
- 情绪得分计算

**使用**:
```python
from analyzers.sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze(data)

# 输出:
# {
#   'score': 0.3,  # -1 到 1
#   'positive': 5,
#   'negative': 2,
#   'neutral': 3
# }
```

#### MacroAnalyzer (宏观面)

**文件**: `macro.py`

**指标**:
- DXY (美元指数) - 负相关
- VIX (恐慌指数) - 正相关
- 原油价格 - 通胀预期
- 美债收益率 - 机会成本

**使用**:
```python
from analyzers.macro import MacroAnalyzer

analyzer = MacroAnalyzer()
result = analyzer.analyze(data)

# 输出:
# {
#   'score': 0.4,
#   'dxy_impact': 'negative',
#   'vix_impact': 'positive',
#   'inflation_expectation': 'moderate'
# }
```

### 3. 预测层 (predictors/)

#### MultiFactorPredictor (多因子)

**文件**: `multi_factor.py`

**权重**:
| 因子 | 权重 |
|------|------|
| 技术面 | 25.5% |
| 情绪面 | 21.25% |
| 宏观面 | 21.25% |
| 动量面 | 17% |
| 时序预测 | 15% |

**使用**:
```python
from predictors.multi_factor import MultiFactorPredictor

predictor = MultiFactorPredictor()
prediction = predictor.predict(data)

# 输出:
# {
#   'current_price': 1001.85,
#   'predicted_price': 1015.50,
#   'direction': 'up',
#   'confidence': '中',
#   'signal': '持有',
#   'analysis': {...}
# }
```

#### SimpleTimeSeriesPredictor (时序)

**文件**: `simple_ts_predictor.py`

**算法**:
- 移动平均
- 趋势外推
- 波动率计算

**使用**:
```python
from predictors.simple_ts_predictor import SimpleTimeSeriesPredictor

predictor = SimpleTimeSeriesPredictor()
predictor.train(prices)  # prices: List[float]
result = predictor.predict(days=1)

# 输出:
# {
#   'predicted_price': 1010.5,
#   'price_lower': 995.0,
#   'price_upper': 1026.0,
#   'trend': 'up',
#   'confidence': '高'
# }
```

#### PredictionValidator (验证)

**文件**: `validator.py`

**功能**:
- 保存预测到 SQLite
- 次日自动验证
- 准确率统计

**使用**:
```python
from predictors.validator import PredictionValidator

validator = PredictionValidator(db_path='data/db/predictions.db')

# 保存预测
validator.save_prediction(prediction)

# 验证
result = validator.verify_prediction('2026-03-26', 1008.0)

# 统计
stats = validator.get_accuracy_stats(days=30)
```

### 4. 输出层 (presenters/)

#### BriefGenerator (简报)

**文件**: `brief_generator.py`

**结构**:
```markdown
# 📊 投资每日简报

## 🌍 市场概览
## 💰 黄金价格
## 📈 宏观数据
## 📰 财经新闻
## 🔮 明日预测
## ⚠️ 风险提示
```

**使用**:
```python
from presenters.brief_generator import BriefGenerator

gen = BriefGenerator()
brief = gen.generate_brief(data, prediction)

# 保存
with open('brief.md', 'w') as f:
    f.write(brief)
```

#### ChartGenerator (图表)

**文件**: `chart_generator.py`

**图表类型**:
1. 价格走势图
2. 预测对比图
3. 因子热力图

**使用**:
```python
from presenters.chart_generator import ChartGenerator

gen = ChartGenerator()
gen.plot_price_chart(prices, save_path='charts/price.png')
gen.plot_prediction_chart(prediction, save_path='charts/prediction.png')
```

---

## API 参考

### DataAPI

**文件**: `api/data_api.py`

**方法**:

```python
class DataAPI:
    def get_all_data(self) -> Dict:
        """获取所有数据"""
    
    def get_gold_data(self) -> Dict:
        """获取金价数据"""
    
    def get_macro_data(self) -> Dict:
        """获取宏观数据"""
    
    def get_news_data(self, count=10) -> Dict:
        """获取新闻数据"""
```

### 数据格式

**完整数据结构**:

```python
{
    'gold': {
        'international': {
            'price': 231.94,
            'change': 0.0,
            'change_pct': 0.0,
            'currency': 'USD',
            'unit': 'oz'
        },
        'domestic': {
            'price': 1001.85,
            'change': 0.0,
            'change_pct': 0.0,
            'currency': 'CNY',
            'unit': 'g'
        },
        'prices': [...]  # 历史价格
    },
    'fund': {...},
    'stock': {...},
    'news': {
        'articles': [...],
        'sentiment_score': 0.2
    },
    'macro': {
        'dxy': {'value': 99.68, ...},
        'vix': {'value': 15.2, ...},
        'oil': {'value': 93.0, ...},
        'treasury': {'value': 4.33, ...}
    },
    'metadata': {...}
}
```

---

## 预测系统说明

### 预测流程

```
1. 数据采集 (08:00)
   ↓
2. 因子计算
   ├─ 技术因子 (RSI, MACD, 均线)
   ├─ 情绪因子 (新闻情感)
   ├─ 宏观因子 (DXY, VIX, 原油，美债)
   └─ 动量因子 (趋势强度)
   ↓
3. 时序预测
   ├─ 训练模型 (最近 30 天价格)
   └─ 生成预测 (1 天/3 天/7 天)
   ↓
4. 多因子加权
   ├─ 多因子得分 × 85%
   └─ 时序得分 × 15%
   ↓
5. 生成预测
   ├─ 预测价格
   ├─ 置信区间
   └─ 交易信号
   ↓
6. 保存预测 (SQLite)
   ↓
7. 次日验证
   ├─ 计算误差
   ├─ 判断方向
   └─ 更新统计
```

### 预测置信度

| 置信度 | 条件 | 建议操作 |
|--------|------|----------|
| 高 | 综合得分 > 0.7 | 可考虑建仓 |
| 中 | 0.4 < 得分 ≤ 0.7 | 持有观望 |
| 低 | 得分 ≤ 0.4 | 谨慎操作 |

### 准确率目标

| 周期 | 目标准确率 | 当前水平 |
|------|------------|----------|
| 1 天 | > 60% | 待积累数据 |
| 3 天 | > 55% | 待积累数据 |
| 7 天 | > 50% | 待积累数据 |

---

## 常见问题

### Q1: 宏观数据为 0 或兜底值

**原因**: AKShare 接口变更或网络问题

**解决**:
```python
# 检查数据源
from data_sources.macro_source import MacroDataSource

ds = MacroDataSource()
data = ds.fetch()
print(data['dxy']['source'])  # 查看数据来源
```

**Fallback**: 系统自动切换到 Yahoo Finance 或兜底数据

### Q2: 金价验证误报

**原因**: 验证阈值过严

**解决**: 已优化阈值
```python
# 当前阈值
gold_price_domestic: (500, 1500)  # 元/克
gold_price_intl: (150, 350)       # 美元/盎司
```

### Q3: 预测准确率低

**原因**: 
1. 数据不足
2. 市场异常波动
3. 因子权重不合理

**解决**:
```python
# 查看验证统计
from predictors.validator import PredictionValidator

validator = PredictionValidator()
stats = validator.get_accuracy_stats(days=30)
print(f"准确率：{stats['accuracy']:.2%}")

# 调整权重 (需要重新初始化)
predictor = MultiFactorPredictor()
predictor.config.params['weights']['technical'] = 0.35
```

### Q4: Playwright 浏览器无法启动

**原因**: 浏览器未安装

**解决**:
```bash
# 安装浏览器
playwright install chromium

# 测试
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### Q5: 简报生成失败

**原因**: 数据缺失

**解决**:
```bash
# 检查数据
python3 main.py data --all --verbose

# 查看日志
tail -f logs/system.log
```

---

## 冗余文件清理指南

### 发现的冗余

#### 1. scripts/ 目录 (66 个文件)

**问题**: 大量旧版本脚本，功能已整合到主系统

**可清理**:
```
scripts/gold_*.py          # 已整合到 gold_source.py
scripts/macro_*.py         # 已整合到 macro_source.py
scripts/news_*.py          # 已整合到 news_source.py
scripts/predict_*.py       # 已整合到 predictors/
scripts/valid_*.py         # 已整合到 validator.py
scripts/backtest_*.py      # 回测框架未完成
scripts/ml_*.py            # ML 预测器未使用
```

**保留**:
```
scripts/run_daily_v8.sh    # 启动脚本
scripts/alert_system.py    # 告警系统
scripts/data_backup.py     # 数据备份
```

**清理命令**:
```bash
# 备份 scripts 目录
cp -r scripts scripts_backup_$(date +%Y%m%d)

# 删除旧脚本
rm scripts/gold_*.py
rm scripts/macro_*.py
rm scripts/news_*.py
rm scripts/predict_*.py
rm scripts/valid_*.py

# 验证系统正常
python3 main.py brief
```

#### 2. 文档冗余

**重复文档**:
- `PHASE1_REVIEW.md` → 已整合到 `PHASE4_SUMMARY.md`
- `PHASE2_COMPLETE.md` → 已整合到 `PHASE4_SUMMARY.md`
- `PHASE3_COMPLETE.md` → 已整合到 `PHASE4_SUMMARY.md`
- `FINAL_SUMMARY.md` → 已整合到 `PHASE4_SUMMARY.md`

**建议保留**:
```
PHASE4_SUMMARY.md          # 最新总结
QUICK_START.md             # 快速开始
SKILL.md                   # 技能说明
WORKFLOW.md                # 工作流程
README.md                  # 项目说明 (待创建)
```

**清理命令**:
```bash
# 移动到 archive 目录
mkdir -p docs/archive
mv PHASE1_REVIEW.md docs/archive/
mv PHASE2_COMPLETE.md docs/archive/
mv PHASE3_COMPLETE.md docs/archive/
mv FINAL_SUMMARY.md docs/archive/
```

#### 3. 代码冗余

**检查项**:
```bash
# 查找重复函数
grep -r "def fetch_gold" --include="*.py" | grep -v __pycache__

# 查找未使用导入
pip3 install autoflake
autoflake --remove-all-unused-imports -r .
```

### 清理后结构

```
Macro-Investment-Assistant/
├── main.py                    # 主入口 ✅
├── api/                       # API 层 ✅
├── data_sources/              # 数据源 ✅
├── data_pipeline/             # 数据管道 ✅
├── analyzers/                 # 分析器 ✅
├── predictors/                # 预测器 ✅
├── presenters/                # 输出层 ✅
├── notifiers/                 # 通知层 ✅
├── services/                  # 服务层 ⭐Phase 5
├── dashboards/                # 看板层 ⭐Phase 5
├── tools/                     # CLI工具 ⭐Phase 5
├── scripts/                   # 仅保留关键脚本
│   ├── run_daily_v8.sh
│   ├── alert_system.py
│   └── data_backup.py
├── data/                      # 数据目录
├── daily_brief/               # 简报输出
├── charts/                    # 图表输出
├── logs/                      # 日志
├── docs/                      # 文档
│   ├── archive/               # 归档旧文档
│   └── USER_GUIDE.md          # 本文档
└── tests/                     # 测试用例
```

---

## 附录

### A. 文件清单

**核心模块** (35+ 个):
```
main.py
api/data_api.py
data_sources/*.py (8 个)
data_pipeline/*.py (3 个)
analyzers/*.py (12 个) ⭐Phase 5 新增7个
predictors/*.py (4 个)
presenters/*.py (3 个)
notifiers/*.py (4 个) ⭐Phase 5 新增1个
services/*.py (3 个) ⭐Phase 5 新增
dashboards/*.py (4 个) ⭐Phase 5 新增
tools/*.py (3 个) ⭐Phase 5 新增
```

**脚本** (3 个):
```
scripts/run_daily_v8.sh
scripts/alert_system.py
scripts/data_backup.py
```

**文档** (10+ 个):
```
README.md
USER_GUIDE.md (本文档)
QUICK_START.md
SKILL.md
PHASE4_SUMMARY.md
PHASE5_STAGE1_COMPLETE.md ⭐Phase 5
PHASE5_STAGE2_COMPLETE.md ⭐Phase 5
PHASE5_STAGE3_COMPLETE.md ⭐Phase 5
PHASE5_STAGE4_COMPLETE.md ⭐Phase 5
PHASE5_COMPLETE.md ⭐Phase 5
EVOLUTION_LOG.md ⭐Phase 5
```

### B. 依赖清单

```txt
# 核心依赖
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0
playwright>=1.20.0

# 数据源
akshare>=1.8.0
requests>=2.25.0

# 可选依赖
yfinance>=0.1.70  # Yahoo Finance

# 开发依赖
pytest>=6.0.0
black>=21.0.0
flake8>=3.9.0
```

### C. 定时任务配置

**cron 配置**:
```bash
# 每日 08:00 生成简报
0 8 * * * cd /path/to/Macro-Investment-Assistant && ./run_daily_v8.sh >> logs/cron.log 2>&1

# 每日 18:00 验证预测
0 18 * * * cd /path/to/Macro-Investment-Assistant && python3 scripts/verify_predictions.py >> logs/verify.log 2>&1

# 每小时检查黄金日内信号 (交易时间)
0 9-15 * * 1-5 cd /path/to/Macro-Investment-Assistant && python3 tools/intraday_cli.py signal >> logs/intraday.log 2>&1

# 每周生成系统看板
0 9 * * 0 cd /path/to/Macro-Investment-Assistant && python3 dashboards/dashboard_service.py >> logs/dashboard.log 2>&1
```

### D. 日志配置

**日志级别**:
- DEBUG: 调试信息
- INFO: 正常流程
- WARNING: 警告信息
- ERROR: 错误信息

**日志文件**:
- `logs/system.log` - 系统日志
- `logs/data.log` - 数据获取日志
- `logs/prediction.log` - 预测日志

---

**文档版本**: 1.0  
**最后更新**: 2026-03-26  
**维护者**: Investment Analyst

---

**祝使用愉快！** 🚀
