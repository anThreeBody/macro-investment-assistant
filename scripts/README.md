# scripts/ 目录说明

**最后更新**: 2026-04-03  
**版本**: V8.2.0

---

## 📁 目录内容

当前 `scripts/` 目录包含 **8 个核心文件**，所有历史版本已归档到 `archive/scripts/`。

### 核心脚本（推荐使用）

| 文件 | 大小 | 用途 | 推荐使用 |
|------|------|------|----------|
| `gold_price_auto_v82.py` | 8.0K | 金价实时获取 V8.2 | ⭐ 是 |
| `daily_brief.py` | 16K | 每日简报生成 V8.2 | ⭐ 是 |
| `daily_brief_v8.py` | 54K | 简报基类（依赖） | ✅ 依赖 |

### 支持模块（内部使用）

| 文件 | 大小 | 用途 |
|------|------|------|
| `data_manager.py` | 17K | 数据管理 |
| `fund_recommender.py` | 11K | 基金推荐 |
| `gold_analyzer_v2.py` | 9.0K | 金价分析 |
| `policy_analyzer.py` | 11K | 政策分析 |
| `sentiment_analyzer.py` | 14K | 情绪分析 |

---

## 🚀 使用方式

### 方式 1: 一键运行（最简单）⭐

```bash
./run_daily.sh
```

**执行流程**:
1. 获取实时金价（`gold_price_auto_v82.py`）
2. 生成每日简报（`main.py brief`）
3. 显示简报路径

**输出**:
```
📈 步骤 1: 获取最新金价...
✅ 获取成功!

📰 步骤 2: 生成每日简报...
[简报生成成功]

📄 最新简报:
   daily_brief/brief_v8_20260403.md
```

---

### 方式 2: 单独使用

#### 获取金价

```bash
python3 scripts/gold_price_auto_v82.py
```

**输出**:
```
✅ 获取成功!
国际金价：$4989.50/oz
国内金价：¥1163.02/g
数据来源：东方财富-COMEX 黄金期货
```

#### 生成简报

```bash
python3 scripts/daily_brief.py
```

**输出**:
```
📊 每日简报 V8.2 生成成功
简报已保存：daily_brief/brief_v8_20260403.md
```

---

### 方式 3: 模块化系统（完整功能）

```bash
python3 main.py brief
```

**适合**: 需要完整分析功能

---

## 📦 归档文件

所有历史脚本已归档到 `archive/scripts/` 目录：

```
archive/scripts/
├── daily_brief_v2.py - v8.py (10 个版本)
├── gold_*.py (12 个金价相关脚本)
├── prediction_*.py (5 个预测脚本)
├── fund_*.py (3 个基金脚本)
├── ... (60+ 个历史脚本)
```

**注意**: 归档脚本不再维护，仅供历史参考。

---

## ⚠️ 不要删除的文件

以下文件是 `daily_brief.py` 的依赖，删除会导致运行失败：

```
scripts/daily_brief_v8.py      # 简报基类
scripts/data_manager.py        # 数据管理
scripts/fund_recommender.py    # 基金推荐
scripts/gold_analyzer_v2.py    # 金价分析
scripts/policy_analyzer.py     # 政策分析
scripts/sentiment_analyzer.py  # 情绪分析
```

---

## 📝 版本历史

### V8.2.0 (2026-04-03)

- ✅ 使用浏览器实时获取金价（东方财富）
- ✅ 清理 60+ 历史脚本
- ✅ 统一入口：`./run_daily.sh`
- ✅ 完善文档

### V8.1.0 (2026-03-26)

- ✅ 添加预测验证
- ✅ 准确率统计

### V8.0.0 (2026-03-24)

- ✅ 完整分析版本
- ✅ 多因子预测

---

## 🔧 故障排查

### 问题 1: 找不到模块

**错误**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决**:
```bash
# 检查文件是否被误删
ls scripts/*.py

# 如缺失，从 archive/scripts/ 恢复
cp archive/scripts/xxx.py scripts/
```

### 问题 2: 金价获取失败

**错误**:
```
❌ 获取失败：无法获取金价数据
```

**解决**:
1. 检查 playwright：`pip install playwright && playwright install chromium`
2. 检查网络：访问 http://quote.eastmoney.com/unify/r/101.GC00Y
3. 稍后重试

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

## 📚 相关文档

| 文档 | 位置 |
|------|------|
| 使用指南 | `scripts/USAGE_GUIDE.md` |
| 部署说明 | `scripts/DEPLOYMENT_V8.2.md` |
| 清理报告 | `scripts/CLEANUP_COMPLETE.md` |
| 金价获取 | `docs/GOLD_BROWSER_SOURCE.md` |

---

## ✅ 验收清单

- [x] scripts/ 只保留 8 个核心文件
- [x] 60+ 历史脚本已归档
- [x] `./run_daily.sh` 运行正常
- [x] 金价获取正常
- [x] 简报生成正常
- [x] 文档完善

---

*文档位置：scripts/README.md*  
*最后更新：2026-04-03*
