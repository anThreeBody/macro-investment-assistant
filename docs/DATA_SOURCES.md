# 数据源模块文档

本文档介绍 Macro Investment Assistant 系统的数据源模块（data_sources）。

---

## 模块总览

| 模块 | 功能 | 数据源 | 更新频率 |
|------|------|--------|----------|
| `gold_source.py` | 黄金价格 | 东方财富、CNGold、Sina | 实时 |
| `macro_source.py` | 宏观数据 | AKShare、Yahoo Finance | 每日 |
| `news_source.py` | 财经新闻 | 和讯财经、新浪财经 | 每小时 |
| `fund_source.py` | 基金数据 | AKShare | 每日 |
| `event_calendar.py` | 事件日历 | 手动配置 + 自动生成 | 每周 |

---

## event_calendar.py - 事件日历 ⭐

**版本**: V8.4.0  
**作者**: Investment Steward  
**状态**: ✅ 生产就绪

### 功能描述

收集和展示未来 7 天可能影响市场的重大事件。

### 事件类型

1. **经济数据**: CPI、GDP、PMI、就业数据等
2. **央行政策**: 议息会议、降准降息、LPR 报价等
3. **政治事件**: 选举、重要会议等
4. **公司财报**: 重要公司财报季
5. **其他**: 地缘政治、自然灾害等

### 数据结构

```json
{
  "events": [
    {
      "date": "2026-04-10",
      "time": "20:30",
      "title": "美国 CPI 数据",
      "country": "US",
      "impact": "高",
      "affected_assets": ["黄金", "美元", "美股"],
      "category": "经济数据",
      "forecast": "3.2%",
      "previous": "3.3%"
    }
  ]
}
```

### 使用方法

#### 独立使用

```python
from data_sources.event_calendar import EventCalendar

# 初始化日历
calendar = EventCalendar()

# 获取未来 7 天事件
events = calendar.get_upcoming_events(days=7)

# 按日期分组
by_date = calendar.get_events_by_date(events)

# 格式化日期
for date_str, date_events in sorted(by_date.items()):
    display_date = calendar.format_date(date_str)
    print(f"**{display_date}** ({date_str})")
    
    for event in date_events:
        print(f"  {event.time}: {event.title} ({event.impact})")
```

#### 在简报中使用

```python
from presenters.brief_generator_enhanced import BriefGeneratorEnhanced

generator = BriefGeneratorEnhanced()
content = generator.generate(data, prediction)
# 事件日历会自动包含在简报末尾
```

### 自动生成规则

系统会自动生成以下定期事件：

| 事件 | 时间规则 | 重要性 |
|------|----------|--------|
| 美国 CPI | 每月 10-15 日 | 🔴 高 |
| 中国 GDP | 季度首月 15-20 日 | 🔴 高 |
| 美联储议息会议 | 偶数月 15-20 日 | 🔴 高 |
| 中国 PMI | 每月 1-2 日 | 🟡 中 |
| 美国非农就业 | 每月第一个周五 | 🔴 高 |

### 手动配置事件

编辑 `data/event_calendar.json`：

```json
{
  "events": [
    {
      "date": "2026-04-15",
      "time": "10:00",
      "title": "中国一季度 GDP",
      "country": "CN",
      "impact": "高",
      "affected_assets": ["A 股", "人民币"],
      "category": "经济数据",
      "forecast": "5.0%",
      "previous": "5.2%"
    }
  ]
}
```

### 输出示例

```markdown
## 📅 未来 7 天重大事件

**4 月 10 日 (周五)** (2026-04-10)

| 时间 | 事件 | 影响资产 | 重要性 |
|------|------|----------|--------|
| 20:30 | 美国 CPI 数据 | 黄金, 美元, 美股 | 🔴 高 |
| 20:30 | 美国非农就业数据 | 美元, 黄金, 美股 | 🔴 高 |

**4 月 12 日 (周日)** (2026-04-12)

| 时间 | 事件 | 影响资产 | 重要性 |
|------|------|----------|--------|
| 10:00 | 中国一季度 GDP | A 股, 人民币 | 🔴 高 |
```

### 测试命令

```bash
# 运行测试
python3 data_sources/event_calendar.py

# 预期输出
未来 7 天共 7 个重大事件:

**4 月 10 日 (周五)** (2026-04-10)
| 时间 | 事件 | 影响资产 | 重要性 |
|------|------|----------|--------|
| 20:30 | 美国 CPI 数据 | 黄金, 美元, 美股 | 🔴 高 |
```

---

## gold_source.py - 黄金价格

**版本**: V8.3.0  
**状态**: ✅ 生产就绪

### 功能描述

从多个数据源获取黄金价格，进行对比验证。

### 数据源

1. **东方财富** - COMEX 黄金期货（主数据源）
2. **CNGold** - 中国黄金网（备用）
3. **Sina** - 新浪财经（备用）

### 使用方法

```python
from data_sources.gold_source import GoldSource

source = GoldSource()
data = source.get_gold_price()

print(f"国际金价：${data['international_usd_per_oz']}")
print(f"国内金价：¥{data['domestic_cny_per_gram']}/g")
print(f"数据源：{data['source']}")
print(f"置信度：{data['confidence']}")
```

---

## macro_source.py - 宏观数据

**版本**: V8.2.0  
**状态**: ✅ 生产就绪

### 功能描述

获取宏观经济数据，包括美元指数、VIX、原油等。

### 数据项

| 指标 | 说明 | 单位 |
|------|------|------|
| DXY | 美元指数 | - |
| VIX | 恐慌指数 | - |
| Oil | 原油价格 | USD/bbl |
| Market Sentiment | 市场情绪 | - |

### 使用方法

```python
from data_sources.macro_source import MacroSource

source = MacroSource()
data = source.get_macro_data()

print(f"DXY: {data['dxy']['value']}")
print(f"VIX: {data['vix']['value']}")
print(f"Oil: ${data['oil']['value']}")
```

---

## news_source.py - 财经新闻

**版本**: V8.2.0  
**状态**: ✅ 生产就绪

### 功能描述

聚合多源财经新闻，提供情绪分析基础数据。

### 数据源

- 和讯财经
- 新浪财经
- 东方财富

### 使用方法

```python
from data_sources.news_source import NewsSource

source = NewsSource()
news = source.get_news(limit=10)

for item in news:
    print(f"{item['title']} - {item['source']}")
```

---

## fund_source.py - 基金数据

**版本**: V8.3.0  
**状态**: ✅ 生产就绪

### 功能描述

获取基金数据，支持基金推荐。

### 数据源

- AKShare

### 使用方法

```python
from data_sources.fund_source import FundSource

source = FundSource()
funds = source.get_fund_recommendations(category='tech')

for fund in funds:
    print(f"{fund['code']}: {fund['name']} ({fund['change_pct']}%)")
```

---

## 数据源优先级

### 金价数据源

```
1. 东方财富 (主) - 实时期货数据
2. CNGold (备) - 现货价格
3. Sina (备) - 行情数据
```

### 基金数据源

```
1. AKShare (唯一) - 每日净值
```

### 宏观数据源

```
1. Yahoo Finance (主) - DXY, VIX
2. AKShare (备) - 原油
```

---

## 故障排查

### 问题 1: 事件日历为空

**症状**: 简报中不显示事件日历

**解决**:
1. 检查 `data/event_calendar.json` 是否存在
2. 运行 `calendar.save_sample_data()` 生成示例数据
3. 检查日期范围是否正确

### 问题 2: 金价获取失败

**症状**: 金价显示"暂缺"

**解决**:
1. 检查网络连接
2. 查看日志：`tail -f logs/gold.log`
3. 尝试切换到备用数据源

---

## 性能指标

| 数据源 | 平均响应时间 | 成功率 |
|--------|-------------|--------|
| 金价（东方财富） | < 2s | > 99% |
| 金价（CNGold） | < 3s | > 95% |
| 宏观数据 | < 5s | > 98% |
| 基金数据 | < 10s | > 95% |
| 事件日历 | < 10ms | 100% |

---

*文档位置：docs/DATA_SOURCES.md*  
*最后更新：2026-04-07*  
*版本：V8.4.0*
