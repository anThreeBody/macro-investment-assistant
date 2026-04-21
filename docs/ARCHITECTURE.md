# 投资分析系统 - 架构总览

**版本**: V8.1  
**日期**: 2026-03-26  
**健康度**: 97%

---

## 🏗️ 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        投资预测系统 V8.1                         │
│                   Macro-Investment-Assistant                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    用户接口层                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  main.py   │  │  CLI 命令   │  │  Python API │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    业务逻辑层                              │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              InvestmentSystem (main.py)            │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │  │
│  │  │  │ DataAPI  ││Predictor ││Presenter │          │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘          │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    核心功能层                              │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  数据源层    │  │  分析层      │  │  预测层      │  │  │
│  │  │              │  │              │  │              │  │  │
│  │  │ gold_source  │  │ technical    │  │ multi_factor │  │  │
│  │  │ fund_source  │  │ sentiment    │  │ simple_ts    │  │  │
│  │  │ stock_source │  │ macro        │  │ validator    │  │  │
│  │  │ news_source  │  │ momentum     │  │              │  │  │
│  │  │ macro_source │  │              │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐                     │  │
│  │  │  数据管道    │  │  输出层      │                     │  │
│  │  │              │  │              │                     │  │
│  │  │ cleaner      │  │ brief_gen    │                     │  │
│  │  │ validator    │  │ chart_gen    │                     │  │
│  │  │ storage      │  │              │                     │  │
│  │  └──────────────┘  └──────────────┘                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    基础设施层                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  SQLite    │  │ JSON 缓存   │  │  日志系统  │         │  │
│  │  │  (data/)   │  │  (data/)   │  │  (logs/)   │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 模块依赖关系

```
main.py
  ├─ api/data_api.py
  │   ├─ data_sources/gold_source.py
  │   │   └─ data_sources/gold_browser_source.py
  │   ├─ data_sources/fund_source.py
  │   ├─ data_sources/stock_source.py
  │   ├─ data_sources/news_source.py
  │   │   └─ data_sources/browser_source.py
  │   └─ data_sources/macro_source.py
  │       ├─ data_sources/macro_api_source.py
  │       └─ data_sources/macro_web_source.py
  │
  ├─ predictors/multi_factor.py
  │   ├─ analyzers/technical.py
  │   ├─ analyzers/sentiment.py
  │   ├─ analyzers/macro.py
  │   ├─ analyzers/momentum.py
  │   └─ predictors/simple_ts_predictor.py
  │
  ├─ predictors/validator.py
  │   └─ (SQLite: data/db/predictions.db)
  │
  ├─ presenters/brief_generator.py
  │   └─ templates/brief_template.md
  │
  └─ presenters/chart_generator.py
      └─ (matplotlib)
```

---

## 🔄 核心流程

### 1. 数据获取流程

```
用户请求
   ↓
DataAPI.get_all_data()
   ↓
┌─────────────────────────────────────┐
│ 并行获取 (部分)                      │
├─────────────────────────────────────┤
│ GoldDataSource.fetch()             │
│   ├─ 金投网 (主)                    │
│   ├─ 浏览器搜索 (备)                │
│   └─ 兜底数据                       │
├─────────────────────────────────────┤
│ MacroDataSource.fetch()            │
│   ├─ AKShare (主)                   │
│   ├─ Yahoo Finance (备)             │
│   ├─ Investing.com (补)             │
│   └─ 兜底数据                       │
├─────────────────────────────────────┤
│ NewsDataSource.fetch()             │
│   ├─ 百度搜索                       │
│   └─ 浏览器抓取                     │
└─────────────────────────────────────┘
   ↓
DataPipeline.clean()
   ↓
DataPipeline.validate()
   ├─ 范围验证
   ├─ 完整性检查
   └─ 质量评分
   ↓
DataPipeline.store()
   ├─ SQLite (历史数据)
   └─ JSON (缓存)
   ↓
返回数据
```

### 2. 预测生成流程

```
数据输入
   ↓
MultiFactorPredictor.predict()
   ↓
┌─────────────────────────────────────┐
│ 1. 时序预测 (15% 权重)              │
│    ├─ SimpleTimeSeriesPredictor   │
│    │   train(prices)               │
│    │   predict(days=1)             │
│    └─ 输出：预测价格 + 置信区间     │
├─────────────────────────────────────┤
│ 2. 多因子分析 (85% 权重)            │
│    ├─ TechnicalAnalyzer           │
│    │   └─ RSI, MACD, 均线          │
│    ├─ SentimentAnalyzer           │
│    │   └─ 新闻情感分析              │
│    ├─ MacroAnalyzer               │
│    │   └─ DXY, VIX, 原油，美债      │
│    └─ MomentumAnalyzer            │
│        └─ 趋势强度                 │
└─────────────────────────────────────┘
   ↓
综合得分计算
   ├─ 多因子得分 × 0.85
   └─ 时序得分 × 0.15
   ↓
生成预测
   ├─ 预测价格
   ├─ 置信区间
   ├─ 方向判断
   └─ 交易信号
   ↓
PredictionValidator.save()
   └─ SQLite 保存
```

### 3. 预测验证流程

```
次日实际价格
   ↓
PredictionValidator.verify()
   ├─ 查询昨日预测
   ├─ 计算误差
   │   error = |predicted - actual|
   │   error_pct = error / actual
   │   accuracy = 1 - error_pct
   ├─ 判断方向
   │   if predicted > actual * 1.005: 'up'
   │   elif predicted < actual * 0.995: 'down'
   │   else: 'sideways'
   └─ 更新数据库
      ↓
PredictionValidator.get_accuracy_stats()
   ├─ 总预测数
   ├─ 正确数
   ├─ 平均准确率
   └─ 成功率
```

### 4. 简报生成流程

```
数据 + 预测
   ↓
BriefGenerator.generate_brief()
   ├─ _market_overview()     # 市场概览
   ├─ _gold_section()        # 金价
   ├─ _macro_section()       # 宏观数据
   ├─ _news_section()        # 新闻
   ├─ _prediction_section()  # 预测
   └─ _risk_warning()        # 风险提示
   ↓
Markdown 格式化
   ↓
保存文件
   └─ daily_brief/brief_v8_YYYYMMDD.md
```

---

## 📊 数据模型

### 金价数据

```python
{
    'international': {
        'price': float,      # 美元/盎司
        'change': float,     # 涨跌额
        'change_pct': float, # 涨跌幅
        'currency': 'USD',
        'unit': 'oz'
    },
    'domestic': {
        'price': float,      # 元/克
        'change': float,
        'change_pct': float,
        'currency': 'CNY',
        'unit': 'g'
    },
    'metadata': {
        'source': str,
        'update_time': str,
        'version': str
    }
}
```

### 宏观数据

```python
{
    'dxy': {
        'name': '美元指数',
        'code': 'DXY',
        'value': float,
        'change': float,
        'change_pct': float,
        'source': str
    },
    'vix': {...},
    'oil': {...},
    'treasury': {...}
}
```

### 预测结果

```python
{
    'current_price': float,
    'predicted_price': float,
    'price_lower': float,    # 置信区间下界
    'price_upper': float,    # 置信区间上界
    'direction': str,        # 'up' | 'down' | 'sideways'
    'confidence': str,       # '高' | '中' | '低'
    'signal': str,           # '买入' | '卖出' | '持有'
    'analysis': {
        'technical': {...},
        'sentiment': {...},
        'macro': {...},
        'momentum': {...},
        'scores': {
            'technical': float,
            'sentiment': float,
            'macro': float,
            'momentum': float
        },
        'weights': {
            'technical': 0.255,
            'sentiment': 0.2125,
            'macro': 0.2125,
            'momentum': 0.17,
            'time_series': 0.15
        }
    },
    'time_series': {
        'predicted_price': float,
        'trend': str,
        'confidence': str
    }
}
```

---

## 🛠️ 关键设计模式

### 1. 策略模式 (Strategy Pattern)

**应用**: 数据源 fallback

```python
class DataSource:
    def fetch(self):
        # 主数据源
        try:
            return self._fetch_primary()
        except:
            pass
        
        # 备用数据源
        try:
            return self._fetch_backup()
        except:
            pass
        
        # 兜底数据
        return self._get_fallback()
```

### 2. 工厂模式 (Factory Pattern)

**应用**: 分析器创建

```python
class AnalyzerFactory:
    @staticmethod
    def create(type: str) -> Analyzer:
        if type == 'technical':
            return TechnicalAnalyzer()
        elif type == 'sentiment':
            return SentimentAnalyzer()
        # ...
```

### 3. 观察者模式 (Observer Pattern)

**应用**: 告警通知

```python
class AlertNotifier:
    def notify(self, event: str, data: Dict):
        # 通知所有订阅者
        for subscriber in self.subscribers:
            subscriber.update(event, data)
```

### 4. 模板方法模式 (Template Method)

**应用**: 简报生成

```python
class BriefGenerator:
    def generate_brief(self, data, prediction):
        sections = []
        sections.append(self._market_overview(data))
        sections.append(self._gold_section(data))
        sections.append(self._prediction_section(prediction))
        # ...
        return '\n'.join(sections)
```

---

## 📈 性能指标

### 数据获取

| 指标 | 目标 | 实际 |
|------|------|------|
| 金价获取时间 | < 5s | ~3s |
| 宏观数据获取 | < 10s | ~8s |
| 新闻获取 | < 15s | ~12s |
| 总体成功率 | > 90% | 95% |

### 预测性能

| 指标 | 目标 | 实际 |
|------|------|------|
| 预测生成时间 | < 2s | ~1s |
| 目标准确率 (1 天) | > 60% | 待积累 |
| 验证覆盖率 | 100% | 100% |

### 系统稳定性

| 指标 | 目标 | 实际 |
|------|------|------|
| 无故障运行 | > 7 天 | 持续中 |
| 错误恢复 | 自动 fallback | ✅ |
| 日志完整性 | 100% | ✅ |

---

## 🔐 安全考虑

### 1. 数据安全

- ✅ 本地存储 (SQLite/JSON)
- ✅ 无敏感信息上传
- ✅ API Key 配置文件隔离

### 2. 代码安全

- ✅ 输入验证
- ✅ 异常处理
- ✅ 超时控制

### 3. 隐私保护

- ✅ 无用户数据收集
- ✅ 本地化处理
- ✅ 日志脱敏

---

## 🚀 扩展指南

### 添加新数据源

1. 继承 `DataSource` 基类
2. 实现 `fetch()` 方法
3. 添加到 `DataAPI`

```python
from data_sources.base import DataSource

class NewDataSource(DataSource):
    def fetch(self):
        # 实现数据获取逻辑
        pass
```

### 添加新分析器

1. 继承 `Analyzer` 基类
2. 实现 `analyze()` 方法
3. 添加到 `MultiFactorPredictor`

```python
from analyzers.base import Analyzer

class NewAnalyzer(Analyzer):
    def analyze(self, data):
        # 实现分析逻辑
        return {'score': 0.5, ...}
```

### 添加新预测模型

1. 继承 `Predictor` 基类
2. 实现 `predict()` 方法
3. 集成到主流程

```python
from predictors.base import Predictor

class NewPredictor(Predictor):
    def predict(self, data):
        # 实现预测逻辑
        return {'predicted_price': ..., ...}
```

---

## 📝 维护清单

### 日常维护

- [ ] 检查日志错误
- [ ] 验证数据准确性
- [ ] 监控预测准确率
- [ ] 清理过期缓存

### 定期维护

- [ ] 更新依赖库
- [ ] 检查 API 变更
- [ ] 优化因子权重
- [ ] 归档旧数据

### 故障排查

```bash
# 1. 检查日志
tail -f logs/system.log

# 2. 测试数据获取
python3 main.py data --all --verbose

# 3. 验证模块导入
python3 -c "from api.data_api import DataAPI; print('OK')"

# 4. 检查数据库
sqlite3 data/db/predictions.db ".tables"
```

---

**架构文档版本**: 1.0  
**最后更新**: 2026-03-26  
**维护者**: Investment Analyst
