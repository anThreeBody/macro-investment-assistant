# 分析模块文档

本文档介绍 Macro Investment Assistant 系统的分析模块（analyzers）。

---

## 模块总览

| 模块 | 功能 | 状态 |
|------|------|------|
| `fear_greed_index.py` | 恐慌贪婪综合指数 | ✅ V8.4.0 |
| `sentiment.py` | 新闻情绪分析 | ✅ V8.2.0 |
| `accuracy_tracker.py` | 预测准确率追踪 | ✅ V8.1.0 |
| `stock_reason_detailer.py` | 股票估值分析 | ✅ V8.3.0 |

---

## fear_greed_index.py - 恐慌贪婪指数 ⭐

**版本**: V8.4.0  
**作者**: Investment Steward  
**状态**: ✅ 生产就绪

### 功能描述

综合多个市场指标生成 0-100 的情绪指数：
- **0** = 极度恐慌（可能是买入机会）
- **100** = 极度贪婪（警惕回调风险）

### 指标组成

| 指标 | 权重 | 说明 |
|------|------|------|
| VIX 恐慌指数 | 25% | 市场波动率预期 |
| 股债性价比 | 25% | 沪深 300 股息率 - 10 年国债收益率 |
| 北向资金 | 20% | 外资流向（亿元） |
| 市场成交量 | 15% | 沪深两市总成交（亿元） |
| 新闻情绪 | 15% | 财经新闻情绪得分（-1 到 1） |

### 使用方法

#### 独立使用

```python
from analyzers.fear_greed_index import FearGreedIndex

# 初始化计算器
calculator = FearGreedIndex()

# 计算指数
result = calculator.calculate_index(
    vix=15.2,                    # VIX 值
    equity_bond_spread=0.2,      # 股债性价比（%）
    northbound_flow=35.8,        # 北向资金（亿元）
    volume=8500,                 # 成交量（亿元）
    sentiment=0.35               # 新闻情绪（-1 到 1）
)

# 查看结果
print(f"指数：{result['index_value']}")
print(f"信号：{result['signal']}")
print(f"解读：{result['description']}")

# 查看分项指标
for ind in result['indicators']:
    print(f"{ind.name}: {ind.value} ({ind.signal})")
```

#### 在简报中使用

```python
from presenters.brief_generator_enhanced import BriefGeneratorEnhanced

generator = BriefGeneratorEnhanced()
content = generator.generate(data, prediction)
# 恐慌贪婪指数会自动包含在简报中
```

### 输出示例

```markdown
### 📊 市场情绪指数

**恐慌贪婪指数**: 53（⚪ 中性）

**解读**: 市场情绪中性，观望为主

**分项指标**:

| 指标 | 数值 | 信号 |
|------|------|------|
| VIX 恐慌指数 | 15.2 | 🟡 中性偏低 |
| 股债性价比 | 0.2% | 🟡 中性偏空 |
| 北向资金 | +35.8 亿 | 🟡 小幅流入 |
| 市场成交量 | 8500 亿 | 🟡 正常偏多 |
| 新闻情绪 | +0.10 | 🟡 中性偏多 |
```

### 信号判断逻辑

| 综合得分 | 信号 | 解读 |
|----------|------|------|
| ≥ 80 | 极度贪婪 | 市场情绪极度乐观，警惕回调风险 |
| ≥ 65 | 贪婪 | 市场情绪乐观，保持谨慎 |
| ≥ 55 | 中性偏贪婪 | 市场情绪略偏乐观 |
| ≥ 45 | 中性 | 市场情绪中性，观望为主 |
| ≥ 35 | 中性偏恐慌 | 市场情绪略偏谨慎 |
| ≥ 20 | 恐慌 | 市场情绪悲观，关注机会 |
| < 20 | 极度恐慌 | 市场情绪极度悲观，可能是买入机会 |

### 阈值配置

可在 `FearGreedIndex` 类中调整各指标阈值：

```python
calculator = FearGreedIndex()

# 调整 VIX 阈值
calculator.vix_thresholds = {
    'extreme_fear': 30,
    'fear': 25,
    'neutral_high': 20,
    'neutral_low': 15,
    'greed': 12,
}

# 调整权重
calculator.weights = {
    'vix': 0.30,        # 提高 VIX 权重
    'equity_bond': 0.20,
    'northbound': 0.20,
    'volume': 0.15,
    'sentiment': 0.15,
}
```

### 测试命令

```bash
# 运行测试
python3 analyzers/fear_greed_index.py

# 预期输出
**恐慌贪婪指数**: 55（🟡 中性偏贪婪）
**解读**: 市场情绪略偏乐观
```

---

## sentiment.py - 新闻情绪分析

**版本**: V8.2.0  
**状态**: ✅ 生产就绪

### 功能描述

分析财经新闻的情绪倾向，生成 -1 到 1 的情绪得分。

### 使用方法

```python
from analyzers.sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
news_list = [...]  # 新闻列表

result = analyzer.analyze(news_list)
print(f"情绪得分：{result['score']}")
print(f"情绪标签：{result['label']}")
```

### 输出示例

```markdown
**情绪得分**: +0.35（偏正面）
（正面：3 条，负面：1 条，中性：1 条）

**情绪解读**: 市场情绪偏正面，主要受政策利好驱动
```

---

## accuracy_tracker.py - 预测准确率追踪

**版本**: V8.1.0  
**状态**: ✅ 生产就绪

### 功能描述

追踪预测准确率，统计 7 天/30 天/90 天的预测表现。

### 数据库

数据存储在 `data/predictions.db`：

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    prediction_date TEXT,
    predicted_price REAL,
    actual_price REAL,
    is_accurate INTEGER,
    ...
);
```

### 使用方法

```python
from analyzers.accuracy_tracker import AccuracyTracker

tracker = AccuracyTracker()
stats = tracker.get_stats()

print(f"7 天准确率：{stats['7 天']['准确率']}%")
print(f"30 天准确率：{stats['30 天']['准确率']}%")
print(f"90 天准确率：{stats['90 天']['准确率']}%")
```

---

## stock_reason_detailer.py - 股票估值分析

**版本**: V8.3.0  
**状态**: ✅ 生产就绪

### 功能描述

分析市场估值水平，包括 PE/PB、历史分位、资金流向等。

### 使用方法

```python
from analyzers.stock_reason_detailer import StockReasonDetailer

detailer = StockReasonDetailer()
result = detailer.analyze()

print(f"上证指数 PE: {result['valuation']['上证指数']['PE']}")
print(f"北向资金：{result['capital_flow']['northbound']}")
```

---

## 模块依赖关系

```
┌────────────────────────────────────────────────┐
│          brief_generator_enhanced.py           │
└────────────────────────────────────────────────┘
              ↓         ↓         ↓
    ┌─────────────┐ ┌──────────┐ ┌──────────────┐
    │ fear_greed  │ │sentiment │ │ stock_reason │
    │   _index    │ │          │ │  _detailer   │
    └─────────────┘ └──────────┘ └──────────────┘
                           ↓
                  ┌────────────────┐
                  │ accuracy_tracker│
                  └────────────────┘
```

---

## 性能指标

| 模块 | 平均执行时间 | 内存占用 |
|------|-------------|----------|
| fear_greed_index | < 10ms | < 5MB |
| sentiment | < 50ms | < 10MB |
| accuracy_tracker | < 20ms | < 5MB |
| stock_reason_detailer | < 100ms | < 20MB |

---

## 故障排查

### 问题 1: 恐慌贪婪指数显示异常

**症状**: 指数超出 0-100 范围

**解决**:
```python
# 检查输入数据是否在合理范围
assert 10 <= vix <= 50
assert -3 <= equity_bond_spread <= 5
assert -200 <= northbound_flow <= 200
assert 3000 <= volume <= 20000
assert -1 <= sentiment <= 1
```

### 问题 2: 情绪得分始终为 0

**症状**: 新闻情绪得分始终显示 0.0

**解决**:
1. 检查新闻数据源是否正常
2. 检查情绪分析器是否初始化
3. 查看日志：`tail -f logs/system.log`

---

## 扩展开发

### 添加新指标

1. 在 `FearGreedIndex.__init__` 中添加权重配置
2. 实现指标得分计算方法
3. 在 `calculate_index` 中调用新方法

```python
# 示例：添加 PUT/CALL 比率指标
self.weights['put_call'] = 0.10

def calculate_put_call_score(self, ratio: float) -> IndicatorSignal:
    # 实现逻辑
    pass

# 在 calculate_index 中调用
put_call_signal = self.calculate_put_call_score(put_call_ratio)
```

---

*文档位置：docs/ANALYZERS.md*  
*最后更新：2026-04-07*  
*版本：V8.4.0*
