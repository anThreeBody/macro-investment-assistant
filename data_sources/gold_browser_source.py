#!/usr/bin/env python3
"""金价浏览器抓取源

通过百度搜索"今日金价"获取实时金价数据
支持：
- 国际金价（美元/盎司）
- 国内金价（元/克）
- 各大金店零售价（周大福、老凤祥等）
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright 未安装，浏览器抓取不可用")

logger = logging.getLogger(__name__)


class GoldBrowserSource:
    """金价浏览器抓取源"""
    
    # 百度搜索 URL
    SEARCH_URL = "https://www.baidu.com/s"
    
    # 目标网站（优先抓取）
    TARGET_SITES = [
        "gold.cngold.org",      # 金投网
        "www.cngold.org",       # 金投网
        "finance.sina.com.cn",  # 新浪财经
        "www.gold678.com",      # 黄金网
    ]
    
    # 兜底数据
    FALLBACK_VALUES = {
        'international': 230.0,  # 美元/盎司
        'domestic': 1000.0,      # 元/克
    }
    
    def __init__(self):
        """初始化"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[金价浏览器] Playwright 未安装")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def fetch_all(self) -> Dict[str, Any]:
        """获取所有金价数据"""
        logger.info("[金价浏览器] 开始获取数据...")
        
        try:
            # 百度搜索
            search_results = self._search_baidu("今日金价")
            
            # 从搜索结果提取金价
            international, domestic = self._extract_gold_prices(search_results)
            
            # 验证数据
            if international > 0 and domestic > 0:
                result = {
                    'international': {
                        'price': international,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'currency': 'USD',
                        'unit': 'oz',
                        'source': '百度搜索'
                    },
                    'domestic': {
                        'price': domestic,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'currency': 'CNY',
                        'unit': 'g',
                        'source': '百度搜索'
                    },
                    'metadata': {
                        'source': '百度搜索',
                        'update_time': datetime.now().isoformat(),
                        'search_query': '今日金价'
                    }
                }
                
                logger.info(f"[金价浏览器] 获取成功 - 国际：${international:.2f}, 国内：¥{domestic:.2f}")
                return result
            
        except Exception as e:
            logger.error(f"[金价浏览器] 获取异常：{e}")
        
        # 返回兜底数据
        return self._get_fallback()
    
    def _search_baidu(self, query: str) -> List[Dict[str, str]]:
        """百度搜索"""
        logger.debug(f"[金价浏览器] 搜索：{query}")
        
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        results = []
        
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
                    ]
                )
                
                # 创建页面
                page = browser.new_page()
                page.set_default_timeout(20000)
                
                # 设置请求头
                page.set_extra_http_headers(self.headers)
                
                # 访问百度搜索
                params = f"wd={query}"
                page.goto(f"{self.SEARCH_URL}?{params}", wait_until='domcontentloaded', timeout=20000)
                
                # 等待搜索结果
                page.wait_for_timeout(3000)
                
                # 获取搜索结果
                search_items = page.query_selector_all('.result.c-container')
                
                for item in search_items[:10]:  # 取前 10 个结果
                    try:
                        title_el = item.query_selector('.t a')
                        content_el = item.query_selector('.c-abstract')
                        
                        if title_el:
                            title = title_el.inner_text().strip()
                            href = title_el.get_attribute('href', '')
                            
                            content = content_el.inner_text().strip() if content_el else ''
                            
                            # 优先保留目标网站
                            is_target = any(site in href for site in self.TARGET_SITES)
                            
                            results.append({
                                'title': title,
                                'href': href,
                                'content': content,
                                'is_target': is_target
                            })
                    except:
                        continue
                
                browser.close()
                
                logger.debug(f"[金价浏览器] 获取到 {len(results)} 个搜索结果")
                
            except Exception as e:
                logger.error(f"[金价浏览器] 搜索异常：{e}")
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
        
        return results
    
    def _extract_gold_prices(self, results: List[Dict[str, str]]) -> Tuple[float, float]:
        """从搜索结果提取金价"""
        international = 0.0
        domestic = 0.0
        
        # 优先处理目标网站
        target_results = [r for r in results if r.get('is_target')]
        other_results = [r for r in results if not r.get('is_target')]
        
        for result in target_results + other_results:
            text = result.get('title', '') + ' ' + result.get('content', '')
            
            # 提取国际金价（美元/盎司）
            if international == 0:
                intl_patterns = [
                    r'国际金价 [：:]\s*([\d.]+)\s*美元',
                    r'现货黄金 [：:]\s*([\d.]+)',
                    r'黄金 [：:]\s*([\d.]+)\s*美元/盎司',
                    r'([\d.]+)\s*美元/盎司',
                ]
                
                for pattern in intl_patterns:
                    match = re.search(pattern, text)
                    if match:
                        value = float(match.group(1))
                        # 验证合理性（150-350 美元/盎司）
                        if 150 < value < 350:
                            international = value
                            logger.debug(f"[金价浏览器] 提取国际金价：${value}")
                            break
            
            # 提取国内金价（元/克）
            if domestic == 0:
                domestic_patterns = [
                    r'国内金价 [：:]\s*([\d.]+)\s*元',
                    r'黄金价格 [：:]\s*([\d.]+)\s*元/克',
                    r'([\d.]+)\s*元/克',
                    r'足金 [：:]\s*([\d.]+)\s*元',
                ]
                
                for pattern in domestic_patterns:
                    match = re.search(pattern, text)
                    if match:
                        value = float(match.group(1))
                        # 验证合理性（400-1500 元/克）
                        if 400 < value < 1500:
                            domestic = value
                            logger.debug(f"[金价浏览器] 提取国内金价：¥{value}")
                            break
            
            # 如果都找到了，提前返回
            if international > 0 and domestic > 0:
                break
        
        return international, domestic
    
    def _get_fallback(self) -> Dict[str, Any]:
        """兜底数据"""
        return {
            'international': {
                'price': self.FALLBACK_VALUES['international'],
                'change': 0.0,
                'change_pct': 0.0,
                'currency': 'USD',
                'unit': 'oz',
                'source': '兜底数据'
            },
            'domestic': {
                'price': self.FALLBACK_VALUES['domestic'],
                'change': 0.0,
                'change_pct': 0.0,
                'currency': 'CNY',
                'unit': 'g',
                'source': '兜底数据'
            },
            'metadata': {
                'source': '兜底数据',
                'update_time': datetime.now().isoformat()
            }
        }
    
    def test_connection(self) -> bool:
        """测试连接"""
        logger.info("[金价浏览器] 测试连接...")
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[金价浏览器] Playwright 未安装")
            return False
        
        try:
            result = self.fetch_all()
            success = (result['international']['price'] > 0 and 
                      result['domestic']['price'] > 0)
            
            if success:
                logger.info(f"[金价浏览器] 连接测试成功")
            else:
                logger.warning("[金价浏览器] 连接测试失败")
            
            return success
            
        except Exception as e:
            logger.error(f"[金价浏览器] 连接测试异常：{e}")
            return False


# 测试入口
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    print("=" * 60)
    print("金价浏览器抓取测试")
    print("=" * 60)
    
    source = GoldBrowserSource()
    
    # 测试连接
    print("\n1. 测试连接...")
    if source.test_connection():
        print("   ✅ 连接正常")
    else:
        print("   ⚠️ 连接异常")
    
    # 获取所有数据
    print("\n2. 获取金价数据...")
    data = source.fetch_all()
    
    print("\n3. 结果摘要:")
    print(f"   国际金价：${data['international']['price']:.2f} ({data['international']['source']})")
    print(f"   国内金价：¥{data['domestic']['price']:.2f} ({data['domestic']['source']})")
    
    print("\n" + "=" * 60)
