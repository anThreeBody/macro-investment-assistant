---
name: macro-investment-assistant
description: 宏观叙事驱动的投资分析助手，基于国家政策、全球经济形势分析黄金、基金、股票的投资机会
version: 8.4.5
last_updated: 2026-04-15
---

# Macro Investment Assistant - 宏观投资助手

## 🚀 60 秒理解本技能

**这是什么**: 宏观叙事驱动的智能投资分析系统（**V8.4.5 取消震荡预测**）

**核心功能**:
- 📊 获取金价/宏观/新闻数据 (26 个数据源模块)
- 🔮 多因子预测 (技术 + 情绪 + 宏观 + 动量 + 时序)
- 📝 生成每日简报 (Markdown，自动保存预测，**新增宏观叙事分析**)
- ✅ 预测验证与准确率追踪 (每日自动验证)
- 🧠 **宏观叙事分析** - 政策→经济→资产→策略因果推理 ⭐V8.4.2 新增

**如何使用**:
```bash
# 每日简报（推荐）
./run_daily.sh                      # 一键运行，包含验证 + 生成

# 或使用主入口
python3 main.py brief               # 生成每日简报
python3 main.py predict             # 仅生成预测
python3 main.py data --type all     # 获取所有数据

# 黄金日内分析 ⭐Phase 5
python3 tools/intraday_cli.py analyze

# 基金推荐 ⭐Phase 5
python3 tools/fund_cli.py recommend --risk balanced

# 股票精选 ⭐Phase 5
python3 tools/stock_cli.py picks --top-n 5

# 系统看板 ⭐Phase 5
python3 dashboards/dashboard_service.py
```

**核心文件**:
- `main.py` - 主入口 ⭐
- `run_daily.sh` - 每日简报脚本 ⭐
- `api/data_api.py` - 数据 API
- `predictors/multi_factor.py` - 预测引擎
- `predictors/validator.py` - 预测验证器 ⭐新增
- `analyzers/macro_narrative.py` - 宏观叙事分析器 ⭐V8.4.2 新增
- `presenters/brief_generator_enhanced.py` - 增强版简报生成器 ⭐新增
- `model_types.py` - 数据类型定义
- `tools/` - CLI 工具 ⭐Phase 5
- `dashboards/` - 系统看板 ⭐Phase 5

**系统指标**:
- Python 文件：100+ 个
- 核心代码：~8,000 行
- 数据源模块：26 个
- 数据库：8 个 SQLite
- 预测模型：2 个 (多因子 + 时序)
- 系统健康度：98%
- **Phase 5**: ✅ 全部完成 (日内分析 + 基金升级 + 股票升级 + 系统透明化)
- **最新版本**: V8.4.2 (宏观叙事分析 + 多源新闻聚合)

---

## 🎯 核心目标

基于**宏观叙事**和**国家政策**分析，为投资决策提供参考：
- **黄金**：价格趋势分析与预测（自动获取实时金价，多数据源验证）
- **基金**：结合政策导向的基金推荐（19311 只基金数据）
- **股票**：宏观视角下的行业/个股分析（行业轮动 + 个股筛选）

**终极目标**：帮助用户在控制风险的前提下实现资产增值

---

## 📊 当前系统功能（V8.4.5）

| 模块 | 功能 | 状态 | 说明 |
|------|------|------|------|
| 金价获取 | 多数据源对比验证 | ✅ 完成 | 东方财富 + 金投网 + 新浪财经 |
| 基金推荐 | 19311 只基金数据 | ✅ 完成 | 按类型分类推荐 |
| 股票分析 | 行业轮动 + 个股筛选 | ✅ 完成 | 基于宏观叙事 |
| 政策新闻 | 多源浏览器获取 | ✅ 完成 | 腾讯 + 百度 + 扩展 |
| 每日简报 | Markdown 自动生成 | ✅ 完成 | **增强版（P0 整合）** |
| SQLite 数据库 | 8 个数据库 | ✅ 完成 | 本地存储 |
| 预测验证 | 每日自动验证 | ✅ 完成 | 今天预测→明天验证 |
| 可视化图表 | matplotlib 生成 | ✅ 完成 | 价格走势 + 准确率 + 热力图 |
| **宏观叙事分析** | **政策→经济→资产→策略** | ✅ **V8.4.2 新增** | **因果推理引擎** ⭐ |
| **多源新闻聚合** | **腾讯 + 百度 + 东方财富 + 和讯 + 新浪** | ✅ **V8.4.2 新增** | **来源多样性优化** ⭐ |
| **预测自动保存** | **简报生成时自动保存** | ✅ **V8.4 新增** | **集成到 main.py** |
| **多数据源验证** | **3 个数据源对比** | ✅ **V8.3 新增** | **置信度评估** |
| **准确率统计** | **7 天/30 天/90 天真实数据** | ✅ **V8.4.3 修复** | **移除模拟数据** ⭐ |
| **国内金价涨跌** | **对比昨收价计算** | ✅ **V8.4.3 新增** | **自动计算涨跌额/幅** ⭐ |
| **方向验证修复** | **基于实际涨跌幅判断** | ✅ **V8.4.4 修复** | **±1% 阈值判断方向** ⭐ |
| **取消震荡预测** | **只保留上涨/下跌** | ✅ **V8.4.5 新增** | **±0.5% 阈值 + 区间±1%** ⭐ |
| **基金净值修复** | **多日期列名检测** | ✅ **V8.4.5 修复** | **支持周末/节假日** ⭐ |
| **情绪分析** | **新闻情绪量化** | ✅ **Phase3.2 完成** | **板块情绪排行** |
| **全球宏观** | **DXY+VIX+Oil** | ✅ **Phase3.4 完成** | **黄金影响因素** |
| **智能预测** | **多因子综合预测** | ✅ **V7.0 完成** | **技术 + 情绪 + 宏观 + 动量** |
| **日内分析** | **黄金小时级分析** | ✅ **Phase5 完成** | **实时推送信号** |
| **基金升级** | **5 种风险画像** | ✅ **Phase5 完成** | **具体买卖时机** |
| **股票升级** | **具体买卖建议** | ✅ **Phase5 完成** | **仓位 + 止损止盈** |
| **系统透明化** | **看板 + 日志** | ✅ **Phase5 完成** | **数据 + 准确率 + 进化** |

### 已归档功能（历史版本）

| 功能 | 状态 | 说明 | 归档位置 |
|------|------|------|----------|
| 交易系统 | 📁 已归档 | 信号生成 + 模拟交易 | `archive/scripts/` |
| 回测引擎 | 📁 已归档 | 策略历史验证 | `archive/scripts/` |

**说明**: 交易系统和回测框架因策略效果未达预期，已归档至 `archive/` 目录，系统重心转向预测准确率提升。

---

## 🚀 使用方法

### 快速生成简报
```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 一键运行（推荐）
./run_daily.sh                      # 自动完成：验证→获取数据→生成简报

# 手动运行
python3 main.py brief               # 生成每日简报（自动保存预测）
```

### 单独功能
```bash
# 获取数据
python3 main.py data --type all     # 获取所有数据
python3 main.py data --type gold    # 仅获取金价

# 生成预测
python3 main.py predict             # 生成预测（自动保存）

# 验证预测
python3 scripts/verify_predictions.py  # 验证昨日预测

# 获取金价（多数据源）
python3 scripts/gold_price_auto_v83.py
```

### CLI 工具（Phase 5）
```bash
# 黄金日内分析
python3 tools/intraday_cli.py analyze

# 基金推荐
python3 tools/fund_cli.py recommend --risk balanced

# 股票精选
python3 tools/stock_cli.py picks --top-n 5

# 系统看板
python3 dashboards/dashboard_service.py
```

---

## 📁 文件结构（V8.4）

```
Macro-Investment-Assistant/
├── main.py                          # 主入口 ⭐
├── run_daily.sh                     # 每日简报脚本 ⭐
├── model_types.py                   # 数据类型定义
├── config.yaml                      # 配置文件
├── SKILL.md                         # 本文档
├── README.md                        # 项目说明
├── QUICK_START.md                   # 快速开始指南
│
├── data/                            # 数据目录
│   ├── db/                          # 数据库（8 个）
│   │   ├── predictions.db           # 预测记录 ⭐
│   │   ├── gold_prices.db           # 金价历史
│   │   ├── fund_data.db             # 基金数据
│   │   ├── fund_nav.db              # 基金净值
│   │   ├── macro_indicators.db      # 宏观指标
│   │   ├── policies.db              # 政策新闻
│   │   ├── trading.db               # 交易记录
│   │   └── accuracy.db              # 准确率统计
│   └── cache/                       # 缓存目录
│
├── data_sources/                    # 数据源（26 个模块）
│   ├── gold_source.py               # 金价数据源 ⭐
│   ├── fund_source.py               # 基金数据源
│   ├── stock_source.py              # 股票数据源
│   ├── macro_source.py              # 宏观数据源
│   ├── news_source.py               # 新闻数据源
│   └── ... (21 个模块)
│
├── analyzers/                       # 分析器（17 个）
│   ├── technical.py                 # 技术分析
│   ├── sentiment.py                 # 情绪分析
│   ├── macro.py                     # 宏观分析
│   ├── momentum.py                  # 动量分析
│   ├── accuracy_tracker.py          # 准确率追踪 ⭐
│   └── ... (12 个)
│
├── predictors/                      # 预测器（8 个）
│   ├── multi_factor.py              # 多因子预测器 ⭐
│   ├── simple_ts_predictor.py       # 时序预测器
│   └── validator.py                 # 预测验证器 ⭐
│
├── presenters/                      # 展示器（7 个）
│   ├── brief_generator.py           # 简报生成器
│   ├── brief_generator_enhanced.py  # 增强版简报生成器 ⭐
│   └── chart_generator.py           # 图表生成器
│
├── scripts/                         # 脚本（10 个）
│   ├── verify_predictions.py        # 预测验证 ⭐
│   ├── gold_price_auto_v83.py       # 金价获取 V8.3 ⭐
│   ├── daily_brief_v8.py            # 每日简报 V8
│   └── ... (7 个)
│
├── api/                             # API 服务（9 个）
│   ├── main.py                      # API 主服务
│   ├── data_api.py                  # 数据 API
│   └── start.sh                     # 启动脚本
│
├── tools/                           # CLI 工具（Phase 5）
│   ├── intraday_cli.py              # 日内分析
│   ├── fund_cli.py                  # 基金推荐
│   └── stock_cli.py                 # 股票分析
│
├── dashboards/                      # 系统看板（Phase 5）
│   ├── dashboard_service.py         # 看板服务
│   ├── accuracy_dashboard.py        # 准确率看板
│   └── ... (3 个)
│
├── daily_brief/                     # 每日简报（30+ 份）
│   └── brief_v8_*.md                # 生成的简报
│
├── docs/                            # 文档（26+ 个）
│   ├── USER_GUIDE.md                # 用户指南（25KB）
│   ├── ARCHITECTURE.md              # 架构说明（17KB）
│   ├── QUICK_REFERENCE.md           # 快速参考（7KB）
│   ├── PREDICTION_SAVE_FIX_REPORT.md # 预测保存修复 ⭐
│   ├── SKILL_MD_VS_ACTUAL_SYSTEM.md # 文档对比分析 ⭐
│   └── ... (21 个)
│
└── archive/                         # 归档（历史版本）
    ├── scripts/                     # 归档脚本
    └── phase_docs/                  # 归档文档
```

---

## 📚 文档索引（V8.4）

| 文档 | 用途 | 大小 | 位置 |
|------|------|------|------|
| **USER_GUIDE.md** | 完整使用指南 | 25KB | `docs/` |
| **ARCHITECTURE.md** | 系统架构说明 | 17KB | `docs/` |
| **QUICK_REFERENCE.md** | 快速参考卡 | 7KB | `docs/` |
| **QUICK_START.md** | 快速开始指南 | 11KB | 根目录 |
| **SKILL_MD_VS_ACTUAL_SYSTEM.md** | SKILL 对比分析 | 8KB | `docs/` ⭐新增 |
| **SYSTEM_FILE_STRUCTURE.md** | 系统文件结构 | 9KB | `docs/` ⭐新增 |
| **PREDICTION_SAVE_FIX_REPORT.md** | 预测保存修复 | 9KB | `docs/` ⭐新增 |
| **FIX_SUMMARY_20260408.md** | 今日修复总结 | 5KB | `docs/` ⭐新增 |
| **PATH_CHANGE_NOTICE.md** | 路径变更通知 | 3KB | `docs/` ⭐新增 |
| **PHASE5_COMPLETE.md** | Phase 5 总结 | 7KB | `docs/` |

**推荐阅读顺序**：
1. 新手：`QUICK_START.md` → `docs/USER_GUIDE.md`
2. 进阶：`docs/QUICK_REFERENCE.md` → `docs/ARCHITECTURE.md`
3. 开发：`docs/SKILL_MD_VS_ACTUAL_SYSTEM.md` → 源码

---

## 📈 预测准确率

### 统计周期
- **7 天准确率**: 自动统计（需要 7 天数据积累）
- **30 天准确率**: 自动统计（需要 30 天数据积累）
- **90 天准确率**: 自动统计（需要 90 天数据积累）

### 验证系统
- **自动验证**: 每日上午执行 `run_daily.sh` 时自动验证昨日预测
- **手动验证**: `python3 scripts/verify_predictions.py`
- **报告位置**: 简报中的"预测准确率历史"章节

### 准确率目标
- **短期目标**: 60%+
- **优化机制**: 基于历史准确率自动调整因子权重
- **反馈闭环**: 预测→验证→统计→优化

---

## 🧠 宏观叙事框架

### 核心逻辑

```
政策/事件 → 经济影响 → 资产价格 → 投资策略
─────────────────────────────────────────────
例：两会提出"新质生产力"
  → 科技投入增加
  → 科技行业盈利预期↑
  → 科技基金/股票受益
```

### 主要宏观因子

| 因子 | 来源 | 影响资产 |
|------|------|---------|
| 货币政策 | 央行 | 债券、黄金、成长股 |
| 财政政策 | 财政部 | 基建、周期股 |
| 产业政策 | 发改委 | 相关行业 |
| 地缘政治 | 国际新闻 | 黄金、原油、避险资产 |
| 美联储政策 | FOMC | 美元、黄金、新兴市场 |
| 中国经济数据 | 统计局 | A 股、人民币资产 |

---

## 📰 数据源列表（26 个模块）

### 金价数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| 东方财富 | `gold_source.py` | COMEX 黄金期货 ⭐主数据源 |
| 金投网 | `gold_browser_source.py` | 实时金价 |
| 新浪财经 | `gold_realtime.py` | 黄金频道 |
| 百度金价 | `gold_baidu.py` | 备用数据源 |

### 基金数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| AKShare | `fund_source.py` | 19311 只基金数据 |

### 股票数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| 东方财富 | `stock_source.py` | 个股行情 + 资金流向 |

### 宏观数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| 统计局 | `macro_source.py` | GDP/CPI/PMI 等 |
| 央行 | `macro_source.py` | 利率/准备金率等 |

### 新闻数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| 腾讯新闻 | `news_source.py` | 财经新闻 |
| 百度新闻 | `news_source.py` | 综合新闻 |
| 和讯财经 | `news_source.py` | 专业财经 |

### 其他数据源
| 数据源 | 文件 | 说明 |
|--------|------|------|
| 事件日历 | `event_calendar.py` | 重大事件提醒 |
| 恐慌贪婪指数 | `fear_greed_index.py` | 市场情绪指标 |

---

## 🔄 预测验证机制

### 工作流程
```
每日生成预测 → 保存到数据库 → 次日获取实际价格 → 验证准确性 → 更新统计
```

### 验证逻辑
1. **方向判断**: 上涨/下跌/震荡
2. **价格区间**: 预测区间是否命中
3. **误差计算**: 绝对误差 + 相对误差
4. **准确率统计**: 7 天/30 天/90 天

### 自动化
- **集成到 run_daily.sh**: 步骤 0 自动验证昨日预测
- **集成到 main.py**: 生成简报时自动保存今日预测

---

## ⚙️ 依赖项

```bash
# 核心依赖
pip install akshare>=1.12 pandas>=1.5 numpy>=1.20

# 数据库
pip install sqlite3

# 网页爬取（可选）
pip install requests beautifulsoup4 lxml playwright

# 可视化
pip install matplotlib

# API 服务
pip install fastapi uvicorn pydantic
```

---

## 🚨 注意事项

1. **数据延迟**：免费数据源可能有 15 分钟延迟
2. **网络问题**：部分接口可能因网络问题失败，已添加多数据源备份
3. **政策解读**：政策影响需结合市场实际情况，避免过度解读
4. **黑天鹅**：宏观框架无法预测突发事件
5. **合规风险**：仅提供分析参考，不构成投资建议
6. **预测准确率**：当前目标准确率 60%+，需持续积累数据

---

## 📈 版本历史

### V8.4.2 (2026-04-08) - 当前版本
- ✅ 宏观叙事分析器 (`analyzers/macro_narrative.py`)
- ✅ 政策→经济→资产→策略因果推理引擎
- ✅ 腾讯新闻数据源（`site:qq.com` 搜索）
- ✅ 新浪财经数据源（浏览器抓取）
- ✅ 新闻来源多样性优化
- ✅ 简报新增「宏观叙事分析」章节
- ✅ 新闻部分显示所有数据来源

### V8.4.1 (2026-04-08)
- ✅ 预测自动保存集成到 `main.py`
- ✅ 预测验证集成到 `run_daily.sh`
- ✅ 准确率查询逻辑修复
- ✅ 系统路径变更：`skills` → `skills`

### V8.3.0 (2026-04-07)
- ✅ 多数据源金价验证（3 个数据源）
- ✅ 置信度评估机制
- ✅ 误差标注机制

### V8.2.0 (2026-04-01)
- ✅ Phase 5 全部完成
- ✅ 系统透明化（看板 + 日志）

### V8.1.0 (2026-03-25)
- ✅ 多因子预测系统
- ✅ 情绪分析量化

---

## 🎯 下一步计划

### 持续优化
1. **准确率提升** - 目标 60%+，基于历史数据优化权重
2. **数据源扩展** - 增加更多可靠数据源
3. **性能优化** - 提升数据获取和生成速度

### 功能增强
1. **告警系统完善** - 低置信度告警、大幅波动告警
2. **可视化增强** - 更多图表类型，交互式看板
3. **文档完善** - 持续更新文档，保持与实际一致

---

*最后更新：2026-04-08*  
*版本：8.4.2*  
*维护 Agent: Investment Steward (5aQmuc)*  
*系统路径：~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant*
