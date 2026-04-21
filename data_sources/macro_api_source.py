#!/usr/bin/env python3
"""宏观数据 API 源（备用方案）

使用第三方 API 获取宏观数据：
- Yahoo Finance (通过 yfinance 库)
- Alpha Vantage (需 API Key)
- 其他免费 API

作为 Investing.com 抓取的备用方案
"""

import logging
import requests
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance 未安装，Yahoo Finance 数据源不可用")

logger = logging.getLogger(__name__)


class MacroAPISource:
    """宏观数据 API 源"""
    
    # 兜底数据
    FALLBACK_VALUES = {
        'dxy': 103.5,
        'vix': 15.2,
        'oil': 78.5,
        'treasury': 4.25
    }
    
    # Yahoo Finance 代码映射
    YF_SYMBOLS = {
        'dxy': 'DX-Y.NYB',      # 美元指数期货
        'vix': 'VIX',           # 恐慌指数
        'oil': 'CL=F',          # 原油期货
        'treasury': '^TNX',     # 10 年期美债收益率
    }
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        初始化
        
        Args:
            alpha_vantage_key: Alpha Vantage API Key (可选)
        """
        self.alpha_vantage_key = alpha_vantage_key
        self.alpha_vantage_url = 'https://www.alphavantage.co/query'
        
        if not YFINANCE_AVAILABLE:
            logger.warning("[MacroAPISource] yfinance 未安装")
    
    def fetch_all(self) -> Dict[str, Any]:
        """获取所有宏观数据"""
        logger.info("[API 宏观] 开始获取数据...")
        
        result = {
            'dxy': self._fetch_with_fallback('dxy', '美元指数'),
            'vix': self._fetch_with_fallback('vix', '恐慌指数'),
            'oil': self._fetch_with_fallback('oil', '原油期货'),
            'treasury': self._fetch_with_fallback('treasury', '10 年期美债'),
            'metadata': self._get_metadata()
        }
        
        # 打印摘要
        logger.info(
            f"[API 宏观] DXY:{result['dxy']['value']:.2f}, "
            f"VIX:{result['vix']['value']:.2f}, "
            f"原油:${result['oil']['value']:.2f}, "
            f"美债:{result['treasury']['value']:.2f}%"
        )
        
        return result
    
    def _fetch_with_fallback(self, key: str, name: str) -> Dict[str, Any]:
        """带兜底的获取"""
        # 尝试 1: Yahoo Finance
        try:
            data = self._fetch_yahoo(key, name)
            if data['value'] > 0:
                logger.debug(f"[API 宏观] {name} Yahoo Finance 成功：{data['value']}")
                return data
        except Exception as e:
            logger.debug(f"[API 宏观] {name} Yahoo Finance 失败：{e}")
        
        # 尝试 2: Alpha Vantage (如果有 API Key)
        if self.alpha_vantage_key:
            try:
                data = self._fetch_alpha_vantage(key, name)
                if data['value'] > 0:
                    logger.debug(f"[API 宏观] {name} Alpha Vantage 成功：{data['value']}")
                    return data
            except Exception as e:
                logger.debug(f"[API 宏观] {name} Alpha Vantage 失败：{e}")
        
        # 兜底数据
        logger.warning(f"[API 宏观] {name} 使用兜底数据：{self.FALLBACK_VALUES[key]}")
        return self._get_fallback(key, name)
    
    def _fetch_yahoo(self, key: str, name: str) -> Dict[str, Any]:
        """从 Yahoo Finance 获取"""
        if not YFINANCE_AVAILABLE:
            return self._get_fallback(key, name)
        
        symbol = self.YF_SYMBOLS.get(key)
        if not symbol:
            return self._get_fallback(key, name)
        
        try:
            # 获取 ticker
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据（最近 1 天）
            hist = ticker.history(period='1d')
            
            if hist.empty:
                logger.warning(f"[API 宏观] {name} Yahoo Finance 无数据")
                return self._get_fallback(key, name)
            
            # 获取最新价格
            latest = hist.iloc[-1]
            price = float(latest['Close'])
            
            # 计算涨跌幅
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                change = price - prev_close
                change_pct = (change / prev_close) * 100
            else:
                change = 0.0
                change_pct = 0.0
            
            return {
                'name': name,
                'code': key.upper(),
                'value': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'update_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'source': 'Yahoo Finance'
            }
            
        except Exception as e:
            logger.error(f"[API 宏观] {name} Yahoo Finance 异常：{e}")
            return self._get_fallback(key, name)
    
    def _fetch_alpha_vantage(self, key: str, name: str) -> Dict[str, Any]:
        """从 Alpha Vantage 获取"""
        if not self.alpha_vantage_key:
            return self._get_fallback(key, name)
        
        # Alpha Vantage 函数映射
        functions = {
            'dxy': ('CURRENCY_EXCHANGE_RATE', {'from_currency': 'USD', 'to_currency': 'EUR'}),
            'vix': None,  # Alpha Vantage 不支持 VIX
            'oil': ('GLOBAL_QUOTE', {'symbol': 'USO'}),
            'treasury': None,  # Alpha Vantage 不支持美债
        }
        
        func_info = functions.get(key)
        if not func_info:
            return self._get_fallback(key, name)
        
        function, params = func_info
        
        try:
            params['function'] = function
            params['apikey'] = self.alpha_vantage_key
            
            response = requests.get(
                self.alpha_vantage_url,
                params=params,
                timeout=10
            )
            
            data = response.json()
            
            # 解析响应
            if function == 'CURRENCY_EXCHANGE_RATE':
                rate_data = data.get('Realtime Currency Exchange Rate', {})
                price = float(rate_data.get('5. Exchange Rate', 0))
            elif function == 'GLOBAL_QUOTE':
                quote_data = data.get('Global Quote', {})
                price = float(quote_data.get('05. price', 0))
            else:
                price = 0
            
            if price > 0:
                return {
                    'name': name,
                    'code': key.upper(),
                    'value': price,
                    'change': 0.0,
                    'change_pct': 0.0,
                    'update_date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'Alpha Vantage'
                }
            
        except Exception as e:
            logger.error(f"[API 宏观] {name} Alpha Vantage 异常：{e}")
        
        return self._get_fallback(key, name)
    
    def _get_fallback(self, key: str, name: str) -> Dict[str, Any]:
        """兜底数据"""
        return {
            'name': name,
            'code': key.upper(),
            'value': self.FALLBACK_VALUES.get(key, 0.0),
            'change': 0.0,
            'change_pct': 0.0,
            'update_date': datetime.now().strftime('%Y-%m-%d'),
            'source': '兜底数据'
        }
    
    def _get_metadata(self) -> Dict[str, Any]:
        """获取元数据"""
        return {
            'source': 'Yahoo Finance / Alpha Vantage',
            'update_time': datetime.now().isoformat(),
            'cache_ttl': 300,
            'yfinance_available': YFINANCE_AVAILABLE,
            'alpha_vantage_configured': bool(self.alpha_vantage_key)
        }
    
    def test_connection(self) -> bool:
        """测试连接"""
        logger.info("[API 宏观] 测试连接...")
        
        if not YFINANCE_AVAILABLE:
            logger.error("[API 宏观] yfinance 未安装")
            return False
        
        try:
            # 测试获取 VIX（最稳定）
            result = self._fetch_yahoo('vix', '恐慌指数')
            success = result['value'] > 0
            
            if success:
                logger.info(f"[API 宏观] 连接测试成功：VIX={result['value']}")
            else:
                logger.warning("[API 宏观] 连接测试失败")
            
            return success
            
        except Exception as e:
            logger.error(f"[API 宏观] 连接测试异常：{e}")
            return False


# 测试入口
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    print("=" * 60)
    print("宏观数据 API 测试")
    print("=" * 60)
    
    source = MacroAPISource()
    
    # 测试连接
    print("\n1. 测试连接...")
    if source.test_connection():
        print("   ✅ 连接正常")
    else:
        print("   ⚠️ 连接异常")
    
    # 获取所有数据
    print("\n2. 获取宏观数据...")
    data = source.fetch_all()
    
    print("\n3. 结果摘要:")
    print(f"   DXY: {data['dxy']['value']:.2f} ({data['dxy']['source']})")
    print(f"   VIX: {data['vix']['value']:.2f} ({data['vix']['source']})")
    print(f"   原油：${data['oil']['value']:.2f} ({data['oil']['source']})")
    print(f"   美债：{data['treasury']['value']:.2f}% ({data['treasury']['source']})")
    
    print("\n" + "=" * 60)
