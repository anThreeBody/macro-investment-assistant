#!/usr/bin/env python3
"""宏观数据网络抓取源

从 Investing.com 抓取宏观数据：
- DXY (美元指数)
- VIX (恐慌指数)
- Oil (原油期货)
- Treasury (10 年期美债收益率)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright 未安装，宏观数据网络抓取不可用")

logger = logging.getLogger(__name__)


class MacroWebSource:
    """宏观数据网络抓取源"""
    
    # 目标网站
    URLS = {
        'dxy': 'https://cn.investing.com/currencies/usdx',
        'vix': 'https://cn.investing.com/indices/vix',
        'oil': 'https://cn.investing.com/commodities/crude-oil',
        'treasury': 'https://cn.investing.com/rates-bonds/u.s.-10-year-bond-yield'
    }
    
    # 兜底数据
    FALLBACK_VALUES = {
        'dxy': 103.5,
        'vix': 15.2,
        'oil': 78.5,
        'treasury': 4.25
    }
    
    # 合理范围（用于验证）
    VALID_RANGES = {
        'dxy': (50, 150),
        'vix': (10, 100),
        'oil': (50, 150),
        'treasury': (1, 10)
    }
    
    def __init__(self):
        """初始化"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[MacroWebSource] Playwright 未安装，请运行：pip3 install playwright")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def fetch_all(self) -> Dict[str, Any]:
        """获取所有宏观数据"""
        logger.info("[网络宏观] 开始获取数据...")
        
        result = {
            'dxy': self._fetch_with_retry('dxy', '美元指数'),
            'vix': self._fetch_with_retry('vix', '恐慌指数'),
            'oil': self._fetch_with_retry('oil', '原油期货'),
            'treasury': self._fetch_with_retry('treasury', '10 年期美债'),
            'metadata': self._get_metadata()
        }
        
        # 打印摘要
        logger.info(
            f"[网络宏观] DXY:{result['dxy']['value']:.2f}, "
            f"VIX:{result['vix']['value']:.2f}, "
            f"原油:${result['oil']['value']:.2f}, "
            f"美债:{result['treasury']['value']:.2f}%"
        )
        
        return result
    
    def _fetch_with_retry(self, key: str, name: str, max_retries: int = 2) -> Dict[str, Any]:
        """带重试的抓取"""
        for attempt in range(max_retries + 1):
            try:
                data = self._fetch_single(key, name)
                if data['value'] > 0:
                    # 验证数据合理性
                    min_val, max_val = self.VALID_RANGES[key]
                    if min_val < data['value'] < max_val:
                        logger.debug(f"[网络宏观] {name} 获取成功：{data['value']}")
                        return data
                    else:
                        logger.warning(f"[网络宏观] {name} 数据异常：{data['value']} (范围：{min_val}-{max_val})")
            except Exception as e:
                logger.warning(f"[网络宏观] {name} 抓取失败 (尝试 {attempt+1}/{max_retries}): {e}")
        
        # 所有尝试失败，返回兜底数据
        logger.warning(f"[网络宏观] {name} 使用兜底数据：{self.FALLBACK_VALUES[key]}")
        return self._get_fallback(key, name)
    
    def _fetch_single(self, key: str, name: str) -> Dict[str, Any]:
        """抓取单个数据"""
        if not PLAYWRIGHT_AVAILABLE:
            return self._get_fallback(key, name)
        
        with sync_playwright() as p:
            browser = None
            page = None
            try:
                # 启动浏览器
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu'
                    ]
                )
                
                # 创建页面
                page = browser.new_page()
                page.set_default_timeout(15000)
                
                # 设置请求头
                page.set_extra_http_headers(self.headers)
                
                # 访问页面
                logger.debug(f"[网络宏观] 访问 {name} 页面...")
                page.goto(self.URLS[key], wait_until='domcontentloaded', timeout=15000)
                
                # 等待页面加载
                page.wait_for_timeout(3000)
                
                # 获取价格
                price = self._extract_price(page, key)
                
                # 获取涨跌幅
                change, change_pct = self._extract_change(page)
                
                browser.close()
                
                if price > 0:
                    return {
                        'name': name,
                        'code': key.upper(),
                        'value': price,
                        'change': change,
                        'change_pct': change_pct,
                        'update_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'source': 'Investing.com'
                    }
                else:
                    logger.warning(f"[网络宏观] {name} 价格提取失败")
                    
            except Exception as e:
                logger.error(f"[网络宏观] {name} 抓取异常：{e}")
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
                return self._get_fallback(key, name)
        
        return self._get_fallback(key, name)
    
    def _extract_price(self, page, key: str) -> float:
        """从页面提取价格"""
        # 尝试多种选择器
        selectors = [
            '[data-test="instrument-price-link"]',
            '[data-test="last"]',
            '.last',
            '[class*="Last"]',
            'span[class*="price"]',
            'span[class*="Price"]',
            '[data-field="last"]',
        ]
        
        for selector in selectors:
            try:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text().strip()
                    price = self._parse_price(text)
                    if price > 0:
                        logger.debug(f"[网络宏观] 通过选择器 '{selector}' 获取价格：{price}")
                        return price
            except Exception as e:
                logger.debug(f"[网络宏观] 选择器 '{selector}' 失败：{e}")
                continue
        
        # 选择器失败，尝试从页面内容提取
        logger.debug(f"[网络宏观] 选择器失败，尝试从内容提取...")
        content = page.content()
        price = self._extract_from_content(content, key)
        
        if price > 0:
            logger.debug(f"[网络宏观] 从内容提取价格：{price}")
        
        return price
    
    def _extract_change(self, page) -> tuple:
        """提取涨跌幅"""
        selectors = [
            '[data-test="instrument-change"]',
            '[class*="change"]',
            '[class*="Change"]',
            'span[class*="changePercent"]',
        ]
        
        for selector in selectors:
            try:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text().strip()
                    change, change_pct = self._parse_change(text)
                    if change != 0 or change_pct != 0:
                        return change, change_pct
            except:
                continue
        
        return 0.0, 0.0
    
    def _parse_price(self, text: str) -> float:
        """解析价格文本"""
        # 移除逗号、空格等非数字字符
        text = text.replace(',', '').strip()
        
        # 提取数字（支持小数）
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        
        return 0.0
    
    def _parse_change(self, text: str) -> tuple:
        """解析涨跌幅"""
        # 移除 % 符号
        text = text.replace('%', '').strip()
        
        # 提取数字（支持负数）
        match = re.search(r'([+-]?\d+\.?\d*)', text)
        if match:
            try:
                change_pct = float(match.group(1))
                return change_pct, change_pct  # 简化处理
            except:
                pass
        
        return 0.0, 0.0
    
    def _extract_from_content(self, content: str, key: str) -> float:
        """从页面内容提取价格"""
        # 根据数据类型设置合理范围
        min_val, max_val = self.VALID_RANGES.get(key, (0, 1000))
        
        # 查找所有数字
        numbers = re.findall(r'(\d+\.?\d*)', content)
        for num_str in numbers:
            try:
                num = float(num_str)
                if min_val < num < max_val:
                    return num
            except:
                continue
        
        return 0.0
    
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
            'source': 'Investing.com',
            'update_time': datetime.now().isoformat(),
            'cache_ttl': 300,
            'playwright_available': PLAYWRIGHT_AVAILABLE
        }
    
    def test_connection(self) -> bool:
        """测试连接"""
        logger.info("[网络宏观] 测试连接...")
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[网络宏观] Playwright 未安装")
            return False
        
        try:
            # 测试抓取 DXY
            result = self._fetch_single('dxy', '美元指数')
            success = result['value'] > 0
            
            if success:
                logger.info(f"[网络宏观] 连接测试成功：DXY={result['value']}")
            else:
                logger.warning("[网络宏观] 连接测试失败")
            
            return success
            
        except Exception as e:
            logger.error(f"[网络宏观] 连接测试异常：{e}")
            return False


# 测试入口
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    print("=" * 60)
    print("宏观数据网络抓取测试")
    print("=" * 60)
    
    source = MacroWebSource()
    
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
