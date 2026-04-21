# Macro-Investment-Assistant 系统文件结构

**系统路径**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant`  
**系统版本**: V8.4.1  
**更新时间**: 2026-04-08 11:20

---

## 📂 完整目录结构

```
Macro-Investment-Assistant/
│
├── 📄 核心文件
│   ├── main.py                          # 主入口（10KB）
│   ├── model_types.py                   # 数据类型定义（13KB）
│   ├── config.yaml                      # 配置文件
│   ├── run_daily.sh                     # 每日简报脚本 ⭐
│   ├── run_daily_v8.sh                  # V8 版本脚本
│   ├── SKILL.md                         # 技能说明文档
│   ├── README.md                        # 项目说明
│   ├── QUICK_START.md                   # 快速开始指南
│   └── CHANGELOG.md                     # 变更日志
│
├── 📊 数据模块 (data/)
│   ├── db/                              # 数据库目录
│   │   ├── predictions.db               # 预测记录 ⭐
│   │   ├── gold_prices.db               # 金价历史
│   │   ├── fund_data.db                 # 基金数据
│   │   ├── fund_nav.db                  # 基金净值
│   │   ├── macro_indicators.db          # 宏观指标
│   │   ├── policies.db                  # 政策新闻
│   │   ├── trading.db                   # 交易记录
│   │   └── accuracy.db                  # 准确率统计
│   ├── cache/                           # 缓存目录
│   └── *.json                           # JSON 数据文件
│
├── 📰 数据源 (data_sources/) - 26 个文件
│   ├── base.py                          # 数据源基类
│   ├── gold_source.py                   # 金价数据源 ⭐
│   ├── fund_source.py                   # 基金数据源
│   ├── stock_source.py                  # 股票数据源
│   ├── macro_source.py                  # 宏观数据源
│   ├── news_source.py                   # 新闻数据源
│   ├── event_calendar.py                # 事件日历
│   └── ... (20+ 个数据源模块)
│
├── 📈 分析器 (analyzers/) - 17 个文件
│   ├── technical.py                     # 技术分析
│   ├── sentiment.py                     # 情绪分析
│   ├── macro.py                         # 宏观分析
│   ├── momentum.py                      # 动量分析
│   ├── fear_greed_index.py              # 恐慌贪婪指数
│   ├── accuracy_tracker.py              # 准确率追踪
│   ├── fund_recommender.py              # 基金推荐
│   └── stock_recommender.py             # 股票推荐
│
├── 🔮 预测器 (predictors/) - 8 个文件
│   ├── base.py                          # 预测器基类
│   ├── multi_factor.py                  # 多因子预测器 ⭐
│   ├── simple_ts_predictor.py           # 时序预测器
│   └── validator.py                     # 预测验证器 ⭐
│
├── 📝 展示器 (presenters/) - 7 个文件
│   ├── brief_generator.py               # 简报生成器
│   ├── brief_generator_enhanced.py      # 增强版简报生成器 ⭐
│   ├── chart_generator.py               # 图表生成器
│   └── report_formatter.py              # 报告格式化
│
├── 📜 脚本 (scripts/) - 23 个文件
│   ├── verify_predictions.py            # 预测验证脚本 ⭐
│   ├── gold_price_auto_v83.py           # 金价自动获取 V8.3
│   ├── daily_brief_v8.py                # 每日简报 V8
│   ├── data_manager.py                  # 数据管理
│   ├── fund_recommender.py              # 基金推荐
│   ├── sentiment_analyzer.py            # 情绪分析
│   └── ... (17+ 个脚本)
│
├── 🌐 API 服务 (api/) - 9 个文件
│   ├── main.py                          # API 主服务
│   ├── data_api.py                      # 数据 API ⭐
│   ├── start.sh                         # 启动脚本
│   └── API_GUIDE.md                     # API 使用指南
│
├── 📊 看板 (dashboards/) - 11 个文件
│   ├── dashboard_service.py             # 看板服务
│   └── ... (10+ 个看板模块)
│
├── 📢 通知器 (notifiers/) - 7 个文件
│   ├── alert_notifier.py                # 告警通知
│   └── ... (6+ 个通知模块)
│
├── 🛠️ 工具 (tools/)
│   ├── intraday_cli.py                  # 日内分析 CLI
│   ├── fund_cli.py                      # 基金推荐 CLI
│   └── stock_cli.py                     # 股票分析 CLI
│
├── 🌍 服务 (services/)
│   └── ... (服务模块)
│
├── 📦 数据管道 (data_pipeline/)
│   └── ... (数据处理管道)
│
├── 📊 图表 (charts/)
│   └── *.png                            # 生成的图表
│
├── 📄 每日简报 (daily_brief/) - 31 个文件
│   ├── brief_v8_20260408.md             # 今日简报 ⭐
│   ├── brief_v8_20260407.md             # 昨日简报
│   └── archive/                         # 归档简报
│
├── 📚 文档 (docs/) - 26 个文件
│   ├── USER_GUIDE.md                    # 用户指南（25KB）
│   ├── ARCHITECTURE.md                  # 架构说明（17KB）
│   ├── QUICK_REFERENCE.md               # 快速参考
│   ├── PREDICTION_SAVE_FIX_REPORT.md    # 预测保存修复报告 ⭐
│   ├── FIX_SUMMARY_20260408.md          # 今日修复总结 ⭐
│   ├── PATH_CHANGE_NOTICE.md            # 路径变更通知 ⭐
│   ├── BUG_ANALYSIS_20260408.md         # Bug 分析报告
│   ├── CRON_VERIFY_PREDICTIONS.md       # Cron 配置说明
│   ├── DATA_SOURCES.md                  # 数据源说明
│   ├── ANALYZERS.md                     # 分析器说明
│   ├── AI_MODEL_GUIDE.md                # AI 模型指南
│   ├── INDEX.md                         # 文档索引
│   └── ... (15+ 个文档)
│
├── 📝 报告 (reports/) - 12 个目录
│   └── validation_*.md                  # 验证报告
│
├── 📖 参考 (references/)
│   └── macro_narrative.md               # 宏观叙事框架
│
├── 🧪 示例 (examples/) - 9 个文件
│   └── ... (示例代码)
│
├── 🕸️ Web 界面 (web/)
│   ├── static/                          # 静态资源
│   └── templates/                       # 模板文件
│
├── 🧪 测试 (tests/)
│   └── ... (测试文件)
│
├── 🗄️ 归档 (archive/)
│   ├── phase_docs/                      # 阶段文档
│   └── scripts/                         # 归档脚本
│
├── 📝 日志 (logs/)
│   └── pushes/                          # 推送日志
│
├── 🤖 Agent (agents/)
│   └── Investment-Steward/              # 运维 Agent
│
├── 🚨 告警 (alerts/)
│   └── ... (告警配置)
│
└── 📋 模板 (templates/)
    └── ... (报告模板)
```

---

## 📊 统计信息

| 类别 | 数量 | 说明 |
|------|------|------|
| **Python 文件** | 100+ | 核心代码模块 |
| **Markdown 文档** | 40+ | 文档和报告 |
| **Shell 脚本** | 10+ | 自动化脚本 |
| **数据库文件** | 8 | SQLite 数据库 |
| **每日简报** | 30+ | 生成的简报 |
| **数据源模块** | 26 | 各类数据源 |
| **分析器模块** | 17 | 分析引擎 |
| **文档目录** | 26 | 完整文档体系 |

---

## 🎯 核心模块说明

### 1. 数据源层 (data_sources/)
```
负责从 11+ 个数据源获取数据：
- 金价：东方财富、金投网、新浪财经
- 基金：AKShare（19311 只基金）
- 股票：东方财富、新浪财经
- 宏观：统计局、央行
- 新闻：腾讯、百度、和讯
```

### 2. 分析层 (analyzers/)
```
多维度分析引擎：
- 技术分析：指标计算、趋势判断
- 情绪分析：新闻情绪量化
- 宏观分析：政策解读、经济数据
- 动量分析：资金流向、市场热度
- 准确率追踪：预测验证统计
```

### 3. 预测层 (predictors/)
```
智能预测系统：
- 多因子预测器：技术 + 情绪 + 宏观 + 动量
- 时序预测器：时间序列预测
- 验证器：次日自动验证
```

### 4. 展示层 (presenters/)
```
报告生成引擎：
- 简报生成器：Markdown 日报
- 图表生成器：可视化图表
- 报告格式化：专业报告
```

### 5. API 服务 (api/)
```
RESTful API：
- 数据查询接口
- 预测接口
- 健康检查
- Swagger 文档
```

---

## 🔑 关键文件路径

| 用途 | 文件路径 |
|------|----------|
| **主入口** | `main.py` |
| **每日简报** | `run_daily.sh` |
| **API 服务** | `api/main.py` |
| **预测保存** | `predictors/validator.py` |
| **准确率查询** | `presenters/brief_generator_enhanced.py` |
| **验证脚本** | `scripts/verify_predictions.py` |
| **金价获取** | `data_sources/gold_source.py` |
| **用户指南** | `docs/USER_GUIDE.md` |
| **架构说明** | `docs/ARCHITECTURE.md` |

---

## 📈 数据流向

```
数据源 → 数据获取 → 分析引擎 → 预测引擎 → 简报生成 → 输出
  ↓         ↓          ↓          ↓          ↓         ↓
11+ 源   data_sources  analyzers  predictors presenters  Markdown/API
```

---

## 🎨 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                              │
│         CLI (run_daily.sh)  |  API (HTTP)                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    展示层 (Presenters)                    │
│    简报生成器  |  图表生成器  |  报告格式化                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    预测层 (Predictors)                    │
│    多因子预测器  |  时序预测器  |  验证器                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    分析层 (Analyzers)                     │
│   技术分析 | 情绪分析 | 宏观分析 | 动量分析 | 准确率追踪   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据层 (Data Sources)                  │
│   金价 | 基金 | 股票 | 宏观 | 新闻 | 事件日历             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    存储层 (Database)                      │
│         8 个 SQLite 数据库 | JSON 缓存                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速访问

```bash
# 进入系统目录
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 运行每日简报
./run_daily.sh

# 启动 API 服务
./api/start.sh

# 查看文档
cat docs/USER_GUIDE.md
cat docs/QUICK_REFERENCE.md

# 查看最新简报
ls -lt daily_brief/*.md | head -1
```

---

**文档生成时间**: 2026-04-08 11:20  
**系统版本**: V8.4.1  
**维护 Agent**: Investment Steward (5aQmuc)
