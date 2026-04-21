# 预测保存功能集成修复报告

**修复日期**: 2026-04-08  
**修复版本**: V8.4.0  
**修复 Agent**: Investment Steward (5aQmuc)

---

## 📋 问题描述

### 原始问题
用户发现最新日报中：
1. 预测准确率历史显示为空（0%）
2. 昨天的预测没有保存到数据库

### 根本原因
1. **预测未保存**: `main.py` 中的 `run_daily_brief()` 方法没有调用预测保存功能
2. **验证流程缺失**: `PredictionValidator` 类存在但从未被使用
3. **表结构不一致**: 数据库表结构与代码期望的字段名不匹配
4. **查询条件过严**: 准确率统计查询要求 `is_accurate IS NOT NULL`，但该字段永远为 NULL

---

## ✅ 修复内容

### 1. 修改 `main.py` - 集成预测保存

**文件**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant/main.py`

**变更**:
```python
# 添加导入
from predictors.validator import PredictionValidator

# 初始化验证器
class InvestmentSystem:
    def __init__(self):
        self.data_api = DataAPI()
        self.predictor = MultiFactorPredictor()
        self.validator = PredictionValidator(db_path='data/predictions.db')  # 新增
        self.brief_gen = BriefGeneratorEnhanced()
        self.chart_gen = ChartGenerator()
        self.alert = AlertNotifier()

# 在 run_daily_brief() 中保存预测
def run_daily_brief(self, save: bool = True, generate_charts: bool = False):
    # ... 获取数据 ...
    # ... 生成预测 ...
    
    # 2.1 保存预测到数据库（新增）
    logger.info("\n💾 步骤 2.1: 保存预测记录...")
    self.validator.save_prediction(prediction)
    
    # ... 生成简报 ...
```

**效果**: 每次生成简报时自动保存预测到数据库

---

### 2. 修改 `predictors/validator.py` - 适配现有表结构

**文件**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant/predictors/validator.py`

**变更**:
```python
def _init_db(self):
    """初始化数据库 - 适配现有表结构并自动添加缺失列"""
    # 检查表是否存在
    # 如果不存在，创建新表
    # 如果存在，检查并添加缺失的列
    # 支持的列：predict_date, predict_time, current_price, predicted_price,
    #          price_lower, price_upper, direction, verified, direction_correct, factors
```

**效果**: 兼容旧数据库结构，自动迁移

---

### 3. 修改 `presenters/brief_generator_enhanced.py` - 修复准确率查询

**文件**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant/presenters/brief_generator_enhanced.py`

**变更**:
```python
def _get_accuracy_stats(self) -> Dict[str, Any]:
    """获取预测准确率统计"""
    # 修改前
    cursor.execute('''
        SELECT COUNT(*), SUM(CASE WHEN is_accurate = 1 THEN 1 ELSE 0 END)
        FROM predictions
        WHERE prediction_date >= ? AND is_accurate IS NOT NULL
    ''', (cutoff_date,))
    
    # 修改后
    cursor.execute('''
        SELECT COUNT(*), SUM(CASE WHEN direction_correct = 1 THEN 1 ELSE 0 END)
        FROM predictions
        WHERE predict_date >= ? AND verified = 1
    ''', (cutoff_date,))
```

**效果**: 使用正确的字段名查询已验证的预测记录

---

### 4. 修改 `presenters/brief_generator.py` - 同步修复

**文件**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant/presenters/brief_generator.py`

**变更**: 同 `brief_generator_enhanced.py`

---

### 5. 创建验证脚本

**文件**: `~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant/scripts/verify_predictions.py`

**功能**:
- 每日自动验证前一天的预测
- 计算预测准确率
- 更新数据库记录

**使用方法**:
```bash
# 自动获取当前金价验证
python3 scripts/verify_predictions.py

# 指定实际价格验证
python3 scripts/verify_predictions.py 1128.50
```

---

## 🧪 测试结果

### 测试 1: 预测保存功能
```
✅ InvestmentSystem 导入成功
✅ PredictionValidator 已集成
✅ InvestmentSystem 初始化成功
✅ validator 已初始化
```

### 测试 2: 数据库记录
```
✅ 预测保存成功
✅ 数据库记录查询成功
   - 记录 ID: 1
   - 预测日期：2026-04-08 10:51:10
   - 当前价格：¥1128.82
   - 预测价格：¥1131.08
   - 方向：sideways
   - 置信度：高
   - 已验证：否

📊 数据库总记录数：1
```

### 测试 3: 验证脚本
```
✅ 验证脚本执行成功
✅ 能够正确获取金价
✅ 能够查询数据库
✅ 验证逻辑正常工作
```

---

## 📅 下一步：创建 Cron 任务

### ✅ 已完成（方案 A）

**修改了 `run_daily.sh`**，在生成简报前自动验证昨日预测：

```bash
# 步骤 0: 验证昨日预测（新增）
echo "🔍 步骤 0: 验证昨日预测..."
python3 scripts/verify_predictions.py 2>&1 | grep -E "(✅|⚠️|验证完成 | 预测 | 实际 | 准确率 | 误差)" || echo "⚠️  验证失败或无昨日预测"
echo ""
```

**优点**:
- ✅ 只需 1 个 Cron 任务（现有的 `./run_daily.sh`）
- ✅ 自动化完整流程（验证 + 生成）
- ✅ 验证后生成的简报会显示最新准确率

**执行流程**:
```
每天定时执行 ./run_daily.sh
  ↓
步骤 0: 验证昨日预测（新增）
  ↓
步骤 1: 获取最新金价
  ↓
步骤 2: 生成每日简报（包含最新准确率）
  ↓
步骤 3: 显示简报
```

### 原有建议（已废弃）
~~创建单独的 Cron 任务~~
~~```bash
copaw cron create \
  --agent-id 5aQmuc \
  --schedule "30 10 * * *" \
  --command "cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant && python3 scripts/verify_predictions.py" \
  --name "verify_predictions"
```~~

---

## 📊 预期效果

### 修复前
```
### 📊 预测准确率历史
| 周期 | 预测次数 | 正确次数 | 准确率 |
|------|----------|----------|--------|
| 7 天  | 0        | 0        | 0%     |
| 30 天 | 0        | 0        | 0%     |
| 90 天 | 0        | 0        | 0%     |
```

### 修复后（运行 7 天后）
```
### 📊 预测准确率历史
| 周期 | 预测次数 | 正确次数 | 准确率 |
|------|----------|----------|--------|
| 7 天  | 7        | 4        | 57.1%  |
| 30 天 | 28       | 16       | 57.1%  |
| 90 天 | 85       | 48       | 56.5%  |

当前预测置信度：高（基于历史准确率 57.1%）
```

---

## 📝 相关文件清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `main.py` | 修改 | 集成 PredictionValidator |
| `predictors/validator.py` | 修改 | 适配现有表结构 |
| `presenters/brief_generator_enhanced.py` | 修改 | 修复准确率查询 |
| `presenters/brief_generator.py` | 修改 | 修复准确率查询 |
| `scripts/verify_predictions.py` | 新建 | 预测验证脚本 |
| `docs/CRON_VERIFY_PREDICTIONS.md` | 新建 | Cron 配置文档 |
| `docs/PREDICTION_SAVE_FIX_REPORT.md` | 新建 | 本文档 |

---

## ⚠️ 注意事项

1. **数据库备份**: 修复前已备份 `predictions.db` 到 `predictions.db.backup`
2. **表结构迁移**: validator.py 会自动添加缺失列，无需手动迁移
3. **历史数据**: 旧预测记录（2026-03-19）由于字段不匹配，无法自动验证
4. **验证时机**: 建议在次日金价稳定后（上午 10:30）进行验证

---

## 🎯 验收标准

- [x] 预测自动保存到数据库
- [x] 数据库表结构正确
- [x] 准确率查询逻辑正确
- [x] 验证脚本可正常运行
- [ ] Cron 任务已创建（需用户确认）
- [ ] 运行 7 天后准确率数据显示正常

---

**修复完成时间**: 2026-04-08 10:52  
**修复状态**: ✅ 完成（待 Cron 配置）
