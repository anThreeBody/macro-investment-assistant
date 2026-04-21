"""
配置管理模块
负责加载和管理系统配置
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """配置管理器 - 单例模式"""
    
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self.load()
    
    def load(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，默认使用 config.yaml
            
        Returns:
            配置字典
        """
        if config_path is None:
            # 默认配置文件路径
            config_path = Path(__file__).parent.parent / 'config.yaml'
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            # 配置文件不存在时使用默认配置
            self._config = self._get_default_config()
            return self._config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            return self._config
        except Exception as e:
            print(f"⚠️ 加载配置文件失败：{e}，使用默认配置")
            self._config = self._get_default_config()
            return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持嵌套键，如 'data_sources.cache_ttl.gold'）
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self._config
    
    def reload(self) -> Dict[str, Any]:
        """重新加载配置"""
        return self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            'system': {
                'name': 'Macro-Investment-Assistant',
                'version': '8.1.0',
                'environment': 'production',
                'debug': False
            },
            'data_sources': {
                'cache_ttl': {
                    'gold': 60,
                    'fund': 300,
                    'stock': 60,
                    'macro': 300,
                    'news': 600
                },
                'timeout': 30,
                'max_retries': 3,
                'fallback_enabled': True
            },
            'prediction': {
                'weights': {
                    'technical': 0.255,
                    'sentiment': 0.2125,
                    'macro': 0.2125,
                    'momentum': 0.17,
                    'time_series': 0.15
                },
                'confidence_thresholds': {
                    'high': 0.8,
                    'medium': 0.6,
                    'low': 0.4
                }
            },
            'output': {
                'brief_dir': 'daily_brief',
                'chart_dir': 'charts',
                'log_dir': 'logs',
                'log_level': 'INFO'
            }
        }


# 全局配置实例
config = Config()


def get_config(key: str, default: Any = None) -> Any:
    """
    便捷函数：获取配置值
    
    Args:
        key: 配置键（支持嵌套，如 'data_sources.cache_ttl.gold'）
        default: 默认值
        
    Returns:
        配置值
        
    Example:
        >>> from utils.config_loader import get_config
        >>> gold_ttl = get_config('data_sources.cache_ttl.gold', 60)
        >>> tech_weight = get_config('prediction.weights.technical', 0.255)
    """
    return config.get(key, default)


def get_all_config() -> Dict[str, Any]:
    """便捷函数：获取全部配置"""
    return config.get_all()


def reload_config() -> Dict[str, Any]:
    """便捷函数：重新加载配置"""
    return config.reload()


if __name__ == '__main__':
    # 测试配置加载
    print("=== 配置加载测试 ===\n")
    
    # 加载配置
    cfg = Config()
    
    # 测试获取配置
    print(f"系统名称：{cfg.get('system.name')}")
    print(f"系统版本：{cfg.get('system.version')}")
    print(f"环境：{cfg.get('system.environment')}")
    print(f"调试模式：{cfg.get('system.debug')}")
    print()
    
    print(f"金价缓存 TTL: {cfg.get('data_sources.cache_ttl.gold')} 秒")
    print(f"宏观缓存 TTL: {cfg.get('data_sources.cache_ttl.macro')} 秒")
    print(f"请求超时：{cfg.get('data_sources.timeout')} 秒")
    print()
    
    print("预测权重:")
    weights = cfg.get('prediction.weights', {})
    for key, value in weights.items():
        print(f"  - {key}: {value:.2%}")
    print()
    
    print(f"高置信度阈值：{cfg.get('prediction.confidence_thresholds.high', 0.8):.0%}")
    print(f"中置信度阈值：{cfg.get('prediction.confidence_thresholds.medium', 0.6):.0%}")
    print(f"低置信度阈值：{cfg.get('prediction.confidence_thresholds.low', 0.4):.0%}")
    print()
    
    print(f"简报目录：{cfg.get('output.brief_dir')}")
    print(f"图表目录：{cfg.get('output.chart_dir')}")
    print(f"日志目录：{cfg.get('output.log_dir')}")
    print(f"日志级别：{cfg.get('output.log_level')}")
    print()
    
    # 测试便捷函数
    print("=== 便捷函数测试 ===")
    print(f"get_config('system.name'): {get_config('system.name')}")
    print(f"get_config('prediction.weights.technical'): {get_config('prediction.weights.technical')}")
