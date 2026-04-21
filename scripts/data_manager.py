#!/usr/bin/env python3
"""
数据管理模块

负责：
1. 本地数据库存储
2. 数据同步（从 akshare 等源）
3. 缓存管理
4. 数据查询
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """数据管理器"""
    
    def __init__(self, db_dir: str = None):
        if db_dir is None:
            # 默认路径：skill 目录下的 data 文件夹
            self.db_dir = Path(__file__).parent.parent / "data"
        else:
            self.db_dir = Path(db_dir)
        
        self.db_dir.mkdir(exist_ok=True)
        
        # 初始化数据库
        self._init_databases()
    
    def _init_databases(self):
        """初始化所有数据库"""
        # 黄金价格数据库
        self._init_gold_db()
        # 基金数据库
        self._init_fund_db()
        # 宏观指标数据库
        self._init_macro_db()
        # 政策数据库
        self._init_policy_db()
        # 预测记录数据库
        self._init_prediction_db()
    
    def _init_gold_db(self):
        """初始化黄金价格数据库"""
        conn = sqlite3.connect(self.db_dir / "gold_prices.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gold_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                morning_price REAL,
                evening_price REAL,
                source TEXT DEFAULT 'SGE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_gold_date ON gold_prices(date)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Gold database initialized")
    
    def _init_fund_db(self):
        """初始化基金数据库"""
        conn = sqlite3.connect(self.db_dir / "fund_nav.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_info (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_nav (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code TEXT NOT NULL,
                date TEXT NOT NULL,
                nav REAL,
                accumulated_nav REAL,
                daily_return REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fund_code) REFERENCES fund_info(code),
                UNIQUE(fund_code, date)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fund_nav_date ON fund_nav(fund_code, date)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Fund database initialized")
    
    def _init_macro_db(self):
        """初始化宏观指标数据库"""
        conn = sqlite3.connect(self.db_dir / "macro_indicators.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_name TEXT NOT NULL,
                date TEXT NOT NULL,
                value REAL,
                yoy_change REAL,
                mom_change REAL,
                unit TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(indicator_name, date)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_macro_indicator ON macro_indicators(indicator_name, date)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Macro database initialized")
    
    def _init_policy_db(self):
        """初始化政策数据库"""
        conn = sqlite3.connect(self.db_dir / "policies.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT,
                source TEXT,
                url TEXT,
                summary TEXT,
                category TEXT,
                impact TEXT,
                keywords TEXT,
                is_processed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_policy_date ON policies(date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_policy_category ON policies(category)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Policy database initialized")
    
    def _init_prediction_db(self):
        """初始化预测记录数据库"""
        conn = sqlite3.connect(self.db_dir / "predictions.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL,
                asset_code TEXT,
                prediction_date TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                prediction_content TEXT NOT NULL,
                rationale TEXT,
                confidence REAL,
                target_date TEXT,
                actual_result TEXT,
                is_accurate BOOLEAN,
                accuracy_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_prediction_date ON predictions(prediction_date)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Prediction database initialized")
    
    # ==================== 黄金数据操作 ====================
    
    def save_gold_price(self, date: str, morning_price: float = None, 
                        evening_price: float = None, source: str = 'SGE'):
        """保存黄金价格"""
        conn = sqlite3.connect(self.db_dir / "gold_prices.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO gold_prices 
                (date, morning_price, evening_price, source, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, morning_price, evening_price, source, datetime.now()))
            
            conn.commit()
            logger.info(f"Saved gold price for {date}")
        except Exception as e:
            logger.error(f"Error saving gold price: {e}")
        finally:
            conn.close()
    
    def get_gold_prices(self, start_date: str = None, end_date: str = None, 
                        limit: int = 100) -> List[Dict]:
        """获取黄金价格历史"""
        conn = sqlite3.connect(self.db_dir / "gold_prices.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM gold_prices WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        conn.close()
        
        return result
    
    def get_latest_gold_price(self) -> Optional[Dict]:
        """获取最新黄金价格"""
        prices = self.get_gold_prices(limit=1)
        return prices[0] if prices else None
    
    # ==================== 基金数据操作 ====================
    
    def save_fund_info(self, code: str, name: str, fund_type: str = None, 
                       category: str = None):
        """保存基金信息"""
        conn = sqlite3.connect(self.db_dir / "fund_nav.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO fund_info (code, name, type, category)
                VALUES (?, ?, ?, ?)
            ''', (code, name, fund_type, category))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving fund info: {e}")
        finally:
            conn.close()
    
    def save_fund_nav(self, fund_code: str, date: str, nav: float,
                      accumulated_nav: float = None, daily_return: float = None):
        """保存基金净值"""
        conn = sqlite3.connect(self.db_dir / "fund_nav.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO fund_nav 
                (fund_code, date, nav, accumulated_nav, daily_return)
                VALUES (?, ?, ?, ?, ?)
            ''', (fund_code, date, nav, accumulated_nav, daily_return))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving fund NAV: {e}")
        finally:
            conn.close()
    
    # ==================== 宏观数据操作 ====================
    
    def save_macro_indicator(self, indicator_name: str, date: str, value: float,
                             yoy_change: float = None, mom_change: float = None,
                             unit: str = None, source: str = None):
        """保存宏观指标"""
        conn = sqlite3.connect(self.db_dir / "macro_indicators.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO macro_indicators 
                (indicator_name, date, value, yoy_change, mom_change, unit, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (indicator_name, date, value, yoy_change, mom_change, unit, source))
            
            conn.commit()
            logger.info(f"Saved {indicator_name} for {date}")
        except Exception as e:
            logger.error(f"Error saving macro indicator: {e}")
        finally:
            conn.close()
    
    def get_macro_indicator(self, indicator_name: str, 
                            start_date: str = None, limit: int = 100) -> List[Dict]:
        """获取宏观指标历史"""
        conn = sqlite3.connect(self.db_dir / "macro_indicators.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM macro_indicators WHERE indicator_name = ?"
        params = [indicator_name]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        conn.close()
        
        return result
    
    # ==================== 政策数据操作 ====================
    
    def save_policy(self, title: str, date: str = None, source: str = None,
                    url: str = None, summary: str = None, category: str = None,
                    impact: str = None, keywords: str = None):
        """保存政策"""
        conn = sqlite3.connect(self.db_dir / "policies.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO policies 
                (title, date, source, url, summary, category, impact, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, date, source, url, summary, category, impact, keywords))
            
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Saved policy: {title[:50]}...")
        except Exception as e:
            logger.error(f"Error saving policy: {e}")
        finally:
            conn.close()
    
    def get_recent_policies(self, category: str = None, days: int = 30, 
                            limit: int = 50) -> List[Dict]:
        """获取近期政策"""
        conn = sqlite3.connect(self.db_dir / "policies.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = "SELECT * FROM policies WHERE date >= ?"
        params = [start_date]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        conn.close()
        
        return result
    
    # ==================== 预测记录操作 ====================
    
    def save_prediction(self, asset_type: str, prediction_date: str,
                        prediction_type: str, prediction_content: str,
                        asset_code: str = None, rationale: str = None,
                        confidence: float = None, target_date: str = None):
        """保存预测"""
        conn = sqlite3.connect(self.db_dir / "predictions.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO predictions 
                (asset_type, asset_code, prediction_date, prediction_type, 
                 prediction_content, rationale, confidence, target_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (asset_type, asset_code, prediction_date, prediction_type,
                  prediction_content, rationale, confidence, target_date))
            
            conn.commit()
            logger.info(f"Saved prediction for {asset_type}")
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
        finally:
            conn.close()
    
    def update_prediction_result(self, prediction_id: int, actual_result: str,
                                  is_accurate: bool, accuracy_score: float = None):
        """更新预测结果"""
        conn = sqlite3.connect(self.db_dir / "predictions.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE predictions 
                SET actual_result = ?, is_accurate = ?, accuracy_score = ?, 
                    updated_at = ?
                WHERE id = ?
            ''', (actual_result, is_accurate, accuracy_score, datetime.now(), prediction_id))
            
            conn.commit()
            logger.info(f"Updated prediction {prediction_id}")
        except Exception as e:
            logger.error(f"Error updating prediction: {e}")
        finally:
            conn.close()
    
    def get_prediction_accuracy(self, asset_type: str = None, 
                                 days: int = 90) -> Dict:
        """获取预测准确率统计"""
        conn = sqlite3.connect(self.db_dir / "predictions.db")
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = '''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_accurate = 1 THEN 1 ELSE 0 END) as accurate
            FROM predictions 
            WHERE prediction_date >= ? AND is_accurate IS NOT NULL
        '''
        params = [start_date]
        
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        total = row[0] if row else 0
        accurate = row[1] if row else 0
        accuracy = (accurate / total * 100) if total > 0 else 0
        
        conn.close()
        
        return {
            "total_predictions": total,
            "accurate_predictions": accurate,
            "accuracy_rate": round(accuracy, 2),
            "period_days": days
        }


# 单例模式
data_manager = None

def get_data_manager() -> DataManager:
    """获取数据管理器实例"""
    global data_manager
    if data_manager is None:
        data_manager = DataManager()
    return data_manager


if __name__ == '__main__':
    # 测试
    dm = DataManager()
    
    # 测试保存黄金价格
    dm.save_gold_price('2026-03-18', 500.5, 501.2)
    
    # 测试查询
    prices = dm.get_gold_prices(limit=5)
    print(f"Gold prices: {prices}")
    
    # 测试保存政策
    dm.save_policy(
        title="测试政策",
        date="2026-03-18",
        source="测试",
        category="测试",
        impact="中性"
    )
    
    # 测试查询政策
    policies = dm.get_recent_policies(limit=5)
    print(f"Policies: {policies}")
