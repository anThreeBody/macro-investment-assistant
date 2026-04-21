# 使用指南 - Macro Investment Assistant V8.2

**最后更新**: 2026-04-03  
**版本**: V8.2.0

---

## 🎯 推荐使用方式

### 方式 1: 一键运行（最简单）⭐

```bash
./run_daily.sh
```

**输出**:
- 获取实时金价
- 生成每日简报
- 显示文件路径

**适合**: 日常使用，一键完成所有操作

---

### 方式 2: 分步运行（灵活）

```bash
# 1. 获取金价
python3 scripts/gold_price_auto_v82.py

# 2. 生成简报
python3 scripts/daily_brief.py
```

**适合**: 只需要获取金价或生成简报

---

### 方式 3: 模块化系统（高级）

```bash
python3 main.py brief
```

**适合**: 开发者，需要自定义功能

---

## 📁 目录结构

```
skills/Macro-Investment-Assistant/
├── run_daily.sh              # 一键运行脚本 ⭐
├── main.py                   # 模块化入口
├── scripts/                  # 工具脚本
│   ├── gold_price_auto_v82.py # 金价获取 V8.2
│   └── daily_brief.py         # 简报生成 V8.2
├── data_sources/             # 数据源模块
├── analyzers/                # 分析模块
├── predictors/               # 预测模块
├── presenters/               # 展示模块
├── daily_brief/              # 生成的简报
└── docs/                     # 文档
```

---

## 🛠️ 核心脚本说明

### scripts/gold_price_auto_v82.py

**功能**: 获取实时金价  
**数据源**: 东方财富 COMEX 黄金期货  
**输出**: 国际金价（美元/盎司）+ 国内金价（元/克）

**使用**:
```bash
python3 scripts/gold_price_auto_v82.py
```

**输出示例**:
```
✅ 获取成功!
国际金价：$4989.50/oz
国内金价：¥1163.02/g
数据来源：东方财富-COMEX 黄金期货
```

---

### scripts/daily_brief.py

**功能**: 生成每日投资简报  
**版本**: V8.2.0  
**内容**: 金价、宏观数据、新闻、预测

**使用**:
```bash
python3 scripts/daily_brief.py
```

**输出**:
- Markdown 简报：`daily_brief/brief_v8_YYYYMMDD.md`
- JSON 数据：`data/brief_v8_YYYYMMDD.json`

---

## ⚠️ 依赖要求

### 必须安装

```bash
pip install playwright
playwright install chromium
```

### 检查安装

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('✅ OK')"
```

---

## 📊 输出文件

### 每日简报

**位置**: `daily_brief/brief_v8_YYYYMMDD.md`

**内容**:
```markdown
# 📊 投资每日简报

**版本**: V8.2.0
**数据源**: 东方财富（实时金价）

## 💰 黄金价格
| 类型 | 价格 | 涨跌额 | 涨跌幅 |
|------|------|--------|--------|
| 国际金价 | $4989.5 | ... | ... |
| 国内金价 | ¥1163.02 | ... | ... |

## 🔮 明日预测
...
```

### 金价数据

**位置**: `data/gold_price_cache.json`

**内容**:
```json
{
  "international_usd_per_oz": 4989.50,
  "domestic_cny_per_gram": 1163.02,
  "source": "东方财富-COMEX 黄金期货",
  "update_time": "2026-04-03 13:51:25"
}
```

---

## 🔧 故障排查

### 问题 1: playwright 未安装

**错误**:
```
ModuleNotFoundError: No module named 'playwright'
```

**解决**:
```bash
pip install playwright
playwright install chromium
```

### 问题 2: 金价获取失败

**错误**:
```
❌ 获取失败：无法获取金价数据
```

**解决**:
1. 检查网络连接
2. 手动访问：http://quote.eastmoney.com/unify/r/101.GC00Y
3. 如仍无法访问，稍后重试

### 问题 3: 简报生成失败

**错误**:
```
FileNotFoundError: [Errno 2] No such file or directory
```

**解决**:
```bash
# 确保在工作目录
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant
./run_daily.sh
```

---

## 📝 历史版本归档

所有历史脚本已归档到 `archive/scripts/` 目录：

```
archive/scripts/
├── daily_brief_v5.py
├── daily_brief_v8.py
├── gold_price_auto.py
└── ... (60+ 个历史脚本)
```

**注意**: 归档脚本不再维护，建议使用 V8.2 版本。

---

## 🎯 最佳实践

### 日常使用

```bash
# 每天早上运行
./run_daily.sh

# 查看简报
cat daily_brief/brief_v8_$(date +%Y%m%d).md
```

### 定时任务

```bash
# 添加到 crontab（每天 8:00 运行）
0 8 * * * cd /path/to/Macro-Investment-Assistant && ./run_daily.sh
```

### 数据备份

```bash
# 备份简报
cp -r daily_brief/ ~/backup/briefs/

# 备份数据
cp -r data/ ~/backup/data/
```

---

## 📞 获取帮助

### 查看文档

```bash
# 部署说明
cat scripts/DEPLOYMENT_V8.2.md

# 金价获取说明
cat docs/GOLD_BROWSER_SOURCE.md

# 完整使用指南
cat docs/USER_GUIDE.md
```

### 检查版本

```bash
# 查看简报版本
head -5 daily_brief/brief_v8_*.md | grep "版本"

# 应显示：版本：V8.2.0
```

---

## 🚀 升级计划

### V8.2 当前功能

- ✅ 实时金价获取（东方财富）
- ✅ 每日简报生成（V8.2.0）
- ✅ 预测验证
- ✅ 数据缓存

### 未来规划

- [ ] 多数据源备份
- [ ] 自动权重优化
- [ ] 回测框架
- [ ] 实时推送通知

---

*文档位置：scripts/USAGE_GUIDE.md*  
*最后更新：2026-04-03*
