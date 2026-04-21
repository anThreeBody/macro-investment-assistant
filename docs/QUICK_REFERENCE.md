# 快速参考指南

**版本**: V8.4.0  
**最后更新**: 2026-04-07

---

## 🚀 常用命令

### 生成简报

```bash
# 一键生成（推荐）
./run_daily.sh

# 查看最新简报
cat daily_brief/brief_v8_$(date +%Y%m%d).md

# 使用 Python 生成
python3 main.py brief
```

---

### 测试模块

```bash
# 恐慌贪婪指数
python3 analyzers/fear_greed_index.py

# 事件日历
python3 data_sources/event_calendar.py

# 金价获取
python3 scripts/gold_price_auto_v83.py

# 完整测试
python3 main.py brief
```

---

### 查看文档

```bash
# 系统总览
cat README.md

# 版本历史
cat docs/VERSION_HISTORY.md

# P0 需求报告
cat docs/P0_REQUIREMENTS_COMPLETE.md

# P1 需求报告
cat docs/P1_REQUIREMENTS_COMPLETE.md

# 分析模块文档
cat docs/ANALYZERS.md

# 数据源文档
cat docs/DATA_SOURCES.md
```

---

## 📊 简报章节

V8.4.0 简报包含以下章节：

1. **市场概览** - 主要指数行情
2. **黄金价格** - 国际/国内金价 + 多源验证
3. **宏观数据** - DXY、VIX、原油 + **恐慌贪婪指数** ⭐
4. **财经新闻** - 新闻情绪分析
5. **明日预测** - 预测结果 + **准确率历史** ⭐
6. **基金推荐** - 4 类基金 × 3 只
7. **股票分析** - 估值 + 资金流向 + 个股推荐
8. **未来 7 天重大事件** ⭐ - 事件日历

---

## 📁 关键文件

### 配置文件

| 文件 | 用途 |
|------|------|
| `data/event_calendar.json` | 事件日历数据 |
| `data/predictions.db` | 预测数据库 |

### 核心模块

| 文件 | 功能 |
|------|------|
| `analyzers/fear_greed_index.py` | 恐慌贪婪指数 |
| `data_sources/event_calendar.py` | 事件日历 |
| `presenters/brief_generator_enhanced.py` | 简报生成器 |
| `main.py` | 主入口 |

### 文档

| 文件 | 内容 |
|------|------|
| `README.md` | 系统总览 |
| `docs/VERSION_HISTORY.md` | 版本历史 |
| `docs/ANALYZERS.md` | 分析模块文档 |
| `docs/DATA_SOURCES.md` | 数据源文档 |
| `docs/P0_REQUIREMENTS_COMPLETE.md` | P0 验收报告 |
| `docs/P1_REQUIREMENTS_COMPLETE.md` | P1 验收报告 |

---

## 🔧 故障排查

### 查看日志

```bash
# 系统日志
tail -f logs/system.log

# API 日志
tail -f logs/api.log

# 金价日志
tail -f logs/gold.log
```

### 常见问题

**Q1: 恐慌贪婪指数显示异常？**
```bash
# 检查输入数据
python3 -c "
from analyzers.fear_greed_index import FearGreedIndex
c = FearGreedIndex()
print(c.get_default_data())
"
```

**Q2: 事件日历为空？**
```bash
# 重新生成示例数据
python3 -c "
from data_sources.event_calendar import EventCalendar
c = EventCalendar()
c.save_sample_data()
"
```

**Q3: 简报生成失败？**
```bash
# 查看错误信息
python3 main.py brief 2>&1 | tail -50
```

---

## 📈 系统指标

### 性能目标

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| API 服务可用性 | > 99.5% | - |
| 数据源可用性 | > 99% | - |
| 简报生成时间 | < 30s | ~20s |
| 预测准确率 | > 60% | 积累中 |

### 资源占用

| 组件 | 内存 | CPU |
|------|------|-----|
| 简报生成 | < 50MB | < 10% |
| 恐慌贪婪指数 | < 5MB | < 1% |
| 事件日历 | < 5MB | < 1% |

---

## 🎯 最佳实践

### 日常使用

```bash
# 早上 8 点：生成简报
./run_daily.sh

# 查看简报
cat daily_brief/brief_v8_*.md | head -100

# 重点关注
# 1. 恐慌贪婪指数（市场情绪）
# 2. 未来 7 天事件（重大事件提醒）
# 3. 预测准确率（模型表现）
```

### 数据分析

```python
# Python 脚本示例
from analyzers.fear_greed_index import FearGreedIndex
from data_sources.event_calendar import EventCalendar

# 获取恐慌贪婪指数
fg = FearGreedIndex()
result = fg.calculate_index(
    vix=15.2,
    equity_bond_spread=0.2,
    northbound_flow=35.8,
    volume=8500,
    sentiment=0.35
)
print(f"情绪指数：{result['index_value']} - {result['signal']}")

# 获取事件日历
ec = EventCalendar()
events = ec.get_upcoming_events(days=7)
print(f"未来 7 天事件：{len(events)} 个")
```

### 自动化集成

```bash
# Crontab 配置
# 每天早上 8 点生成简报
0 8 * * * cd /path/to/Macro-Investment-Assistant && ./run_daily.sh

# 或保持 API 服务运行
@reboot cd /path/to/Macro-Investment-Assistant && nohup python3 api/main.py > logs/api.log 2>&1 &
```

---

## 📞 快速链接

### 文档

- [系统总览](../README.md)
- [版本历史](VERSION_HISTORY.md)
- [P0 需求报告](P0_REQUIREMENTS_COMPLETE.md)
- [P1 需求报告](P1_REQUIREMENTS_COMPLETE.md)
- [分析模块文档](ANALYZERS.md)
- [数据源文档](DATA_SOURCES.md)

### 代码

- [恐慌贪婪指数](../analyzers/fear_greed_index.py)
- [事件日历](../data_sources/event_calendar.py)
- [简报生成器](../presenters/brief_generator_enhanced.py)
- [主入口](../main.py)

### 数据

- [事件日历数据](../data/event_calendar.json)
- [预测数据库](../data/predictions.db)
- [简报输出](../daily_brief/)

---

## 🎓 学习路径

### 新手入门

1. 阅读 [README.md](../README.md)
2. 运行 `./run_daily.sh` 生成简报
3. 查看简报，了解各章节含义
4. 阅读 [P0 需求报告](P0_REQUIREMENTS_COMPLETE.md)
5. 阅读 [P1 需求报告](P1_REQUIREMENTS_COMPLETE.md)

### 进阶使用

1. 阅读 [分析模块文档](ANALYZERS.md)
2. 独立使用恐慌贪婪指数
3. 配置事件日历
4. 调整指数权重和阈值

### 开发扩展

1. 阅读 [数据源文档](DATA_SOURCES.md)
2. 添加新的分析指标
3. 接入真实数据源
4. 优化算法和权重

---

*文档位置：docs/QUICK_REFERENCE.md*  
*最后更新：2026-04-07*  
*版本：V8.4.0*
