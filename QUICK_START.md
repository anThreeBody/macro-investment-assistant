# 投资分析系统 V8.1 - 快速使用指南

**版本**: V8.1 Phase 5  
**更新日期**: 2026-04-02  
**状态**: ✅ Phase 5 全部完成 | ⚠️ 金价数据需手动更新

---

## ⚠️ 重要提醒：金价数据更新

由于数据源变更，**金价需要手动更新**。请在每次使用前更新金价：

```bash
# 更新金价（根据实际市场价格）
python data_sources/gold_emergency_fix.py --update --intl 2350 --domestic 548

# 查看当前金价
python data_sources/gold_emergency_fix.py --show
```

**参考价格**（2025年4月）：
- 国际金价：约 $2350-2400 USD/oz
- 国内金价：约 ¥545-560 CNY/g

---

## 🚀 快速开始

### 1. 更新金价数据（必需）

```bash
# 更新金价（根据实际市场价格调整参数）
python data_sources/gold_emergency_fix.py --update --intl 2350 --domestic 548

# 验证金价
python data_sources/gold_emergency_fix.py --show
```

### 2. 生成每日简报

```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 方式 1: 使用脚本
./run_daily_v8.sh

# 方式 2: 使用 Python
python3 main.py brief --verbose
```

**输出**:
- 每日简报：`daily_brief/brief_v8_YYYYMMDD.md`
- 数据快照：`data/daily/JSON/brief_v8_YYYYMMDD.json`
- 图表（可选）：`charts/` 目录

---

## 🆕 Phase 5 新增功能

### 2. 黄金日内分析

小时级黄金分析和实时交易信号：

```bash
# 分析当前黄金
python tools/intraday_cli.py analyze

# 查看当前交易信号
python tools/intraday_cli.py signal

# 查看推送历史
python tools/intraday_cli.py history
```

**输出示例**:
```
🎯 黄金日内分析
当前价格: ¥1059.35
交易信号: BUY (置信度: 75%)
支撑位: ¥1050.00 / ¥1040.00
阻力位: ¥1070.00 / ¥1080.00
建议: 在¥1055-1060区间买入
止损: ¥1045 (-1.4%) / 止盈: ¥1075 (+1.5%)
```

---

### 3. 基金个性化推荐

根据风险偏好获取基金推荐：

```bash
# 保守型 (债券70%)
python tools/fund_cli.py recommend --risk conservative

# 稳健型 (债券50%)
python tools/fund_cli.py recommend --risk moderate

# 平衡型 (混合40%) ⭐推荐
python tools/fund_cli.py recommend --risk balanced --top-n 3

# 积极型 (股票60%)
python tools/fund_cli.py recommend --risk aggressive

# 进取型 (股票80%)
python tools/fund_cli.py recommend --risk speculative

# 查看具体基金时机
python tools/fund_cli.py timing --code 163402

# 查看详细理由
python tools/fund_cli.py reason --code 163402
```

**输出示例**:
```
💼 组合配置建议: 混合型 40% + 股票型 30% + 债券型 20% + 指数型 10%

⭐ 推荐基金:
1. 兴全趋势投资混合 (163402)
   类型: 混合型 | 风险等级: 3
   近1年收益: 8.0% | 波动率: 15.0%
   综合得分: 28.6
   买入时机: 当前可买入
   目标涨幅: +8% | 止损: -5% | 止盈: +15%
```

---

### 4. 股票分析升级

获取具体买卖建议：

```bash
# 分析个股
python tools/stock_cli.py analyze --code 000001 --name 平安银行 --price 12.50

# 查看今日精选
python tools/stock_cli.py picks --top-n 5

# 生成股票报告
python tools/stock_cli.py report --show
```

**输出示例**:
```
📊 分析结果:
  股票: 平安银行 (000001)
  信号: 买入 (置信度: 71%)
  目标价格: ¥13.50
  止损价格: ¥11.88 (-5%)
  止盈价格: ¥14.37 (+15%)
  建议仓位: 10-20%
  持有周期: 1-3个月
```

---

### 5. 系统透明化看板

查看系统运行状态：

```bash
# 一键生成所有看板
python dashboards/dashboard_service.py

# 单独查看数据资产
python dashboards/data_asset_dashboard.py

# 单独查看准确率
python dashboards/accuracy_dashboard.py

# 查看系统进化日志
python dashboards/evolution_log.py
```

**输出文件**:
- `dashboards/data_assets_YYYYMMDD.md` - 数据资产看板
- `dashboards/accuracy_YYYYMMDD.md` - 准确率看板
- `dashboards/master_YYYYMMDD.md` - 主看板
- `docs/EVOLUTION_LOG.md` - 进化日志

**输出示例**:
```
📊 系统透明化看板

📁 数据资产:
  总记录数: 19,321
  每日新增: 55
  平均质量: 90%

🎯 预测准确率:
  总体准确率: 统计中
  覆盖品类: 黄金/基金/股票/宏观

🔄 系统进化:
  总变更数: 8
  已完成: 8 ✅
```

---

## 📋 命令行接口

### 查看帮助

```bash
python3 main.py --help
```

### 生成简报

```bash
# 基础用法
python3 main.py brief

# 详细输出
python3 main.py brief --verbose

# 生成图表
python3 main.py brief --charts

# 指定日期
python3 main.py brief --date 2026-03-25
```

### 生成预测

```bash
# 快速预测
python3 main.py predict

# 详细预测
python3 main.py predict --verbose
```

### 获取数据

```bash
# 获取所有数据
python3 main.py data

# 获取特定数据
python3 main.py data --data-type gold
python3 main.py data --data-type fund
python3 main.py data --data-type stock
```

---

## 💻 编程接口

### 基础用法

```python
from main import InvestmentSystem

# 创建系统实例
system = InvestmentSystem()

# 生成每日简报
brief = system.run_daily_brief(save=True, generate_charts=True)

# 查看简报内容
print(brief['brief_content'])

# 查看预测结果
print(brief['prediction'])

# 关闭系统
system.close()
```

### 高级用法

```python
from main import InvestmentSystem
from presenters.brief_generator import BriefGenerator
from presenters.chart_generator import ChartGenerator
from notifiers.alert_notifier import AlertNotifier

system = InvestmentSystem()

# 1. 获取数据
data = system.data_api.get_all_data()

# 2. 生成预测
prediction = system.predictor.predict(data)

# 3. 生成简报
brief_content = system.brief_gen.generate(data, prediction)

# 4. 生成图表
system.chart_gen.generate_price_chart(
    prices=data.get('prices', []),
    title="金价走势"
)

system.chart_gen.generate_prediction_chart(
    current_price=prediction.get('current_price', 0),
    prediction=prediction
)

# 5. 发送告警
if prediction.get('confidence') == '低':
    system.alert.alert_low_confidence(prediction)

system.close()
```

---

## 📊 输出示例

### 每日简报

```markdown
# 📊 投资每日简报

**日期**: 2026-03-25  
**生成时间**: 2026-03-25 19:53:34  
**版本**: V8.0

---

## 💰 黄金价格

| 类型 | 价格 | 涨跌额 | 涨跌幅 |
|------|------|--------|--------|
| 国际金价 | $234.76 | 0.0 | 0.0% |
| 国内金价 | ¥1014.02 | 0.0 | 0.0% |

## 🔮 明日预测

- **当前价格**: ¥1014.02
- **预测价格**: ¥1014.02
- **预测区间**: ¥993.74 - ¥1034.30
- **预测方向**: 震荡
- **置信度**: 高
- **交易信号**: 持有
```

### 告警通知

```
时间：2026-03-25 19:53:34
级别：WARNING
类别：prediction

⚠️ 低置信度预测告警

预测置信度：低
置信度得分：0.350

建议：谨慎参考此预测，等待更高置信度信号。
```

---

## 📁 文件结构

```
Macro-Investment-Assistant/
├── main.py                    # 主入口
├── run_daily_v8.sh            # 每日运行脚本
├── daily_brief/               # 每日简报
│   └── brief_v8_YYYYMMDD.md
├── charts/                    # 图表
│   ├── price_chart_*.png
│   ├── prediction_chart_*.png
│   └── factor_heatmap_*.png
├── dashboards/                # 系统看板 ⭐Phase 5新增
│   ├── data_asset_dashboard.py
│   ├── accuracy_dashboard.py
│   ├── evolution_log.py
│   ├── dashboard_service.py
│   └── master_YYYYMMDD.md
├── alerts/                    # 告警记录
│   └── alert_*_*.txt
├── data/                      # 数据
│   ├── cache/                 # 缓存
│   ├── daily/                 # 每日数据
│   └── db/                    # 数据库
├── analyzers/                 # 分析层
│   ├── intraday_gold.py       # ⭐Phase 5新增
│   ├── fund_recommender.py    # ⭐Phase 5新增
│   ├── stock_recommender.py   # ⭐Phase 5新增
│   └── accuracy_tracker.py
├── services/                  # 服务层 ⭐Phase 5新增
│   ├── gold_intraday_service.py
│   ├── fund_analysis_service.py
│   └── stock_analysis_service.py
├── tools/                     # CLI工具 ⭐Phase 5新增
│   ├── intraday_cli.py
│   ├── fund_cli.py
│   └── stock_cli.py
├── presenters/                # 输出层
└── notifiers/                 # 通知层
```

---

## 🔧 配置选项

### 环境变量

```bash
# 设置日志级别
export LOG_LEVEL=INFO  # DEBUG/INFO/WARNING/ERROR

# 设置数据目录
export DATA_DIR=/path/to/data

# 设置缓存目录
export CACHE_DIR=/path/to/cache
```

### 代码配置

```python
# 在 main.py 中修改配置
class InvestmentSystem:
    def __init__(self):
        self.config = {
            'save_data': True,          # 是否保存数据
            'generate_charts': False,   # 是否生成图表
            'send_alerts': True,        # 是否发送告警
            'log_level': 'INFO',        # 日志级别
        }
```

---

## ⚠️ 注意事项

### 数据源

- **金价**: 金投网（实时）
- **基金**: AKShare（可能延迟）
- **股票**: AKShare（可能延迟）
- **新闻**: 本地缓存（需更新）

### 依赖

```bash
# 必需
pip3 install akshare pandas numpy

# 可选（图表生成）
pip3 install matplotlib

# 可选（高级功能）
pip3 install prophet scikit-learn
```

### 已知问题

1. **AKShare 兼容性**: 部分接口可能返回 0 或空数据
2. **新闻数据**: 依赖本地缓存，需定期更新
3. **图表生成**: 需要 matplotlib，否则跳过

---

## 🆘 常见问题

### Q: 简报生成失败？

A: 检查日志输出，常见原因：
- 网络问题导致数据获取失败
- 缓存文件损坏（删除 `data/cache/` 重试）
- 依赖库未安装

### Q: 图表不生成？

A: 安装 matplotlib：
```bash
pip3 install matplotlib
```

### Q: 告警不发送？

A: 告警已保存到 `alerts/` 目录，查看该目录文件。

### Q: 数据为 0 或空？

A: 可能是 AKShare 接口问题，使用兜底数据或等待修复。

---

## 📞 技术支持

如有问题，请查看：

1. **日志文件**: 终端输出
2. **错误信息**: 查看 traceback
3. **文档**: `REFACTORING_GUIDE.md`
4. **示例**: `PHASE2_SUMMARY.md`

---

## 📊 日常使用流程

```bash
# 1. 早上 8:00 - 生成每日简报
python main.py brief

# 2. 查看基金推荐（根据风险偏好）
python tools/fund_cli.py recommend --risk balanced

# 3. 查看股票精选
python tools/stock_cli.py picks --top-n 5

# 4. 盘中监控黄金（交易时间）
python tools/intraday_cli.py signal

# 5. 周末查看系统状态
python dashboards/dashboard_service.py
```

---

## 🎉 开始使用

```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 生成每日简报
python3 main.py brief --verbose

# 或查看基金推荐
python3 tools/fund_cli.py recommend --risk balanced
```

**祝使用愉快！** 🚀

---

*最后更新: 2026-04-01*  
*版本: V8.1 Phase 5*
