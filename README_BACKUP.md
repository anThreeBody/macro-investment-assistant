# 投资分析系统 - 完整使用指南

**版本**: V8.4.5 + API V1.0.0  
**最后更新**: 2026-04-15  
**状态**: ✅ 生产就绪

---

## 🎯 快速开始

### 方式 1: 命令行工具（传统方式）

```bash
# 一键生成每日简报（包含 P0+P1 所有功能）
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant
./run_daily.sh
```

**适合场景**:
- ✅ 每日定时生成简报
- ✅ 脚本自动化
- ✅ 服务器环境

---

### 方式 2: Web 仪表盘（推荐）⭐

```bash
# 启动 API 服务
./api/start.sh

# 浏览器访问
http://localhost:8000
```

**适合场景**:
- ✅ 实时查看数据
- ✅ 可视化分析
- ✅ 历史数据查询
- ✅ 移动端访问

---

## 📁 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                               │
├──────────────────────┬──────────────────────────────────────┤
│   命令行工具          │      Web 仪表盘                       │
│   ./run_daily.sh     │      http://localhost:8000           │
│   main.py brief      │      (实时可视化)                     │
└──────────────────────┴──────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      API 服务层 (FastAPI)                     │
│  /api/gold/price  │  /api/prediction  │  /api/accuracy     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层                               │
│  data_sources/  │  analyzers/  │  predictors/  │  presenters/ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                               │
│  SQLite (predictions.db, feedback.db)                       │
│  JSON (gold_price_cache.json, briefs)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 使用场景

### 场景 1: 每日查看金价和预测

**命令行方式**:
```bash
./run_daily.sh
cat daily_brief/brief_v8_$(date +%Y%m%d).md
```

**Web 方式**:
```bash
./api/start.sh
# 访问 http://localhost:8000
```

---

### 场景 2: 查看预测准确率

**命令行方式**:
```bash
python3 scripts/prediction_feedback.py --stats
```

**Web 方式**:
```bash
# 访问仪表盘，查看"预测准确率"卡片
# 或调用 API
curl http://localhost:8000/api/accuracy/stats?period=30
```

---

### 场景 3: 获取金价数据（程序调用）

**Python**:
```python
import requests

response = requests.get('http://localhost:8000/api/gold/price')
data = response.json()

print(f"国际金价：${data['international_usd_per_oz']}")
print(f"国内金价：¥{data['domestic_cny_per_gram']}/g")
```

**Shell**:
```bash
curl -s http://localhost:8000/api/gold/price | jq '.'
```

---

### 场景 4: 定时任务（Cron）

```bash
# 每天早上 8 点生成简报
0 8 * * * cd /path/to/Macro-Investment-Assistant && ./run_daily.sh

# 或保持 API 服务运行
@reboot cd /path/to/Macro-Investment-Assistant && ./api/start.sh
```

---

## 📋 功能对比

| 功能 | 命令行 | Web 仪表盘 | API |
|------|--------|-----------|-----|
| 实时金价 | ✅ | ✅ | ✅ |
| 每日简报 | ✅ | ⏳ | ⏳ |
| 预测生成 | ✅ | ✅ | ✅ |
| 准确率统计 | ✅ | ✅ | ✅ |
| 历史数据 | 📁 文件 | 📊 图表 | 🔌 API |
| 可视化 | ❌ | ✅ | ⏳ |
| 实时刷新 | ❌ | ✅ (60s) | ✅ |
| 移动端 | ❌ | ✅ | ✅ |
| 自动化 | ✅ | ❌ | ✅ |

**图例**: ✅ 支持 | ⏳ 待实现 | ❌ 不支持

---

## 📚 文档索引

### 核心文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **系统总览** | `README.md` | 本文档 |
| **使用指南** | `scripts/USAGE_GUIDE.md` | 命令行使用 |
| **API 指南** | `api/API_GUIDE.md` | API 服务使用 |
| **部署说明** | `scripts/DEPLOYMENT_V8.2.md` | V8.2 部署 |
| **P0 完成报告** | `docs/P0_REQUIREMENTS_COMPLETE.md` | P0 需求验收 |
| **P1 完成报告** | `docs/P1_REQUIREMENTS_COMPLETE.md` | P1 需求验收 |
| **P1 总结** | `docs/P1_SUMMARY.md` | P1 实现总结 |

### 技术文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **金价获取** | `docs/GOLD_BROWSER_SOURCE.md` | 浏览器获取金价 |
| **清理报告** | `scripts/CLEANUP_COMPLETE.md` | 代码清理报告 |
| **阶段 1 完成** | `api/PHASE1_COMPLETE.md` | API 开发报告 |

### 技能文档

| 文档 | 位置 |
|------|------|
| **技能说明** | `SKILL.md` |

---

## 📝 文档维护

### 维护规范

**重要**: 所有系统更新必须遵循文档维护规范。

**核心原则**:
1. **及时更新** - 代码变更后立即更新文档
2. **及时同步** - 文档版本与代码保持一致
3. **及时清理** - 测试文件立即删除或归档

**相关文档**:
- `docs/DOCUMENTATION_MAINTENANCE.md` - 完整维护规范
- `docs/CLEANUP_AND_ARCHIVE_REPORT.md` - 清理归档报告

### 维护脚本

```bash
# 清理测试文件和临时文件（建议每周运行）
./scripts/cleanup.sh

# 检查文档质量（每次提交前运行）
./scripts/check_docs.sh

# 归档过期文档（按需运行）
./scripts/archive_docs.sh docs/OLD_FILE.md
```

### 文档状态

| 类别 | 数量 | 位置 |
|------|------|------|
| 有效文档 | 15 | `docs/` |
| 归档文档 | 14 | `docs/archive/2026-04/` |
| 文档健康度 | 100% | ✅ |

**查看文档索引**:
```bash
cat docs/INDEX.md
```

---

## 🔧 常见问题

### Q1: 应该用命令行还是 Web?

**答**: 
- **日常查看** → Web 仪表盘（可视化好）
- **定时任务** → 命令行（稳定可靠）
- **程序集成** → API（灵活方便）

---

### Q2: API 服务需要一直运行吗？

**答**: 
- **不需要**。API 服务按需启动即可。
- 如需实时查看，可后台运行：
  ```bash
  nohup python3 api/main.py > logs/api.log 2>&1 &
  ```

---

### Q3: 数据从哪里来？

**答**:
- **金价**: 东方财富 COMEX 黄金期货（实时）
- **基金**: AKShare
- **预测**: 多因子模型（本地计算）
- **新闻**: 多源聚合

---

### Q4: 预测准确率如何？

**答**:
- **短期**（1-3 天）：目标 > 60%
- **中期**（1-2 周）：目标 > 55%
- **查看方法**:
  ```bash
  curl http://localhost:8000/api/accuracy/stats?period=30
  ```

---

### Q5: 如何更新系统？

**答**:
```bash
# 1. 备份数据
cp -r data/ backup/data_$(date +%Y%m%d)/

# 2. 拉取最新代码
git pull  # 如有版本控制

# 3. 安装依赖
pip install -r api/requirements.txt

# 4. 重启服务
./api/start.sh
```

---

## 📊 系统状态

### 当前版本

| 组件 | 版本 | 状态 |
|------|------|------|
| **核心系统** | V8.4.0 | ✅ 生产就绪 |
| **API 服务** | V1.0.0 | ✅ 生产就绪 |
| **Web 仪表盘** | V1.0.0 | ✅ 生产就绪 |
| **命令行工具** | V8.4.0 | ✅ 生产就绪 |

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/health

# 系统信息
curl http://localhost:8000/api/system/info

# 金价数据
curl http://localhost:8000/api/gold/price
```

---

## 🎯 最佳实践

### 1. 日常使用

```bash
# 早上：启动 API 服务（可选）
./api/start.sh &

# 白天：浏览器查看 http://localhost:8000

# 晚上：生成简报（如未自动生成）
./run_daily.sh
```

### 2. 数据分析

```bash
# 获取金价历史
curl "http://localhost:8000/api/gold/history?days=30" | jq '.'

# 获取预测历史
curl "http://localhost:8000/api/prediction/history?days=30" | jq '.'

# 计算准确率
curl "http://localhost:8000/api/accuracy/stats?period=30" | jq '.accuracy_rate'
```

### 3. 自动化集成

```python
# Python 示例
import requests

API_BASE = 'http://localhost:8000'

def get_gold_price():
    resp = requests.get(f'{API_BASE}/api/gold/price')
    return resp.json()

def get_prediction():
    resp = requests.get(f'{API_BASE}/api/prediction/today')
    return resp.json()

def get_accuracy(days=30):
    resp = requests.get(f'{API_BASE}/api/accuracy/stats?period={days}')
    return resp.json()
```

---

## 🚀 开发计划

### 已完成 ✅

- [x] V8.4.0 核心系统（恐慌贪婪指数 + 事件日历）
- [x] V8.3.0 P0 需求（准确率 + 估值 + 资金流向）
- [x] V8.2.0 核心系统
- [x] 实时金价获取（浏览器）
- [x] 多因子预测
- [x] 预测验证
- [x] API 服务 V1.0.0
- [x] Web 仪表盘 V1.0.0

### 进行中 ⏳

- [ ] 真实数据接入（VIX、北向资金、成交量）
- [ ] 财经日历 API 集成
- [ ] 基金推荐 API
- [ ] 市场概览 API

### 计划中 📅

- [ ] 指数历史走势图表
- [ ] 事件提醒功能
- [ ] Vue 3 重构
- [ ] 用户系统
- [ ] 通知推送
- [ ] 移动端 App

---

## 📞 技术支持

### 查看日志

```bash
# API 日志
tail -f logs/api.log

# 系统日志
tail -f logs/system.log

# 金价日志
tail -f logs/gold.log
```

### 问题排查

1. **检查服务状态**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **查看文档**:
   - API 文档：http://localhost:8000/docs
   - 使用指南：`scripts/USAGE_GUIDE.md`

3. **检查依赖**:
   ```bash
   pip list | grep -E "fastapi|uvicorn|playwright"
   ```

---

## 📝 更新日志

### V8.4.0 (2026-04-07) - P1 增强版

- ✅ **P1-2**: 恐慌贪婪综合指数（5 指标加权）
- ✅ **P1-3**: 重大事件日历（未来 7 天）
- ✅ 简报增强：市场情绪指数 + 事件提醒
- ✅ 新建模块：`fear_greed_index.py`, `event_calendar.py`

### V8.3.0 (2026-04-07) - P0 增强版

- ✅ **P0-1**: 预测准确率统计（7/30/90 天）
- ✅ **P0-2**: 股票估值数据（PE/PB/历史分位）
- ✅ **P0-3**: 北向资金流向
- ✅ **P0-4**: 新闻情绪分析修复
- ✅ **P0-5**: 所有数据标注更新时间
- ✅ 简报增强版：`brief_generator_enhanced.py`

### V8.4.5 (2026-04-15) - 预测逻辑优化版 ⭐

**核心变更**:
- ✅ 取消震荡预测，只保留上涨/下跌
- ✅ 方向阈值从 ±1% 调整为 ±0.5%
- ✅ 预测区间从 ±2% 缩小到 ±1%
- ✅ 基金净值智能列名检测
- ✅ 北向资金实时获取（不再硬编码）

**修改文件**:
- `predictors/validator.py` - 验证逻辑
- `predictors/multi_factor.py` - 预测生成
- `predictors/base.py` - 区间计算
- `data_sources/fund_source.py` - 基金净值
- `analyzers/fear_greed_index.py` - 北向资金

**效果对比**:
```
预测方向：上涨/下跌/震荡 → 上涨/下跌（更明确）
预测区间：±2% (4.2% 跨度) → ±1% (2.0% 跨度)（更精确）
基金净值：多只 0.0 → 全部有效（更可靠）
北向资金：固定 35.8 亿 → 实时获取（更真实）
```

### V8.4.4 (2026-04-15) - 方向验证修复版

**核心修复**:
- ✅ 修复方向验证逻辑错误
- ✅ 基于实际涨跌幅判断方向
- ✅ 准确率从 0% 修正为 25%

**问题**: 验证逻辑比较"预测价格 vs 实际价格"（错误）  
**修复**: 基于"实际涨跌幅"判断方向（正确）

### V8.4.3 (2026-04-10) - 真实准确率版

**核心变更**:
- ✅ 移除预测准确率模拟数据
- ✅ 使用真实数据库记录
- ✅ 国内金价涨跌通过昨收价计算

### V8.4.2 (2026-04-08)

- ✅ 实时金价获取（东方财富浏览器）
- ✅ API 服务 V1.0.0
- ✅ Web 仪表盘 V1.0.0
- ✅ 代码清理（68→8 个脚本）

### V8.1.0 (2026-03-26)

- ✅ 预测验证
- ✅ 准确率统计

### V8.0.0 (2026-03-24)

- ✅ 完整分析版本
- ✅ 多因子预测

---

## 🔧 系统维护

### 日常巡检清单

| 频率 | 检查项 | 命令/方法 |
|------|--------|-----------|
| 每日 | API 服务状态 | `curl http://localhost:8000/api/health` |
| 每日 | 金价数据源 | 查看 `logs/gold.log` |
| 每日 | 基金数据源 | 查看 `logs/fund.log` |
| 每日 | 新闻数据源 | 查看 `logs/news.log` |
| 每周 | 数据库连接 | `sqlite3 data/predictions.db ".tables"` |
| 每周 | 磁盘空间 | `df -h` |
| 每月 | 日志清理 | `rm logs/*.log.*.gz` |

---

### 文档维护规范 ⭐

**核心原则**:
> **每一次修改，都应该记录下来。**  
> **每一次变更，相关文档都需要同步更新。**

#### 必更文档清单

| 优先级 | 文档 | 更新条件 |
|--------|------|----------|
| 🔴 **P0** | `docs/CHANGELOG.md` | **每次修改** |
| 🔴 **P0** | `docs/VERSION_HISTORY.md` | **版本发布** |
| 🔴 **P0** | `README.md` | **版本发布** |
| 🔴 **P0** | `SKILL.md` | **功能变更** |
| 🟡 **P1** | `docs/INDEX.md` | **新增文档** |
| 🟡 **P1** | `docs/FIX_*.md` | **Bug 修复** |

#### 文档更新流程

```
修改代码
   ↓
更新 CHANGELOG.md ← 必须！
   ↓
创建修复报告（如为 Bug 修复）
   ↓
更新 VERSION_HISTORY.md（如为版本发布）
   ↓
更新 README.md + SKILL.md（如为版本发布）
   ↓
更新 INDEX.md（如有新文档）
   ↓
文档一致性检查 ← 必须！
   ↓
提交/发布
```

#### 检查清单

每次修改完成后，逐项检查：

- [ ] `docs/CHANGELOG.md` - 添加更新记录
- [ ] `docs/VERSION_HISTORY.md` - 添加版本记录（如适用）
- [ ] `README.md` - 更新版本号和日志（如适用）
- [ ] `SKILL.md` - 更新版本号和功能表（如适用）
- [ ] `docs/INDEX.md` - 更新文档索引（如适用）
- [ ] 版本号一致性检查
- [ ] 更新日期一致性检查
- [ ] 内部链接有效性检查

#### 快速检查命令

```bash
# 检查版本号一致性
grep -h "version:" *.md docs/*.md | sort | uniq -c

# 检查更新日期
grep -h "最后更新\|last_updated" *.md docs/*.md | sort | uniq -c

# 检查内部链接
find docs -name "*.md" -exec grep -l "\[.*\](.*.md)" {} \;
```

#### 相关文档

- `docs/DOCUMENTATION_MAINTENANCE.md` - **完整文档维护规范** ⭐
- `docs/CHANGELOG.md` - **统一更新日志**
- `docs/VERSION_HISTORY.md` - **完整版本历史**
- `docs/INDEX.md` - **文档索引**

---

### 版本快速参考

| 版本 | 日期 | 核心变更 | 文档 |
|------|------|----------|------|
| **V8.4.5** | 2026-04-15 | 取消震荡预测 + 阈值±0.5% + 区间±1% | [CHANGELOG.md](docs/CHANGELOG.md) |
| **V8.4.4** | 2026-04-15 | 方向验证逻辑修复 | [DIRECTION_FIX](docs/DIRECTION_FIX_20260415.md) |
| **V8.4.3** | 2026-04-10 | 真实准确率 + 金价涨跌计算 | [ACCURACY_FIX](docs/ACCURACY_FIX_20260410.md) |
| **V8.4.2** | 2026-04-08 | 宏观叙事分析 + 多源新闻 | [VERSION_HISTORY](docs/VERSION_HISTORY.md) |
| **V8.4.1** | 2026-04-08 | 路径优化 + 预测自动保存 | [VERSION_HISTORY](docs/VERSION_HISTORY.md) |
| **V8.4.0** | 2026-04-07 | P1 增强（恐慌贪婪 + 事件日历） | [VERSION_HISTORY](docs/VERSION_HISTORY.md) |

---

*文档位置：README.md*  
*最后更新：2026-04-15*  
*版本：V8.4.5 + API V1.0.0*
