# Macro Investment Assistant - 更新日志

**最后更新**: 2026-04-03

---

## V8.2.0 (2026-04-03) - 金价实时获取系统 ✅

### 🎯 核心目标：从手动配置 → 浏览器实时获取

#### 1. 金价数据源升级
- **模块**: `data_sources/gold_source.py` (重写)
- **功能**: 使用浏览器访问东方财富获取实时金价
- **数据源**: 东方财富 COMEX 黄金期货 (GC00Y)
- **URL**: http://quote.eastmoney.com/unify/r/101.GC00Y

**核心特性**:
- ✅ 每次执行都实时获取最新价格
- ✅ 获取不到就报错，不给预估价
- ✅ 统一使用浏览器获取东方财富数据

**获取数据**:
- 最新价（美元/盎司）
- 涨跌额
- 涨跌幅
- 昨收价
- 最高价
- 最低价
- 成交量
- 持仓量

#### 2. 新增模块
```
data_sources/
├── gold_browser.py            # 浏览器获取模块 ⭐
├── gold_browser_scraper.py    # 数据解析模块 ⭐
└── gold_baidu_search.py       # 百度搜索模块（备用）⭐

docs/
├── GOLD_BROWSER_SOURCE.md     # 使用文档 ⭐
├── GOLD_INTEGRATION_COMPLETE.md # 整合报告 ⭐
└── GOLD_PRICE_FINAL.md        # 最终方案 ⭐
```

#### 3. 数据验证
- **价格区间**: 国际$1800-5500/oz，国内¥450-1200/g
- **合理性检查**: 自动验证价格是否在合理区间
- **数据清洗**: 标准化格式，确保数据质量

#### 4. 换算公式
```
国内金价 (元/克) = 国际金价 (美元/盎司) × 汇率 ÷ 31.1035

其中：
- 1 金衡盎司 = 31.1034768 克
- 汇率默认：7.25 CNY/USD（可配置）
```

#### 5. 使用方法

**基础使用**:
```python
from data_sources.gold_source import GoldDataSource

ds = GoldDataSource()
data = ds.fetch()

print(f"国际金价：${data['international']['price']}")
print(f"国内金价：¥{data['domestic']['price']}")
```

**生成简报**:
```bash
python3 main.py brief
```

**输出示例**:
```
INFO:[金价数据] 获取成功 - 国际：$4989.30/oz (-2.29%), 国内：¥1162.97/g
```

#### 6. 技术实现

**获取流程**:
```
1. 使用 browser_use 打开东方财富页面
2. 等待 5 秒让数据加载完成
3. 提取页面文本内容
4. 使用正则表达式解析价格数据
5. 验证价格合理性
6. 计算国内金价（基于汇率）
7. 返回标准格式数据
```

**依赖**:
```bash
pip install browser-use playwright
playwright install chromium
```

#### 7. 废弃功能
- ❌ `gold_emergency_fix.py` - 不再需要手动配置
- ❌ `gold_final.py` - 已被浏览器方案替代

---

## V8.1.0 (2026-04-02) - 金价数据修复 ✅

### 🎯 核心目标：修复金价数据准确性问题

#### 问题汇总
- akshare 接口废弃（2016 年数据）
- 期货价格误作现货（¥1053 vs ¥548）
- 国际金价计算错误（4000-5000 美元）
- 缓存机制问题（数据不更新）

#### 解决方案
- 紧急修复模块：手动配置价格
- 修正换算公式
- 添加价格验证

---

## Phase 5 Stage 2 (2026-04-01) - 基金分析升级 ✅

### 🎯 核心目标: 从通用推荐 → 个性化 + 可执行建议

#### 1. 基金推荐个性化
- **模块**: `analyzers/fund_recommender.py`
- **功能**: 根据用户风险偏好推荐基金
- **风险偏好**: 保守型/稳健型/平衡型/进取型/激进型
- **评估维度**: 年龄、投资期限、收入稳定性、风险承受能力、投资经验

**组合配置建议**:
| 风险偏好 | 债券型 | 混合型 | 股票型 | 指数型 | QDII |
|---------|--------|--------|--------|--------|------|
| 保守型 | 60% | 10% | - | - | - |
| 稳健型 | 40% | 40% | - | 20% | - |
| 平衡型 | 20% | 40% | 30% | 10% | - |
| 进取型 | - | 30% | 50% | - | 20% |
| 激进型 | - | - | 60% | - | 25% |

#### 2. 基金买卖点建议
- **模块**: `analyzers/fund_timing_advisor.py`
- **功能**: 提供具体的买入/卖出时机
- **分析维度**: 技术面(35%) + 基本面(35%) + 情绪面(30%)
- **信号类型**: 买入/卖出/观望
- **信号强度**: 强烈/中等/较弱

**交易策略**:
- 目标涨幅: +5%
- 止损设置: -3%
- 止盈目标: +10%
- 仓位建议: 20-30%
- 持有周期: 1-6个月

#### 3. 基金理由增强
- **模块**: `analyzers/fund_reason_enhancer.py`
- **功能**: 政策+情绪+业绩详细分析
- **政策分析**: 识别行业政策关键词，判断政策趋势
- **情绪分析**: 资金流向 + 市场情绪综合评分
- **业绩分析**: 短期/长期业绩 + 风险调整收益 + 回撤控制

**输出格式**:
```
【政策】政策面利好科技成长，相关政策持续出台...
【情绪】市场情绪乐观，资金明显流入...
【业绩】业绩表现近1年收益优秀(25.0%)，超额收益显著...
```

#### 4. 新增文件
```
analyzers/
├── fund_recommender.py        # 基金推荐器 ⭐
├── fund_timing_advisor.py     # 买卖点顾问 ⭐
└── fund_reason_enhancer.py    # 理由增强器 ⭐

services/
└── fund_analysis_service.py   # 基金分析服务 ⭐

tools/
└── fund_cli.py                # 基金CLI工具 ⭐
```

#### 5. 使用方法

**交互式风险评估**:
```bash
python tools/fund_cli.py assess
```

**基金推荐**:
```bash
python tools/fund_cli.py recommend --risk balanced --top-n 5
```

**买卖点建议**:
```bash
python tools/fund_cli.py timing --code 005911 --nav 2.4567
```

**生成报告**:
```bash
python tools/fund_cli.py report --risk moderate --show
```

---

## Phase 5 Stage 1 (2026-04-01) - 黄金日内分析系统 ✅

### 🎯 核心目标: 从日级预测 → 时级交易

#### 1. 日内最佳买卖时机识别
- **模块**: `analyzers/intraday_gold.py`
- **功能**: 小时级金价分析，识别最佳买卖点
- **指标**: RSI、MACD、支撑/阻力位
- **信号**: 买入/卖出/观望

#### 2. 实时时机主动推送
- **模块**: `notifiers/realtime_pusher.py`
- **功能**: 高置信度信号自动推送
- **阈值**: 最小置信度 0.7
- **冷却**: 30分钟防重复
- **上限**: 每日最多10次

#### 3. 预测置信度分级
- **高置信度** (≥0.8): 强烈信号，建议操作
- **中置信度** (0.6-0.8): 潜在机会，谨慎操作
- **低置信度** (<0.6): 信号不足，建议观望

#### 4. 预测准确率统计
- **模块**: `analyzers/accuracy_tracker.py`
- **统计**: 7天/30天/90天准确率
- **存储**: SQLite数据库
- **报告**: 自动生成准确率报告

#### 5. 新增文件
```
analyzers/
├── intraday_gold.py           # 日内分析器 ⭐
└── accuracy_tracker.py        # 准确率追踪 ⭐

notifiers/
└── realtime_pusher.py         # 实时推送服务 ⭐

services/
└── gold_intraday_service.py   # 集成服务 ⭐

tools/
└── intraday_cli.py            # CLI工具 ⭐
```

#### 6. 使用方法
```bash
# 分析当前机会
python tools/intraday_cli.py analyze

# 查看最佳交易时段
python tools/intraday_cli.py best-hours

# 查看准确率统计
python tools/intraday_cli.py accuracy
```

#### 7. 最佳交易时段
| 时段 | 时间 | 波动率 | 优先级 |
|------|------|--------|--------|
| 欧美重叠 | 21:00-23:00 | 最高 | ⭐⭐⭐ |
| 亚欧重叠 | 15:00-17:00 | 中高 | ⭐⭐ |
| 美洲时段 | 21:00-05:00 | 最高 | ⭐⭐ |
| 欧洲时段 | 15:00-23:00 | 高 | ⭐ |

---

## 历史版本归档

**说明**: 以下版本已归档至 `docs/archive/CHANGELOG_HISTORY.md`

- Phase 3.5 (2026-03-19) - 回测框架
- Phase 3.4 (2026-03-19) - 全球宏观
- Phase 3.2 (2026-03-19) - 情绪分析
- Phase 3.1 (2026-03-19) - 机器学习预测
- V5.2.0 (2026-03-19) - 交易系统
- V5.1.1 (2026-03-19) - 预测验证优化
- V5.1.0 (2026-03-19) - 功能完善
- V6.0.0 (2026-03-19) - Phase 2 完成
- V5.0.0 (2026-03-19) - Phase 1 完成

---

## Phase 5 Stage 3 (2026-04-01) - 股票分析升级 ✅

### 🎯 核心目标: 从"观察用" → 具体买卖建议

#### 1. 个股推荐升级
- **模块**: `analyzers/stock_recommender.py`
- **功能**: 从"观察"到具体买卖建议
- **信号类型**: 强烈买入/买入/持有/卖出/强烈卖出
- **分析维度**: 技术面(40%) + 基本面(35%) + 资金面(25%)

**技术指标**:
- RSI (相对强弱指数)
- MACD (指数平滑异同平均线)
- 均线系统 (MA5/MA10/MA20/MA60)
- 布林带 (Bollinger Bands)
- 成交量分析

**基本面指标**:
- PE (市盈率)
- PB (市净率)
- ROE (净资产收益率)
- 营收增长率
- 利润增长率
- 负债率

**资金面指标**:
- 主力资金流向
- 北向资金流向
- 换手率
- 融资融券余额

**交易策略**:
- 目标涨幅: +8%
- 止损设置: -5%
- 止盈目标: +15%
- 仓位建议: 10-30%
- 持有周期: 1-3个月

#### 2. 个股理由详化
- **模块**: `analyzers/stock_reason_detailer.py`
- **功能**: 技术面+基本面+资金面详细分析
- **输出**: 详细的分析报告，包含投资逻辑和风险提示

**分析内容**:
```
【技术面】
- 趋势分析: 均线排列、趋势方向
- RSI指标: 超买超卖判断
- MACD指标: 金叉死叉、动能分析
- 布林带: 位置判断、波动区间
- 成交量: 量价配合分析

【基本面】
- 估值分析: PE/PB vs 行业平均
- 盈利能力: ROE分析
- 成长性: 营收/利润增长
- 财务健康: 负债率分析

【资金面】
- 主力资金: 流入流出分析
- 北向资金: 外资态度
- 市场活跃度: 换手率
- 杠杆资金: 融资融券

【投资逻辑】
- 催化剂识别
- 风险评估
- 可比公司分析
```

#### 3. 新增文件
```
analyzers/
├── stock_recommender.py       # 个股推荐器 ⭐
└── stock_reason_detailer.py   # 理由详化器 ⭐

services/
└── stock_analysis_service.py  # 股票分析服务 ⭐

tools/
└── stock_cli.py               # 股票CLI工具 ⭐
```

#### 4. 使用方法

**分析个股**:
```bash
python tools/stock_cli.py analyze --code 000001 --name 平安银行 --price 12.50
```

**今日精选**:
```bash
python tools/stock_cli.py picks --top-n 5
```

**生成报告**:
```bash
python tools/stock_cli.py report --show
```

#### 5. Python API

```python
from services.stock_analysis_service import StockAnalysisService

service = StockAnalysisService()

# 全面分析个股
result = service.analyze_stock(
    code="000001",
    name="平安银行",
    industry="银行",
    current_price=12.50,
    price_history=[...],
    volume_history=[...],
    fundamental_data={"pe": 8.5, "pb": 0.9, ...},
    capital_data={"main_force": 1.5, "north_bound": 0.8, ...}
)

# 获取今日精选
picks = service.get_top_picks(top_n=5)

# 生成报告
report = service.generate_stock_report(stocks_data)
```

---

## Phase 5 Stage 4 (2026-04-01) - 系统透明化 ✅

### 🎯 核心目标: 让系统运行状态一目了然

#### 1. 数据资产看板
- **模块**: `dashboards/data_asset_dashboard.py`
- **功能**: 展示系统已积累的数据量
- **统计维度**: 记录数、存储大小、数据质量、最后更新

**数据类别**:
| 类别 | 说明 |
|------|------|
| 黄金价格数据 | 每日国际/国内金价 |
| 预测记录数据 | 所有预测及验证结果 |
| 基金数据 | 19311只基金信息 |
| 新闻情绪数据 | 每日财经新闻及情绪分析 |
| 宏观指标数据 | DXY、VIX、油价、美债收益率 |

**使用方法**:
```python
from dashboards.data_asset_dashboard import DataAssetDashboard

dashboard = DataAssetDashboard()
dashboard.display_dashboard()  # 显示看板
dashboard.save_dashboard()     # 保存看板
```

#### 2. 预测准确率看板
- **模块**: `dashboards/accuracy_dashboard.py`
- **功能**: 展示各品类预测准确率趋势
- **统计周期**: 7天、30天、90天

**指标**:
- 总体准确率
- 各品类准确率 (黄金/基金/股票/宏观)
- 准确率趋势 (6个月)
- 置信度分布

**使用方法**:
```python
from dashboards.accuracy_dashboard import AccuracyDashboard

dashboard = AccuracyDashboard()
dashboard.display_dashboard()
dashboard.save_dashboard()
```

#### 3. 系统进化日志
- **模块**: `dashboards/evolution_log.py`
- **功能**: 记录系统的优化调整历史
- **变更类型**: feature/fix/optimize/refactor

**记录内容**:
- 版本号
- 阶段
- 变更类型
- 标题和描述
- 影响范围
- 状态

**使用方法**:
```python
from dashboards.evolution_log import EvolutionLog, EvolutionRecord

log = EvolutionLog()
log.add_record(EvolutionRecord(...))
log.display_summary()
log.save_changelog()
```

#### 4. 统一看板服务
- **模块**: `dashboards/dashboard_service.py`
- **功能**: 整合所有看板，一键生成

**使用方法**:
```bash
python dashboards/dashboard_service.py
```

**输出文件**:
```
dashboards/
├── data_assets_YYYYMMDD.md    # 数据资产看板
├── accuracy_YYYYMMDD.md       # 准确率看板
├── master_YYYYMMDD.md         # 主看板
docs/
└── EVOLUTION_LOG.md           # 进化日志
```

#### 5. 新增文件
```
dashboards/
├── data_asset_dashboard.py    # 数据资产看板 ⭐
├── accuracy_dashboard.py      # 准确率看板 ⭐
├── evolution_log.py           # 进化日志 ⭐
└── dashboard_service.py       # 统一看板服务 ⭐
```

---

## Phase 5 完成总结 ✅

| 阶段 | 功能 | 状态 |
|------|------|------|
| Stage 1 | 黄金日内分析 | ✅ 完成 |
| Stage 2 | 基金分析升级 | ✅ 完成 |
| Stage 3 | 股票分析升级 | ✅ 完成 |
| Stage 4 | 系统透明化 | ✅ 完成 |

**Phase 5 全部完成！** 🎉

---

*系统版本: V8.2.0 | 最后更新: 2026-04-01*
