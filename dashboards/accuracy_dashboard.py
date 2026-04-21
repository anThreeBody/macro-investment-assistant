#!/usr/bin/env python3
"""
预测准确率看板
展示各品类预测准确率趋势
"""

import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AccuracyMetrics:
    """准确率指标"""
    category: str           # 品类
    period: str             # 周期
    accuracy: float         # 准确率
    total_predictions: int  # 总预测数
    correct_predictions: int # 正确预测数
    avg_error: float        # 平均误差
    trend: str              # 趋势 (上升/下降/持平)


class AccuracyDashboard:
    """预测准确率看板"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = str(Path(__file__).parent.parent / "data")
        
        self.data_dir = Path(data_dir)
        self.dashboard_dir = Path(__file__).parent.parent / "dashboards"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.predictions_db = self.data_dir / "predictions.db"
        
        logger.info("[准确率看板] 初始化完成")
    
    def get_accuracy_by_category(self, category: str, days: int = 30) -> Dict:
        """按品类获取准确率"""
        metrics = {
            "category": category,
            "period": f"近{days}天",
            "accuracy": 0.0,
            "total_predictions": 0,
            "correct_predictions": 0,
            "avg_error": 0.0,
            "trend": "持平"
        }
        
        try:
            if not self.predictions_db.exists():
                return metrics
            
            conn = sqlite3.connect(str(self.predictions_db))
            cursor = conn.cursor()
            
            # 获取时间范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 根据品类查询不同的表
            if category == "gold":
                cursor.execute("""
                    SELECT today_trend, actual_result, accuracy_score
                    FROM gold_predictions
                    WHERE date >= ? AND date <= ?
                    AND actual_result IS NOT NULL
                """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            elif category == "fund":
                cursor.execute("""
                    SELECT recommendation_reason, actual_return, accuracy_score
                    FROM fund_recommendations
                    WHERE date >= ? AND date <= ?
                    AND actual_return IS NOT NULL
                """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            else:
                # 通用查询
                cursor.execute("""
                    SELECT prediction_type, actual_result, accuracy_score
                    FROM predictions
                    WHERE asset_type = ? AND prediction_date >= ? AND prediction_date <= ?
                    AND actual_result IS NOT NULL
                """, (category, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            records = cursor.fetchall()
            
            if records:
                total = len(records)
                # 计算准确率: accuracy_score >= 60 视为正确
                correct = sum(1 for r in records if r[2] is not None and r[2] >= 60)
                errors = [r[2] for r in records if r[2] is not None]
                
                metrics["total_predictions"] = total
                metrics["correct_predictions"] = correct
                metrics["accuracy"] = correct / total if total > 0 else 0.0
                metrics["avg_error"] = (100 - sum(errors) / len(errors)) if errors else 0.0
                
                # 计算趋势 (对比上一个周期)
                prev_start = start_date - timedelta(days=days)
                if category == "gold":
                    cursor.execute("""
                        SELECT actual_result, accuracy_score
                        FROM gold_predictions
                        WHERE date >= ? AND date < ?
                        AND actual_result IS NOT NULL
                    """, (prev_start.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d')))
                elif category == "fund":
                    cursor.execute("""
                        SELECT actual_return, accuracy_score
                        FROM fund_recommendations
                        WHERE date >= ? AND date < ?
                        AND actual_return IS NOT NULL
                    """, (prev_start.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d')))
                else:
                    cursor.execute("""
                        SELECT actual_result, accuracy_score
                        FROM predictions
                        WHERE asset_type = ? AND prediction_date >= ? AND prediction_date < ?
                        AND actual_result IS NOT NULL
                    """, (category, prev_start.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d')))
                
                prev_records = cursor.fetchall()
                if prev_records:
                    prev_correct = sum(1 for r in prev_records if r[1] is not None and r[1] >= 60)
                    prev_accuracy = prev_correct / len(prev_records) if prev_records else 0
                    
                    if metrics["accuracy"] > prev_accuracy + 0.05:
                        metrics["trend"] = "上升"
                    elif metrics["accuracy"] < prev_accuracy - 0.05:
                        metrics["trend"] = "下降"
                    else:
                        metrics["trend"] = "持平"
            
            conn.close()
        except Exception as e:
            logger.warning(f"[准确率看板] {category} 准确率统计失败: {e}")
        
        return metrics
    
    def get_all_categories_accuracy(self, days: int = 30) -> List[Dict]:
        """获取所有品类准确率"""
        categories = ["gold", "fund", "stock", "macro"]
        results = []
        
        for category in categories:
            metrics = self.get_accuracy_by_category(category, days)
            results.append(metrics)
        
        return results
    
    def get_accuracy_trend(self, category: str, periods: int = 6) -> List[Dict]:
        """获取准确率趋势"""
        trends = []
        
        try:
            for i in range(periods):
                end_date = datetime.now() - timedelta(days=i*30)
                start_date = end_date - timedelta(days=30)
                
                metrics = self.get_accuracy_by_category(category, days=30)
                metrics["period"] = f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"
                trends.append(metrics)
            
            trends.reverse()  # 按时间顺序
        except Exception as e:
            logger.warning(f"[准确率看板] 趋势统计失败: {e}")
        
        return trends
    
    def calculate_overall_accuracy(self, days: int = 30) -> Dict:
        """计算总体准确率"""
        all_metrics = self.get_all_categories_accuracy(days)
        
        total_predictions = sum(m["total_predictions"] for m in all_metrics)
        total_correct = sum(m["correct_predictions"] for m in all_metrics)
        avg_error = sum(m["avg_error"] for m in all_metrics) / len(all_metrics) if all_metrics else 0.0
        
        # 加权平均准确率
        if total_predictions > 0:
            overall_accuracy = total_correct / total_predictions
        else:
            overall_accuracy = 0.0
        
        return {
            "period": f"近{days}天",
            "overall_accuracy": overall_accuracy,
            "total_predictions": total_predictions,
            "total_correct": total_correct,
            "avg_error": avg_error,
            "categories": len(all_metrics)
        }
    
    def get_confidence_distribution(self, category: str) -> Dict:
        """获取置信度分布"""
        distribution = {
            "high": 0,      # >= 0.7
            "medium": 0,    # 0.5 - 0.7
            "low": 0        # < 0.5
        }
        
        try:
            if not self.predictions_db.exists():
                return distribution
            
            conn = sqlite3.connect(str(self.predictions_db))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT confidence FROM predictions
                WHERE category = ? AND confidence IS NOT NULL
            """, (category,))
            
            confidences = [r[0] for r in cursor.fetchall()]
            
            for conf in confidences:
                if conf >= 0.7:
                    distribution["high"] += 1
                elif conf >= 0.5:
                    distribution["medium"] += 1
                else:
                    distribution["low"] += 1
            
            conn.close()
        except Exception as e:
            logger.warning(f"[准确率看板] 置信度分布统计失败: {e}")
        
        return distribution
    
    def generate_dashboard(self) -> str:
        """生成准确率看板"""
        # 7天、30天、90天准确率
        accuracy_7d = self.get_all_categories_accuracy(days=7)
        accuracy_30d = self.get_all_categories_accuracy(days=30)
        accuracy_90d = self.get_all_categories_accuracy(days=90)
        
        overall_30d = self.calculate_overall_accuracy(days=30)
        
        dashboard = f"""# 📊 预测准确率看板

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 总体准确率

| 指标 | 数值 |
|------|------|
| **总体准确率** | **{overall_30d['overall_accuracy']:.1%}** |
| 总预测次数 | {overall_30d['total_predictions']:,} |
| 正确次数 | {overall_30d['total_correct']:,} |
| 平均误差 | {overall_30d['avg_error']:.2f}% |
| 覆盖品类 | {overall_30d['categories']} 个 |

---

## 📊 各品类准确率

### 近7天

| 品类 | 准确率 | 预测数 | 正确数 | 趋势 |
|------|--------|--------|--------|------|
"""
        
        for metric in accuracy_7d:
            dashboard += f"| {metric['category']} | {metric['accuracy']:.1%} | {metric['total_predictions']} | {metric['correct_predictions']} | {metric['trend']} |\n"
        
        dashboard += f"""
### 近30天

| 品类 | 准确率 | 预测数 | 正确数 | 趋势 |
|------|--------|--------|--------|------|
"""
        
        for metric in accuracy_30d:
            dashboard += f"| {metric['category']} | {metric['accuracy']:.1%} | {metric['total_predictions']} | {metric['correct_predictions']} | {metric['trend']} |\n"
        
        dashboard += f"""
### 近90天

| 品类 | 准确率 | 预测数 | 正确数 | 趋势 |
|------|--------|--------|--------|------|
"""
        
        for metric in accuracy_90d:
            dashboard += f"| {metric['category']} | {metric['accuracy']:.1%} | {metric['total_predictions']} | {metric['correct_predictions']} | {metric['trend']} |\n"
        
        dashboard += f"""
---

## 📈 准确率趋势

"""
        
        # 添加各品类趋势
        for category in ["gold", "fund", "stock"]:
            trends = self.get_accuracy_trend(category, periods=6)
            if trends:
                dashboard += f"""
### {category.upper()} 趋势 (6个月)

| 周期 | 准确率 | 预测数 |
|------|--------|--------|
"""
                for trend in trends:
                    dashboard += f"| {trend['period']} | {trend['accuracy']:.1%} | {trend['total_predictions']} |\n"
                
                dashboard += "\n"
        
        dashboard += f"""
---

## 🎯 置信度分布

"""
        
        for category in ["gold", "fund", "stock"]:
            dist = self.get_confidence_distribution(category)
            total = sum(dist.values())
            if total > 0:
                dashboard += f"""
### {category.upper()}

| 置信度级别 | 数量 | 占比 |
|------------|------|------|
| 高 (>=70%) | {dist['high']} | {dist['high']/total:.1%} |
| 中 (50-70%) | {dist['medium']} | {dist['medium']/total:.1%} |
| 低 (<50%) | {dist['low']} | {dist['low']/total:.1%} |

"""
        
        dashboard += f"""
---

## 💡 准确率说明

### 计算方法
- **准确率** = 正确预测数 / 总预测数
- **正确预测** = 预测方向与实际方向一致
- **误差** = |预测价格 - 实际价格| / 实际价格

### 目标标准
- 短期预测 (1-3天): 目标准确率 > 60%
- 中期预测 (1-2周): 目标准确率 > 55%
- 长期预测 (1月+): 提供趋势方向，不承诺具体点位

### 优化方向
1. **高置信度优先**: 优先使用置信度 >= 70% 的预测
2. **多因子交叉**: 技术+情绪+宏观+动量四维验证
3. **持续学习**: 根据验证结果自动调整因子权重

## ⚠️ 风险提示

- 历史准确率不代表未来表现
- 市场存在不可预测的黑天鹅事件
- 建议结合其他分析方法综合判断

---

*看板生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return dashboard
    
    def save_dashboard(self):
        """保存看板到文件"""
        dashboard = self.generate_dashboard()
        
        dashboard_file = self.dashboard_dir / f"accuracy_{datetime.now().strftime('%Y%m%d')}.md"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        logger.info(f"[准确率看板] 已保存: {dashboard_file}")
        return dashboard_file
    
    def display_dashboard(self):
        """显示看板"""
        dashboard = self.generate_dashboard()
        print(dashboard)


def demo_accuracy_dashboard():
    """演示预测准确率看板"""
    print("="*70)
    print("📊 预测准确率看板演示")
    print("="*70)
    
    dashboard = AccuracyDashboard()
    
    print("\n📈 总体准确率:")
    overall = dashboard.calculate_overall_accuracy(days=30)
    print(f"  总体准确率: {overall['overall_accuracy']:.1%}")
    print(f"  总预测次数: {overall['total_predictions']}")
    print(f"  正确次数: {overall['total_correct']}")
    print(f"  平均误差: {overall['avg_error']:.2f}%")
    
    print("\n📊 各品类准确率 (近30天):")
    for metric in dashboard.get_all_categories_accuracy(days=30):
        print(f"  {metric['category']}: {metric['accuracy']:.1%} ({metric['correct_predictions']}/{metric['total_predictions']}) - {metric['trend']}")
    
    print(f"\n{'='*70}")
    print("📄 生成完整看板")
    print(f"{'='*70}")
    
    dashboard.display_dashboard()
    
    # 保存看板
    dashboard_file = dashboard.save_dashboard()
    print(f"\n✅ 看板已保存: {dashboard_file}")
    
    print("\n" + "="*70)
    print("✅ 预测准确率看板演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_accuracy_dashboard()
