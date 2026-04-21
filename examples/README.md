# 示例代码目录

本目录包含投资分析系统的使用示例，帮助 AI 模型和开发者快速理解如何集成和使用系统。

---

## 📚 示例列表

### 示例 1: 基础使用 - 生成每日简报

**文件**: `01_basic_usage.py`

**用途**: 展示如何使用系统生成完整的每日简报

**核心代码**:
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
```

**运行**:
```bash
python3 examples/01_basic_usage.py
```

---

### 示例 2: 数据获取

**文件**: `02_data_fetching.py`

**用途**: 展示如何获取金价、宏观、新闻等各类数据

**核心代码**:
```python
api = DataAPI()

# 获取金价
gold = api.get_gold_price()

# 获取宏观数据
macro = api.get_macro_data()

# 获取新闻
news = api.get_news(limit=10)

# 获取历史价格
history = api.get_gold_history(days=30)
```

**运行**:
```bash
python3 examples/02_data_fetching.py
```

---

### 示例 3: 预测生成

**文件**: `03_prediction.py`

**用途**: 展示如何使用多因子模型生成价格预测

**核心代码**:
```python
predictor = MultiFactorPredictor()
prediction = predictor.predict(data)

# 预测结果包含:
# - predicted_price: 预测价格
# - direction: 方向 (up/down/sideways)
# - confidence: 置信度 (高/中/低)
# - signal: 交易信号 (买入/卖出/持有)
# - scores: 各因子得分
```

**运行**:
```bash
python3 examples/03_prediction.py
```

---

### 示例 4: 简报生成

**文件**: `04_brief_generation.py`

**用途**: 展示如何生成 Markdown 简报和可视化图表

**核心代码**:
```python
gen = BriefGenerator()
brief = gen.generate(data, prediction)

chart_gen = ChartGenerator()
chart_gen.generate_price_chart(prices)
chart_gen.generate_prediction_chart(current_price, prediction)
chart_gen.generate_factor_heatmap(scores, weights)
```

**运行**:
```bash
python3 examples/04_brief_generation.py
```

---

### 示例 5: 自定义分析

**文件**: `05_custom_analysis.py`

**用途**: 展示如何单独使用各个分析器进行独立分析

**核心代码**:
```python
from analyzers.technical import TechnicalAnalyzer
from analyzers.sentiment import SentimentAnalyzer
from analyzers.macro import MacroAnalyzer
from analyzers.momentum import MomentumAnalyzer

tech = TechnicalAnalyzer().analyze(data)
sent = SentimentAnalyzer().analyze(data)
macro = MacroAnalyzer().analyze(data)
momentum = MomentumAnalyzer().analyze(data)
```

**运行**:
```bash
python3 examples/05_custom_analysis.py
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install pandas numpy matplotlib playwright
```

### 2. 运行示例

```bash
# 运行所有示例
for i in 01 02 03 04 05; do
    python3 examples/${i}_*.py
done
```

### 3. 查看输出

```bash
# 查看生成的简报
cat daily_brief/brief_example_*.md

# 查看生成的图表
ls -lh charts/
```

---

## 📊 输出示例

### 数据输出

```python
{
    'gold': {
        'international': {'price': 2034.5, 'change': 12.3},
        'domestic': {'price': 486.2, 'change': 2.1}
    },
    'macro': {
        'dxy': {'value': 103.5},
        'vix': {'value': 15.2},
        'oil': {'value': 82.3},
        'treasury': {'value': 4.2}
    }
}
```

### 预测输出

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

### 简报输出

```markdown
# 投资分析每日简报

## 市场概览
- 国际金价：$2034.5/盎司 (+0.61%)
- 国内金价：¥486.2/克 (+0.43%)

## 价格预测
- 预测价格：¥492.5
- 方向：上涨
- 置信度：中
- 信号：买入
```

---

## 🔧 自定义示例

### 修改预测权重

```python
from predictors.multi_factor import MultiFactorPredictor

predictor = MultiFactorPredictor()
predictor.weights = {
    'technical': 0.3,
    'sentiment': 0.2,
    'macro': 0.3,
    'momentum': 0.2
}
prediction = predictor.predict(data)
```

### 添加自定义分析器

```python
from analyzers.base import Analyzer

class MyCustomAnalyzer(Analyzer):
    def analyze(self, data):
        # 自定义分析逻辑
        return {'score': 0.5, 'signal': '持有'}

analyzer = MyCustomAnalyzer()
result = analyzer.analyze(data)
```

---

## 📚 更多资源

- [AI_MODEL_GUIDE.md](../docs/AI_MODEL_GUIDE.md) - AI 模型集成指南
- [USER_GUIDE.md](../docs/USER_GUIDE.md) - 完整使用指南
- [QUICK_REFERENCE.md](../docs/QUICK_REFERENCE.md) - 快速参考卡
- [types.py](../types.py) - 数据类型定义

---

**最后更新**: 2026-03-31  
**维护者**: Investment Analyst
