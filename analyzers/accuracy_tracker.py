#!/usr/bin/env python3
"""
预测准确率统计模块
追踪7天/30天/90天准确率
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
class PredictionRecord:
    """预测记录"""
    id: int
    timestamp: str
    asset_type: str
    predicted_direction: str  # UP/DOWN/FLAT
    predicted_price: float
    actual_direction: Optional[str]
    actual_price: Optional[float]
    confidence: str
    confidence_score: float
    is_correct: Optional[bool]
    error_rate: Optional[float]


class AccuracyTracker:
    """准确率追踪器"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "data" / "predictions.db")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_tables()
        
        logger.info(f"[准确率追踪] 初始化完成: {db_path}")
    
    def _init_tables(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 预测记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                predicted_direction TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                actual_direction TEXT,
                actual_price REAL,
                confidence TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                is_correct INTEGER,
                error_rate REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 准确率统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accuracy_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                period_days INTEGER NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0,
                avg_error_rate REAL DEFAULT 0,
                high_conf_accuracy REAL DEFAULT 0,
                medium_conf_accuracy REAL DEFAULT 0,
                low_conf_accuracy REAL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, asset_type, period_days)
            )
        ''')
        
        self.conn.commit()
    
    def record_prediction(self, asset_type: str, predicted_direction: str,
                         predicted_price: float, confidence: str,
                         confidence_score: float) -> int:
        """记录预测"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (timestamp, asset_type, predicted_direction, predicted_price, 
             confidence, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), asset_type, predicted_direction,
              predicted_price, confidence, confidence_score))
        
        self.conn.commit()
        prediction_id = cursor.lastrowid
        
        logger.info(f"[准确率追踪] 记录预测 #{prediction_id}: {asset_type} {predicted_direction}")
        return prediction_id
    
    def update_actual_result(self, prediction_id: int, actual_price: float):
        """更新实际结果"""
        cursor = self.conn.cursor()
        
        # 获取预测记录
        cursor.execute('''
            SELECT predicted_direction, predicted_price, confidence_score
            FROM predictions WHERE id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        if not row:
            logger.warning(f"[准确率追踪] 预测记录不存在: #{prediction_id}")
            return
        
        predicted_direction, predicted_price, confidence_score = row
        
        # 计算实际方向
        price_change = actual_price - predicted_price
        if price_change > predicted_price * 0.002:  # 涨0.2%以上
            actual_direction = "UP"
        elif price_change < -predicted_price * 0.002:  # 跌0.2%以上
            actual_direction = "DOWN"
        else:
            actual_direction = "FLAT"
        
        # 判断是否准确
        is_correct = (predicted_direction == actual_direction)
        
        # 计算误差率
        error_rate = abs(actual_price - predicted_price) / predicted_price
        
        # 更新记录
        cursor.execute('''
            UPDATE predictions 
            SET actual_direction = ?, actual_price = ?, 
                is_correct = ?, error_rate = ?
            WHERE id = ?
        ''', (actual_direction, actual_price, int(is_correct), error_rate, prediction_id))
        
        self.conn.commit()
        
        logger.info(f"[准确率追踪] 更新结果 #{prediction_id}: 预测{predicted_direction}, 实际{actual_direction}, 准确: {is_correct}")
    
    def calculate_accuracy(self, days: int, asset_type: str = "gold") -> Dict:
        """计算准确率"""
        cursor = self.conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 总体准确率
        cursor.execute('''
            SELECT COUNT(*), SUM(is_correct)
            FROM predictions
            WHERE timestamp > ? AND asset_type = ? AND is_correct IS NOT NULL
        ''', (cutoff_date, asset_type))
        
        total, correct = cursor.fetchone()
        total = total or 0
        correct = correct or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # 平均误差率
        cursor.execute('''
            SELECT AVG(error_rate)
            FROM predictions
            WHERE timestamp > ? AND asset_type = ? AND error_rate IS NOT NULL
        ''', (cutoff_date, asset_type))
        
        avg_error = cursor.fetchone()[0] or 0
        
        # 分置信度准确率
        confidences = ["HIGH", "MEDIUM", "LOW"]
        conf_accuracy = {}
        
        for conf in confidences:
            cursor.execute('''
                SELECT COUNT(*), SUM(is_correct)
                FROM predictions
                WHERE timestamp > ? AND asset_type = ? 
                AND confidence = ? AND is_correct IS NOT NULL
            ''', (cutoff_date, asset_type, conf))
            
            conf_total, conf_correct = cursor.fetchone()
            conf_total = conf_total or 0
            conf_correct = conf_correct or 0
            conf_accuracy[conf] = (conf_correct / conf_total * 100) if conf_total > 0 else 0
        
        return {
            "period_days": days,
            "asset_type": asset_type,
            "total_predictions": total,
            "correct_predictions": correct,
            "accuracy_rate": round(accuracy, 2),
            "avg_error_rate": round(avg_error * 100, 2),
            "high_conf_accuracy": round(conf_accuracy["HIGH"], 2),
            "medium_conf_accuracy": round(conf_accuracy["MEDIUM"], 2),
            "low_conf_accuracy": round(conf_accuracy["LOW"], 2)
        }
    
    def get_all_accuracy_stats(self, asset_type: str = "gold") -> Dict:
        """获取所有周期准确率统计"""
        return {
            "7_days": self.calculate_accuracy(7, asset_type),
            "30_days": self.calculate_accuracy(30, asset_type),
            "90_days": self.calculate_accuracy(90, asset_type)
        }
    
    def get_recent_predictions(self, days: int = 7, asset_type: str = "gold") -> List[Dict]:
        """获取最近预测"""
        cursor = self.conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT id, timestamp, asset_type, predicted_direction, predicted_price,
                   actual_direction, actual_price, confidence, confidence_score,
                   is_correct, error_rate
            FROM predictions
            WHERE timestamp > ? AND asset_type = ?
            ORDER BY timestamp DESC
        ''', (cutoff_date, asset_type))
        
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "id": row[0],
                "timestamp": row[1],
                "asset_type": row[2],
                "predicted_direction": row[3],
                "predicted_price": row[4],
                "actual_direction": row[5],
                "actual_price": row[6],
                "confidence": row[7],
                "confidence_score": row[8],
                "is_correct": bool(row[9]) if row[9] is not None else None,
                "error_rate": row[10]
            })
        
        return predictions
    
    def generate_accuracy_report(self) -> str:
        """生成准确率报告"""
        stats = self.get_all_accuracy_stats()
        
        report = f"""
# 📊 预测准确率报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🥇 7天准确率

| 指标 | 数值 |
|------|------|
| 预测总数 | {stats['7_days']['total_predictions']} |
| 正确预测 | {stats['7_days']['correct_predictions']} |
| **准确率** | **{stats['7_days']['accuracy_rate']}%** |
| 平均误差 | {stats['7_days']['avg_error_rate']}% |
| 高置信度准确率 | {stats['7_days']['high_conf_accuracy']}% |
| 中置信度准确率 | {stats['7_days']['medium_conf_accuracy']}% |
| 低置信度准确率 | {stats['7_days']['low_conf_accuracy']}% |

## 🥈 30天准确率

| 指标 | 数值 |
|------|------|
| 预测总数 | {stats['30_days']['total_predictions']} |
| 正确预测 | {stats['30_days']['correct_predictions']} |
| **准确率** | **{stats['30_days']['accuracy_rate']}%** |
| 平均误差 | {stats['30_days']['avg_error_rate']}% |
| 高置信度准确率 | {stats['30_days']['high_conf_accuracy']}% |
| 中置信度准确率 | {stats['30_days']['medium_conf_accuracy']}% |
| 低置信度准确率 | {stats['30_days']['low_conf_accuracy']}% |

## 🥉 90天准确率

| 指标 | 数值 |
|------|------|
| 预测总数 | {stats['90_days']['total_predictions']} |
| 正确预测 | {stats['90_days']['correct_predictions']} |
| **准确率** | **{stats['90_days']['accuracy_rate']}%** |
| 平均误差 | {stats['90_days']['avg_error_rate']}% |
| 高置信度准确率 | {stats['90_days']['high_conf_accuracy']}% |
| 中置信度准确率 | {stats['90_days']['medium_conf_accuracy']}% |
| 低置信度准确率 | {stats['90_days']['low_conf_accuracy']}% |

---

## 📈 准确率趋势

- **短期(7天)**: {'✅ 达标' if stats['7_days']['accuracy_rate'] >= 60 else '⚠️ 需优化'} (目标: 60%+)
- **中期(30天)**: {'✅ 达标' if stats['30_days']['accuracy_rate'] >= 55 else '⚠️ 需优化'} (目标: 55%+)
- **长期(90天)**: {'✅ 达标' if stats['90_days']['accuracy_rate'] >= 55 else '⚠️ 需优化'} (目标: 55%+)

## 💡 优化建议

1. **高置信度预测**: 优先参考高置信度信号，准确率更高
2. **连续错误监控**: 连续3次错误时暂停预测，检查模型
3. **市场环境适应**: 震荡市准确率通常低于趋势市
4. **定期复盘**: 每周回顾错误预测，优化因子权重

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()


def demo_accuracy_tracker():
    """演示准确率追踪"""
    print("="*70)
    print("📊 预测准确率追踪演示")
    print("="*70)
    
    # 创建追踪器（使用内存数据库）
    tracker = AccuracyTracker(":memory:")
    
    print("\n1. 模拟记录10条预测...")
    
    # 模拟10条预测
    predictions = [
        ("gold", "UP", 4500.0, "HIGH", 0.85),
        ("gold", "UP", 4520.0, "MEDIUM", 0.72),
        ("gold", "DOWN", 4550.0, "LOW", 0.55),
        ("gold", "UP", 4480.0, "HIGH", 0.88),
        ("gold", "FLAT", 4510.0, "MEDIUM", 0.65),
        ("gold", "UP", 4530.0, "HIGH", 0.82),
        ("gold", "DOWN", 4560.0, "MEDIUM", 0.70),
        ("gold", "UP", 4490.0, "LOW", 0.58),
        ("gold", "UP", 4540.0, "HIGH", 0.86),
        ("gold", "DOWN", 4570.0, "MEDIUM", 0.68),
    ]
    
    prediction_ids = []
    for asset, direction, price, conf, score in predictions:
        pid = tracker.record_prediction(asset, direction, price, conf, score)
        prediction_ids.append(pid)
    
    print(f"✅ 已记录 {len(prediction_ids)} 条预测")
    
    print("\n2. 模拟更新实际结果...")
    
    # 模拟实际结果（假设70%准确）
    actual_prices = [
        4510.0,  # UP - 正确
        4515.0,  # UP - 正确
        4540.0,  # DOWN - 错误（实际涨）
        4495.0,  # UP - 错误（实际跌）
        4512.0,  # FLAT - 正确
        4540.0,  # UP - 正确
        4550.0,  # DOWN - 正确
        4500.0,  # UP - 正确
        4550.0,  # UP - 正确
        4560.0,  # DOWN - 正确
    ]
    
    for pid, actual in zip(prediction_ids, actual_prices):
        tracker.update_actual_result(pid, actual)
    
    print(f"✅ 已更新 {len(actual_prices)} 条结果")
    
    print("\n3. 计算准确率统计...")
    
    stats = tracker.get_all_accuracy_stats()
    
    print("\n📈 7天准确率:")
    print(f"  总预测: {stats['7_days']['total_predictions']}")
    print(f"  正确: {stats['7_days']['correct_predictions']}")
    print(f"  准确率: {stats['7_days']['accuracy_rate']}%")
    print(f"  高置信度准确率: {stats['7_days']['high_conf_accuracy']}%")
    
    print("\n📈 30天准确率:")
    print(f"  总预测: {stats['30_days']['total_predictions']}")
    print(f"  正确: {stats['30_days']['correct_predictions']}")
    print(f"  准确率: {stats['30_days']['accuracy_rate']}%")
    
    print("\n📈 90天准确率:")
    print(f"  总预测: {stats['90_days']['total_predictions']}")
    print(f"  正确: {stats['90_days']['correct_predictions']}")
    print(f"  准确率: {stats['90_days']['accuracy_rate']}%")
    
    print("\n4. 生成准确率报告...")
    report = tracker.generate_accuracy_report()
    print(report[:500] + "...")
    
    print("\n✅ 演示完成!")
    
    tracker.close()


if __name__ == "__main__":
    demo_accuracy_tracker()
