# AI 模型集成指南

**版本**: V8.1  
**更新日期**: 2026-03-31  
**目标读者**: AI 模型/开发者

---

## 🚀 60 秒理解本系统

### 这是什么？

**宏观叙事驱动的投资分析系统**，用于：
- 获取金价、宏观数据、新闻
- 生成价格预测（多因子模型）
- 输出每日简报（Markdown）
- 追踪预测准确率

### 核心功能

```
数据获取 → 分析 → 预测 → 输出 → 验证
```

### 快速使用

```bash
# 生成每日简报
python3 main.py brief --verbose

# 查看结果
cat daily_brief/brief_v8_*.md
```

### 核心文件

| 文件 | 用途 |
|------|------|
| `main.py` | 主入口 |
| `api/data_api.py` | 数据 API |
| `predictors/multi_factor.py` | 预测引擎 |
| `model_types.py` | 数据类型定义 |

---

## 📦 模块 API

### 1. 数据获取 API

#### 获取所有数据

```python
from api.data_api import DataAPI

# 初始化
api = DataAPI()

# 获取所有数据
data = api.get_all_data()

# 返回结构
{
    'gold': {
        'international': {'price': 2034.5, 'change': 12.3, 'change_pct': 0.61},
        'domestic': {'price': 486.2, 'change': 2.1, 'change_pct': 0.43}
    },
    'macro': {
        'dxy': {'value': 103.5, 'change': 0.2},
        'vix': {'value': 15.2, 'change': -0.5},
        'oil': {'value': 82.3, 'change': 1.2},
        'treasury': {'value': 4.2, 'change': 0.05}
    },
    'news': [
        {'title': '...', 'summary': '...', 'sentiment': 0.6}
    ],
    'prices': [...]  # 历史价格
}
```

#### 获取金价

```python
gold = api.get_gold_price(use_cache=True)
# 返回：GoldPrice 对象（见 types.py）
```

#### 获取宏观数据

```python
macro = api.get_macro_data()
# 返回：MacroData 对象
```

#### 获取新闻

```python
news = api.get_news(limit=10)
# 返回：NewsData 对象
```

### 2. 预测 API

#### 生成预测

```python
from predictors.multi_factor import MultiFactorPredictor

# 初始化
predictor = MultiFactorPredictor()

# 生成预测
prediction = predictor.predict(data)

# 返回结构
{
    'current_price': 486.2,
    'predicted_price': 492.5,
    'price_lower': 487.0,
    'price_upper': 498.0,
    'direction': 'up',
    'confidence': '中',
    'signal': '买入',
    'analysis': {
        'technical': {'score': 0.65, 'signal': '买入'},
        'sentiment': {'score': 0.55, 'signal': '持有'},
        'macro': {'score': 0.70, 'signal': '买入'},
        'momentum': {'score': 0.60, 'signal': '持有'}
    },
    'time_series': {
        'predicted_price': 490.2,
        'trend': '上涨',
        'confidence': '中'
    }
}
```

#### 验证预测

```python
from predictors.validator import PredictionValidator

# 初始化
validator = PredictionValidator()

# 验证昨日预测
validator.verify(actual_price=492.3)

# 获取准确率统计
stats = validator.get_accuracy_stats(days=30)
# 返回：{'total': 25, 'correct': 16, 'accuracy': 0.64, 'success_rate': 0.68}
```

### 3. 输出生成 API

#### 生成简报

```python
from presenters.brief_generator import BriefGenerator

# 初始化
gen = BriefGenerator()

# 生成简报
brief_content = gen.generate(data, prediction)

# 保存
with open('daily_brief/brief_v8_20260331.md', 'w') as f:
    f.write(brief_content)
```

#### 生成图表

```python
from presenters.chart_generator import ChartGenerator

# 初始化
chart_gen = ChartGenerator()

# 生成价格趋势图
chart_gen.generate_price_chart(prices, title="金价走势")

# 生成预测对比图
chart_gen.generate_prediction_chart(current_price, prediction)

# 生成因子热力图
chart_gen.generate_factor_heatmap(scores, weights)
```

### 4. 告警 API

```python
from notifiers.alert_notifier import AlertNotifier

# 初始化
alert = AlertNotifier()

# 检查告警
alert.check_alerts(data, prediction)
# 自动检测：价格突破、低置信度、系统错误
```

---

## 🔄 完整调用示例

### 示例 1: 基础使用

```python
#!/usr/bin/env python3
"""基础使用示例 - 生成每日简报"""

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor
from presenters.brief_generator import BriefGenerator

def main():
    # 1. 初始化
    api = DataAPI()
    predictor = MultiFactorPredictor()
    gen = BriefGenerator()
    
    # 2. 获取数据
    data = api.get_all_data()
    
    # 3. 生成预测
    prediction = predictor.predict(data)
    
    # 4. 生成简报
    brief = gen.generate(data, prediction)
    
    # 5. 输出
    print(brief)

if __name__ == '__main__':
    main()
```

### 示例 2: 仅获取数据

```python
#!/usr/bin/env python3
"""数据获取示例"""

from api.data_api import DataAPI
import json

def main():
    api = DataAPI()
    
    # 获取金价
    gold = api.get_gold_price()
    print(f"国际金价：${gold['international']['price']}")
    print(f"国内金价：¥{gold['domestic']['price']}/克")
    
    # 获取宏观数据
    macro = api.get_macro_data()
    print(f"DXY: {macro['dxy']['value']}")
    print(f"VIX: {macro['vix']['value']}")
    
    # 获取新闻
    news = api.get_news(limit=5)
    print(f"新闻数量：{len(news['items'])}")

if __name__ == '__main__':
    main()
```

### 示例 3: 生成预测

```python
#!/usr/bin/env python3
"""预测生成示例"""

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor

def main():
    # 获取数据
    api = DataAPI()
    data = api.get_all_data()
    
    # 生成预测
    predictor = MultiFactorPredictor()
    prediction = predictor.predict(data)
    
    # 输出预测结果
    print("=" * 50)
    print("预测结果")
    print("=" * 50)
    print(f"当前价格：¥{prediction['current_price']}")
    print(f"预测价格：¥{prediction['predicted_price']}")
    print(f"置信区间：[{prediction['price_lower']}, {prediction['price_upper']}]")
    print(f"方向：{prediction['direction']}")
    print(f"置信度：{prediction['confidence']}")
    print(f"信号：{prediction['signal']}")
    
    # 输出各因子得分
    print("\n因子分析:")
    for factor, score in prediction['analysis']['scores'].items():
        print(f"  {factor}: {score:.2f}")

if __name__ == '__main__':
    main()
```

### 示例 4: 验证预测准确率

```python
#!/usr/bin/env python3
"""预测验证示例"""

from predictors.validator import PredictionValidator

def main():
    validator = PredictionValidator()
    
    # 验证昨日预测（需要提供实际价格）
    actual_price = 492.3
    validator.verify(actual_price=actual_price)
    
    # 获取统计
    stats = validator.get_accuracy_stats(days=30)
    
    print("=" * 50)
    print("预测准确率统计")
    print("=" * 50)
    print(f"总预测数：{stats['total']}")
    print(f"正确数：{stats['correct']}")
    print(f"准确率：{stats['accuracy']:.2%}")
    print(f"方向正确率：{stats['success_rate']:.2%}")
    print(f"平均误差：{stats['avg_error']:.2f}")

if __name__ == '__main__':
    main()
```

### 示例 5: 自定义分析

```python
#!/usr/bin/env python3
"""自定义分析示例"""

from api.data_api import DataAPI
from analyzers.technical import TechnicalAnalyzer
from analyzers.sentiment import SentimentAnalyzer

def main():
    # 获取数据
    api = DataAPI()
    data = api.get_all_data()
    
    # 技术分析
    tech_analyzer = TechnicalAnalyzer()
    tech_result = tech_analyzer.analyze(data)
    print(f"RSI: {tech_result['rsi']:.2f}")
    print(f"MACD: {tech_result['macd']:.2f}")
    print(f"技术信号：{tech_result['signal']}")
    
    # 情感分析
    sent_analyzer = SentimentAnalyzer()
    sent_result = sent_analyzer.analyze(data)
    print(f"平均情感：{sent_result['avg_sentiment']:.2f}")
    print(f"情感信号：{sent_result['signal']}")

if __name__ == '__main__':
    main()
```

---

## 📊 数据类型详解

### 金价数据 (GoldPrice)

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
        'update_time': str
    }
}
```

### 宏观数据 (MacroData)

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

### 预测结果 (Prediction)

```python
{
    'current_price': float,
    'predicted_price': float,
    'price_lower': float,    # 置信区间下界
    'price_upper': float,    # 置信区间上界
    'direction': str,        # 'up' | 'down' | 'sideways'
    'confidence': str,       # '高' | '中' | '低'
    'signal': str,           # '买入' | '卖出' | '持有'
    'scores': {
        'technical': float,  # 技术面得分
        'sentiment': float,  # 情绪面得分
        'macro': float,      # 宏观面得分
        'momentum': float    # 动量面得分
    },
    'weights': {
        'technical': 0.255,
        'sentiment': 0.2125,
        'macro': 0.2125,
        'momentum': 0.17,
        'time_series': 0.15
    }
}
```

---

## 🏗️ 系统架构

### 分层架构

```
用户接口层 (CLI/API)
    ↓
业务编排层 (InvestmentSystem)
    ↓
核心功能层 (数据源/分析器/预测器/输出)
    ↓
基础设施层 (数据库/缓存/日志)
```

### 模块依赖

```
main.py
├── api/data_api.py
│   ├── data_sources/gold_source.py
│   ├── data_sources/macro_source.py
│   └── data_pipeline/validator.py
├── predictors/multi_factor.py
│   ├── analyzers/technical.py
│   ├── analyzers/sentiment.py
│   ├── analyzers/macro.py
│   └── analyzers/momentum.py
├── presenters/brief_generator.py
└── notifiers/alert_notifier.py
```

---

## ⚙️ 配置说明

### 数据源配置

```python
# data_sources/base.py
CACHE_TTL = {
    'gold': 60,      # 金价缓存 60 秒
    'macro': 300,    # 宏观数据缓存 5 分钟
    'news': 600,     # 新闻缓存 10 分钟
}
```

### 预测权重配置

```python
# predictors/multi_factor.py
WEIGHTS = {
    'technical': 0.255,
    'sentiment': 0.2125,
    'macro': 0.2125,
    'momentum': 0.17,
    'time_series': 0.15
}
```

### 验证阈值配置

```python
# data_pipeline/validator.py
VALIDATION_RANGES = {
    'gold_price_domestic': (500, 1500),
    'gold_price_intl': (150, 350),
    'dxy': (50, 150),
    'vix': (10, 100),
    'oil': (50, 150),
    'treasury': (1, 10)
}
```

---

## 🔍 故障排查

### 问题 1: 数据为 0

```python
# 检查数据源
from data_sources.macro_source import MacroDataSource

ds = MacroDataSource()
data = ds.fetch()
print(data['dxy']['source'])  # 查看数据来源
```

### 问题 2: 预测置信度低

```python
# 检查各因子得分
prediction = predictor.predict(data)
print(prediction['scores'])  # 查看各因子得分
# 如果某个因子得分异常，检查对应分析器
```

### 问题 3: 模块导入失败

```bash
# 测试导入
python3 -c "from api.data_api import DataAPI; print('OK')"

# 安装依赖
pip3 install pandas numpy matplotlib playwright
```

---

## 📚 更多资源

| 文档 | 用途 |
|------|------|
| [USER_GUIDE.md](USER_GUIDE.md) | 完整使用指南 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构说明 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 快速参考卡 |
| [types.py](../types.py) | 数据类型定义 |

---

**最后更新**: 2026-03-31  
**维护者**: Investment Analyst
