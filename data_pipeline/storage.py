#!/usr/bin/env python3
"""
数据存储 - 统一数据存储接口

支持：
- SQLite 数据库
- JSON 文件
- CSV 文件
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataStorage:
    """数据存储"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data"
        
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据库连接缓存
        self._db_connections = {}
    
    def save_json(self, data: Dict[str, Any], filename: str) -> Path:
        """
        保存为 JSON 文件
        
        Args:
            data: 数据
            filename: 文件名（不含扩展名）
            
        Returns:
            Path: 保存的文件路径
        """
        filepath = self.base_dir / f"{filename}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[数据存储] JSON 已保存：{filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[数据存储] 保存 JSON 失败：{e}")
            raise
    
    def load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载 JSON 文件
        
        Args:
            filename: 文件名（不含扩展名）
            
        Returns:
            Dict[str, Any]: 数据
        """
        filepath = self.base_dir / f"{filename}.json"
        
        if not filepath.exists():
            logger.warning(f"[数据存储] JSON 文件不存在：{filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"[数据存储] JSON 已加载：{filepath}")
            return data
        except Exception as e:
            logger.error(f"[数据存储] 加载 JSON 失败：{e}")
            return None
    
    def save_csv(self, data: List[Dict[str, Any]], filename: str) -> Path:
        """
        保存为 CSV 文件
        
        Args:
            data: 数据列表
            filename: 文件名（不含扩展名）
            
        Returns:
            Path: 保存的文件路径
        """
        import csv
        
        filepath = self.base_dir / f"{filename}.csv"
        
        if not data:
            logger.warning(f"[数据存储] 空数据，跳过保存")
            return filepath
        
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"[数据存储] CSV 已保存：{filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[数据存储] 保存 CSV 失败：{e}")
            raise
    
    def load_csv(self, filename: str) -> List[Dict[str, Any]]:
        """
        加载 CSV 文件
        
        Args:
            filename: 文件名（不含扩展名）
            
        Returns:
            List[Dict]: 数据列表
        """
        import csv
        
        filepath = self.base_dir / f"{filename}.csv"
        
        if not filepath.exists():
            logger.warning(f"[数据存储] CSV 文件不存在：{filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            logger.info(f"[数据存储] CSV 已加载：{filepath}")
            return data
        except Exception as e:
            logger.error(f"[数据存储] 加载 CSV 失败：{e}")
            return []
    
    def get_db(self, db_name: str) -> sqlite3.Connection:
        """
        获取数据库连接
        
        Args:
            db_name: 数据库名称
            
        Returns:
            sqlite3.Connection: 数据库连接
        """
        if db_name in self._db_connections:
            return self._db_connections[db_name]
        
        db_path = self.base_dir / f"{db_name}.db"
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            self._db_connections[db_name] = conn
            logger.info(f"[数据存储] 数据库已连接：{db_path}")
            return conn
        except Exception as e:
            logger.error(f"[数据存储] 连接数据库失败：{e}")
            raise
    
    def execute_sql(self, db_name: str, sql: str, params: tuple = ()) -> List[Dict]:
        """
        执行 SQL 查询
        
        Args:
            db_name: 数据库名称
            sql: SQL 语句
            params: 参数
            
        Returns:
            List[Dict]: 查询结果
        """
        conn = self.get_db(db_name)
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = [dict(row) for row in rows]
            return result
        except Exception as e:
            logger.error(f"[数据存储] 执行 SQL 失败：{e}")
            return []
    
    def insert_sql(self, db_name: str, table: str, data: Dict[str, Any]) -> int:
        """
        插入数据
        
        Args:
            db_name: 数据库名称
            table: 表名
            data: 数据字典
            
        Returns:
            int: 插入的行 ID
        """
        conn = self.get_db(db_name)
        
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = conn.cursor()
            cursor.execute(sql, tuple(data.values()))
            conn.commit()
            
            row_id = cursor.lastrowid
            logger.info(f"[数据存储] 数据已插入：{table}, ID={row_id}")
            return row_id
        except Exception as e:
            logger.error(f"[数据存储] 插入数据失败：{e}")
            conn.rollback()
            raise
    
    def close_all(self):
        """关闭所有数据库连接"""
        for db_name, conn in self._db_connections.items():
            try:
                conn.close()
                logger.info(f"[数据存储] 数据库已关闭：{db_name}")
            except Exception as e:
                logger.error(f"[数据存储] 关闭数据库失败：{e}")
        
        self._db_connections.clear()
    
    def backup(self, db_name: str, backup_path: Optional[Path] = None) -> Path:
        """
        备份数据库
        
        Args:
            db_name: 数据库名称
            backup_path: 备份路径（可选）
            
        Returns:
            Path: 备份文件路径
        """
        if backup_path is None:
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{db_name}_{timestamp}.db"
        
        db_path = self.base_dir / f"{db_name}.db"
        
        if not db_path.exists():
            logger.warning(f"[数据存储] 数据库不存在：{db_path}")
            return backup_path
        
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"[数据存储] 数据库已备份：{backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"[数据存储] 备份失败：{e}")
            raise
