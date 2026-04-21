#!/usr/bin/env python3
"""
数据源基类 - 定义所有数据源的标准接口
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str                          # 数据源名称
    source_type: str                   # 数据类型：gold/fund/stock/news/macro
    cache_enabled: bool = True         # 是否启用缓存
    cache_ttl: int = 300              # 缓存 TTL（秒），默认 5 分钟
    retry_times: int = 3              # 重试次数
    timeout: int = 30                 # 超时时间（秒）
    extra_params: Dict = field(default_factory=dict)  # 额外参数


class DataSource(ABC):
    """数据源基类"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.cache_dir = Path(__file__).parent.parent / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """
        获取数据（抽象方法，子类必须实现）
        
        Returns:
            Dict[str, Any]: 标准化数据格式
        """
        pass
    
    def fetch_with_cache(self, **kwargs) -> Dict[str, Any]:
        """
        带缓存的数据获取
        
        Returns:
            Dict[str, Any]: 标准化数据格式
        """
        if not self.config.cache_enabled:
            return self.fetch(**kwargs)
        
        # 尝试从缓存读取
        cache_data = self._read_cache()
        if cache_data:
            logger.info(f"[{self.config.name}] 使用缓存数据")
            return cache_data
        
        # 缓存未命中，获取新数据
        logger.info(f"[{self.config.name}] 缓存未命中，获取新数据")
        data = self.fetch(**kwargs)
        
        # 保存到缓存
        self._write_cache(data)
        
        return data
    
    def _get_cache_path(self) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{self.config.source_type}_latest.json"
    
    def _read_cache(self) -> Optional[Dict[str, Any]]:
        """读取缓存"""
        cache_path = self._get_cache_path()
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cached_at = cache_data.get('_meta', {}).get('cached_at', '')
            if cached_at:
                cached_time = datetime.fromisoformat(cached_at)
                elapsed = (datetime.now() - cached_time).total_seconds()
                
                if elapsed > self.config.cache_ttl:
                    logger.info(f"[{self.config.name}] 缓存已过期 ({elapsed:.0f}s > {self.config.cache_ttl}s)")
                    return None
            
            return cache_data
        except Exception as e:
            logger.warning(f"[{self.config.name}] 读取缓存失败：{e}")
            return None
    
    def _write_cache(self, data: Dict[str, Any]) -> None:
        """写入缓存"""
        cache_path = self._get_cache_path()
        
        # 添加元数据
        cache_data = {
            '_meta': {
                'cached_at': datetime.now().isoformat(),
                'source': self.config.name,
                'source_type': self.config.source_type,
            },
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"[{self.config.name}] 缓存已保存")
        except Exception as e:
            logger.error(f"[{self.config.name}] 保存缓存失败：{e}")
    
    def _validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """验证数据完整性"""
        for field in required_fields:
            if field not in data:
                logger.error(f"[{self.config.name}] 数据缺少必需字段：{field}")
                return False
        return True
    
    def get_standard_metadata(self) -> Dict[str, Any]:
        """获取标准元数据"""
        return {
            'source': self.config.name,
            'source_type': self.config.source_type,
            'fetched_at': datetime.now().isoformat(),
            'version': '1.0.0',
        }
