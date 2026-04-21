#!/usr/bin/env python3
"""预测验证器

功能：
- 保存预测结果到数据库
- 次日验证预测准确性
- 统计预测准确率
- 优化因子权重
"""

import logging
import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PredictionValidator:
    """预测验证器"""
    
    def __init__(self, db_path: str = 'data/db/predictions.db'):
        """
        初始化
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库
        
        注意：为保持向后兼容，使用现有表结构
        现有字段：prediction_date, prediction_type, prediction_content, is_accurate, confidence
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # 创建新表（使用兼容的表结构）
            cursor.execute('''
                CREATE TABLE predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    predict_date TEXT NOT NULL,
                    predict_time TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    predicted_price REAL NOT NULL,
                    price_lower REAL,
                    price_upper REAL,
                    direction TEXT,
                    confidence TEXT,
                    factors TEXT,
                    verified INTEGER DEFAULT 0,
                    actual_price REAL,
                    error REAL,
                    error_pct REAL,
                    direction_correct INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP
                )
            ''')
            logger.info("[预测验证] 创建新 predictions 表")
        else:
            # 表已存在，检查并添加缺失的列
            cursor.execute("PRAGMA table_info(predictions)")
            columns = {row[1] for row in cursor.fetchall()}
            
            # 添加缺失的列
            if 'predict_date' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN predict_date TEXT")
                logger.info("[预测验证] 添加列：predict_date")
            if 'predict_time' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN predict_time TEXT")
                logger.info("[预测验证] 添加列：predict_time")
            if 'current_price' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN current_price REAL")
                logger.info("[预测验证] 添加列：current_price")
            if 'predicted_price' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN predicted_price REAL")
                logger.info("[预测验证] 添加列：predicted_price")
            if 'price_lower' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN price_lower REAL")
                logger.info("[预测验证] 添加列：price_lower")
            if 'price_upper' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN price_upper REAL")
                logger.info("[预测验证] 添加列：price_upper")
            if 'direction' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN direction TEXT")
                logger.info("[预测验证] 添加列：direction")
            if 'verified' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN verified INTEGER DEFAULT 0")
                logger.info("[预测验证] 添加列：verified")
            if 'direction_correct' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN direction_correct INTEGER")
                logger.info("[预测验证] 添加列：direction_correct")
            if 'factors' not in columns:
                cursor.execute("ALTER TABLE predictions ADD COLUMN factors TEXT")
                logger.info("[预测验证] 添加列：factors")
        
        conn.commit()
        conn.close()
        
        logger.info(f"[预测验证] 数据库初始化完成：{self.db_path}")
    
    def save_prediction(self, prediction: Dict[str, Any]) -> bool:
        """
        保存预测结果
        
        Args:
            prediction: 预测结果字典
        
        Returns:
            bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            factors = prediction.get('analysis', {}).get('scores', {})
            
            cursor.execute('''
                INSERT INTO predictions (
                    predict_date, predict_time, current_price, predicted_price,
                    price_lower, price_upper, direction, confidence, factors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.get('predict_date', datetime.now().strftime('%Y-%m-%d')),
                prediction.get('predict_time', datetime.now().strftime('%H:%M:%S')),
                prediction.get('current_price', 0),
                prediction.get('predicted_price', 0),
                prediction.get('price_lower', 0),
                prediction.get('price_upper', 0),
                prediction.get('direction', 'unknown'),
                prediction.get('confidence', 'unknown'),
                json.dumps(factors)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(
                f"[预测验证] 预测已保存 - "
                f"当前：¥{prediction.get('current_price', 0):.2f}, "
                f"预测：¥{prediction.get('predicted_price', 0):.2f}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[预测验证] 保存失败：{e}")
            return False
    
    def verify_prediction(self, date: str, actual_price: float) -> Optional[Dict[str, Any]]:
        """
        验证指定日期的预测
        
        Args:
            date: 预测日期 (YYYY-MM-DD)
            actual_price: 实际价格
        
        Returns:
            Dict: 验证结果，失败返回 None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找预测
            cursor.execute('''
                SELECT id, predicted_price, direction, price_lower, price_upper
                FROM predictions
                WHERE predict_date = ? AND verified = 0
            ''', (date,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"[预测验证] 未找到 {date} 的未验证预测")
                conn.close()
                return None
            
            pred_id, predicted_price, direction, price_lower, price_upper = row
            
            # 获取当前价格（用于计算实际涨跌幅）
            cursor.execute('''
                SELECT current_price FROM predictions WHERE id = ?
            ''', (pred_id,))
            current_price = cursor.fetchone()[0]
            
            # 计算误差
            error = abs(predicted_price - actual_price)
            error_pct = error / actual_price if actual_price > 0 else 0
            accuracy = 1 - error_pct
            
            # 计算实际涨跌幅
            actual_change_pct = (actual_price - current_price) / current_price * 100 if current_price else 0
            
            # 判断实际方向（基于实际涨跌幅，取消震荡，只保留上涨/下跌）
            # 阈值调整为±0.5%，更敏感地捕捉方向变化
            if actual_change_pct > 0.5:  # 上涨超过 0.5%
                pred_direction = 'up'
            else:  # 下跌或持平都算下跌（<= 0.5%）
                pred_direction = 'down'
            
            # 判断方向是否正确
            direction_correct = 1 if pred_direction == direction else 0
            
            logger.info(f"[预测验证] {date} 方向判断：预测={direction}, 实际={pred_direction} (涨跌幅={actual_change_pct:.2f}%), 结果={'正确' if direction_correct else '错误'}")
            
            # 判断价格区间是否命中
            in_range = 1 if price_lower <= actual_price <= price_upper else 0
            
            # 更新记录
            cursor.execute('''
                UPDATE predictions
                SET verified = 1, actual_price = ?, error = ?, error_pct = ?,
                    direction_correct = ?, verified_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (actual_price, error, error_pct, direction_correct, pred_id))
            
            conn.commit()
            conn.close()
            
            result = {
                'predicted': predicted_price,
                'actual': actual_price,
                'error': round(error, 2),
                'error_pct': round(error_pct, 4),
                'accuracy': round(accuracy, 4),
                'direction_correct': bool(direction_correct),
                'in_range': bool(in_range)
            }
            
            logger.info(
                f"[预测验证] {date} 验证完成 - "
                f"预测：¥{predicted_price:.2f}, 实际：¥{actual_price:.2f}, "
                f"误差：{error_pct:.2%}, 准确率：{accuracy:.2%}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[预测验证] 验证失败：{e}")
            return None
    
    def get_accuracy_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        获取准确率统计
        
        Args:
            days: 统计天数
        
        Returns:
            Dict: 统计结果
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询最近 N 天的验证记录
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(direction_correct) as correct,
                    AVG(error_pct) as avg_error,
                    AVG(1 - error_pct) as avg_accuracy
                FROM predictions
                WHERE verified = 1 AND predict_date >= ?
            ''', (cutoff_date,))
            
            row = cursor.fetchone()
            conn.close()
            
            total = row[0] or 0
            correct = row[1] or 0
            avg_error = row[2] or 0
            avg_accuracy = row[3] or 0
            
            return {
                'total': total,
                'correct': correct,
                'accuracy': round(avg_accuracy, 4) if total > 0 else 0,
                'avg_error_pct': round(avg_error, 4),
                'period_days': days,
                'success_rate': round(correct / total, 4) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"[预测验证] 统计失败：{e}")
            return {
                'total': 0,
                'correct': 0,
                'accuracy': 0,
                'avg_error_pct': 0,
                'period_days': days,
                'success_rate': 0
            }
    
    def get_all_predictions(self, limit: int = 30) -> List[Dict[str, Any]]:
        """获取所有预测记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                ORDER BY predict_date DESC, predict_time DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"[预测验证] 查询失败：{e}")
            return []
    
    def export_report(self, days: int = 30) -> Dict[str, Any]:
        """
        导出预测报告
        
        Args:
            days: 统计天数
        
        Returns:
            Dict: 完整报告
        """
        stats = self.get_accuracy_stats(days)
        predictions = self.get_all_predictions(limit=days)
        
        return {
            'stats': stats,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        }


# 测试入口
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    print("=" * 60)
    print("预测验证器测试")
    print("=" * 60)
    
    validator = PredictionValidator(db_path='data/db/test_predictions.db')
    
    # 保存预测
    print("\n1. 保存预测...")
    test_prediction = {
        'predict_date': '2026-03-26',
        'predict_time': '08:00:00',
        'current_price': 1000.0,
        'predicted_price': 1010.0,
        'price_lower': 995.0,
        'price_upper': 1025.0,
        'direction': 'up',
        'confidence': '中',
        'analysis': {'scores': {'technical': 0.6, 'sentiment': 0.5, 'macro': 0.4, 'momentum': 0.7}}
    }
    
    if validator.save_prediction(test_prediction):
        print("   ✅ 保存成功")
    else:
        print("   ❌ 保存失败")
    
    # 验证预测
    print("\n2. 验证预测...")
    result = validator.verify_prediction('2026-03-26', 1008.0)
    if result:
        print(f"   预测：¥{result['predicted']:.2f}")
        print(f"   实际：¥{result['actual']:.2f}")
        print(f"   误差：{result['error_pct']:.2%}")
        print(f"   准确率：{result['accuracy']:.2%}")
        print(f"   方向正确：{result['direction_correct']}")
    else:
        print("   ❌ 验证失败")
    
    # 获取统计
    print("\n3. 准确率统计...")
    stats = validator.get_accuracy_stats(days=30)
    print(f"   总预测数：{stats['total']}")
    print(f"   正确数：{stats['correct']}")
    print(f"   准确率：{stats['accuracy']:.2%}")
    print(f"   成功率：{stats['success_rate']:.2%}")
    
    print("\n" + "=" * 60)
