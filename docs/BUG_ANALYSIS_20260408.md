# Bug 分析报告 - 2026-04-08

## 问题 1: 金价是否正确？

### 当前简报显示
- **国际金价**: $4842.8/oz
- **国内金价**: ¥1128.82/g
- **数据来源**: 东方财富-COMEX 黄金期货
- **置信度**: 中

### 验证结果
运行 `scripts/gold_price_auto_v83.py` 获取实时金价：
- **国际金价**: $4840.50/oz (差异：$2.3, 0.05%)
- **国内金价**: ¥1128.29/g (差异：¥0.53, 0.05%)

### 结论
✅ **金价数据基本正确**，差异在合理范围内（<0.1%）

**差异原因**:
1. 简报生成时间 (10:01) 与当前验证时间 (10:42) 相差 41 分钟
2. 金价在此期间有正常波动
3. 数据源 COMEX 期货价格本身也有买卖价差

### 建议
- 当前多数据源验证机制工作正常
- 置信度"中"是合理的（只有 1 个数据源成功）
- 无需修复

---

## 问题 2: 预测准确率历史为什么为空？

### 数据库状态检查
```
总预测数：8
已验证 (is_accurate 有值): 0
未验证 (is_accurate=NULL): 8

最近的预测日期：2026-03-19
昨天 (2026-04-07) 预测数：0
今天 (2026-04-08) 预测数：0
```

### 根本原因分析

#### 原因 1: 预测记录未保存
- `main.py` 中的 `run_daily_brief()` 方法**没有调用**预测保存功能
- `PredictionValidator` 类存在但**未被使用**
- 预测数据只生成简报，未持久化到数据库

#### 原因 2: 预测验证流程缺失
- 预测记录表中的 `is_accurate` 字段全部为 NULL
- 没有自动验证机制在次日更新预测准确性
- 历史预测 (2026-03-19) 至今未验证

#### 原因 3: 数据表结构不一致
`analyzers/accuracy_tracker.py` 期望的表结构：
```sql
- predicted_direction (TEXT)
- actual_direction (TEXT)
- is_correct (BOOLEAN)
```

`predictors/validator.py` 创建的表结构：
```sql
- direction (TEXT)
- actual_price (REAL)
- direction_correct (INTEGER)
```

**两个模块使用不同的字段名！**

#### 原因 4: 简报生成器查询条件过严
`brief_generator_enhanced.py` 第 107 行：
```python
WHERE prediction_date >= ? AND is_accurate IS NOT NULL
```
- 要求 `is_accurate` 字段有值
- 但实际数据库中该字段**永远为 NULL**

### 影响
- 简报显示准确率全为 0%
- 无法追踪预测质量
- 无法优化因子权重

---

## 修复方案

### 方案 A: 快速修复（推荐）

**目标**: 让准确率统计显示数据

1. **修改查询条件** - 放宽到所有预测记录
   ```python
   # brief_generator_enhanced.py
   WHERE prediction_date >= ?  # 移除 is_accurate IS NOT NULL
   ```

2. **使用 direction_correct 字段** - 适配实际表结构
   ```python
   SELECT COUNT(*), SUM(CASE WHEN direction_correct = 1 THEN 1 ELSE 0 END)
   ```

3. **集成 PredictionValidator** - 在 main.py 中保存预测
   ```python
   from predictors.validator import PredictionValidator
   validator = PredictionValidator()
   validator.save_prediction(prediction_data)
   ```

### 方案 B: 完整重构

**目标**: 建立完整的预测 - 验证 - 统计闭环

1. 统一数据库表结构
2. 在 `main.py` 中集成预测保存
3. 创建 cron 任务每日验证昨日预测
4. 更新 `accuracy_tracker.py` 使用正确的表

---

## 建议优先级

| 任务 | 优先级 | 工作量 | 价值 |
|------|--------|--------|------|
| 修复准确率查询逻辑 | P1 | 30 分钟 | 高 |
| 集成预测保存 | P1 | 1 小时 | 高 |
| 创建验证 cron 任务 | P2 | 2 小时 | 中 |
| 统一表结构 | P3 | 4 小时 | 中 |

---

## 下一步行动

1. ✅ 确认金价数据正常 - 无需修复
2. 🔧 修复预测准确率统计查询
3. 🔧 在 main.py 中添加预测保存
4. 📅 创建每日验证 cron 任务
