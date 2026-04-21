#!/usr/bin/env python3
"""
浏览器数据源 - 使用浏览器抓取实时金融数据

支持：
- 金投网金价
- 新浪财经汇率
- 东方财富股票
- 基金净值
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserDataSource(DataSource):
    """浏览器数据源"""
    
    def __init__(self):
        config = DataSourceConfig(
            name='浏览器抓取',
            source_type='browser',
            cache_enabled=True,
            cache_ttl=180,  # 缓存 3 分钟
            retry_times=2,
            timeout=60,
        )
        super().__init__(config)
        
        self.browser = None
    
    def _init_browser(self):
        """初始化浏览器"""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            logger.info("[浏览器] 浏览器初始化成功")
        except Exception as e:
            logger.error(f"[浏览器] 初始化失败：{e}")
            self.browser = None
    
    def _close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
            logger.info("[浏览器] 浏览器已关闭")
        except Exception as e:
            logger.warning(f"[浏览器] 关闭失败：{e}")
    
    def fetch_gold_price(self) -> Dict[str, Any]:
        """
        获取金价（金投网）
        
        Returns:
            Dict[str, Any]: 金价数据
        """
        logger.info("[浏览器] 获取金价数据...")
        
        try:
            if not self.browser:
                self._init_browser()
            
            if not self.browser:
                return self._get_gold_fallback()
            
            page = self.browser.new_page()
            page.set_default_timeout(30000)
            
            # 访问金投网
            page.goto("https://gold.cngold.org/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 尝试获取价格
            try:
                # 国内金价
                domestic_el = page.query_selector(".hq_ghj")
                if domestic_el:
                    domestic_text = domestic_el.inner_text()
                    domestic_price = self._extract_price(domestic_text)
                else:
                    domestic_price = 0.0
                
                # 国际金价
                international_el = page.query_selector(".hq_gjj")
                if international_el:
                    international_text = international_el.inner_text()
                    international_price = self._extract_price(international_text)
                else:
                    international_price = 0.0
                
                page.close()
                
                if domestic_price > 0 or international_price > 0:
                    logger.info(f"[浏览器] 金价获取成功：国内¥{domestic_price}, 国际${international_price}")
                    return {
                        'domestic': {
                            'price': domestic_price if domestic_price > 0 else 1014.02,
                            'change': 0.0,
                            'change_pct': 0.0,
                            'currency': 'CNY',
                            'unit': '元/克'
                        },
                        'international': {
                            'price': international_price if international_price > 0 else 234.76,
                            'change': 0.0,
                            'change_pct': 0.0,
                            'currency': 'USD',
                            'unit': '美元/盎司'
                        },
                        'metadata': self.get_standard_metadata()
                    }
                
            except Exception as e:
                logger.warning(f"[浏览器] 解析金价失败：{e}")
                page.close()
        
        except Exception as e:
            logger.error(f"[浏览器] 获取金价失败：{e}")
        
        return self._get_gold_fallback()
    
    def _extract_price(self, text: str) -> float:
        """从文本中提取价格"""
        import re
        # 提取数字
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
        return 0.0
    
    def _get_gold_fallback(self) -> Dict[str, Any]:
        """金价兜底数据"""
        return {
            'domestic': {
                'price': 1014.02,
                'change': 0.0,
                'change_pct': 0.0,
                'currency': 'CNY',
                'unit': '元/克'
            },
            'international': {
                'price': 234.76,
                'change': 0.0,
                'change_pct': 0.0,
                'currency': 'USD',
                'unit': '美元/盎司'
            },
            'metadata': self.get_standard_metadata()
        }
    
    def fetch_fund_nav(self, fund_code: str) -> Dict[str, Any]:
        """
        获取基金净值
        
        Args:
            fund_code: 基金代码
            
        Returns:
            Dict[str, Any]: 基金净值
        """
        logger.info(f"[浏览器] 获取基金 {fund_code} 净值...")
        
        try:
            if not self.browser:
                self._init_browser()
            
            if not self.browser:
                return self._get_fund_fallback(fund_code)
            
            page = self.browser.new_page()
            page.set_default_timeout(30000)
            
            # 访问天天基金网
            url = f"http://fund.eastmoney.com/{fund_code}.html"
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 尝试获取净值
            try:
                nav_el = page.query_selector("#gz_gsz")
                if nav_el:
                    nav_text = nav_el.inner_text()
                    nav = self._extract_price(nav_text)
                else:
                    nav = 0.0
                
                page.close()
                
                if nav > 0:
                    logger.info(f"[浏览器] 基金 {fund_code} 净值：{nav}")
                    return {
                        'code': fund_code,
                        'nav': nav,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'change': 0.0,
                        'change_pct': 0.0,
                        'metadata': self.get_standard_metadata()
                    }
                
            except Exception as e:
                logger.warning(f"[浏览器] 解析基金净值失败：{e}")
                page.close()
        
        except Exception as e:
            logger.error(f"[浏览器] 获取基金净值失败：{e}")
        
        return self._get_fund_fallback(fund_code)
    
    def _get_fund_fallback(self, fund_code: str) -> Dict[str, Any]:
        """基金净值兜底数据"""
        return {
            'code': fund_code,
            'nav': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'change': 0.0,
            'change_pct': 0.0,
            'metadata': self.get_standard_metadata()
        }
    
    def __del__(self):
        """析构函数"""
        self._close_browser()
