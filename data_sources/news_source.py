#!/usr/bin/env python3
"""
新闻数据源 - 从多源获取财经新闻（优化版）

支持：
- 腾讯新闻（百度搜索 site:qq.com）
- 百度新闻
- 东方财富（浏览器抓取）
- 和讯财经（浏览器抓取）
- 新浪财经（浏览器抓取）
- 本地缓存（读写）

优化：
- 确保每个来源至少有 2 条新闻
- 自动保存到本地缓存
- 来源多样性优先
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsDataSource(DataSource):
    """新闻数据源"""
    
    def __init__(self):
        config = DataSourceConfig(
            name='多源聚合',
            source_type='news',
            cache_enabled=True,
            cache_ttl=3600,  # 新闻缓存 1 小时
            retry_times=3,
            timeout=30,
        )
        super().__init__(config)
        
        self.data_dir = Path(__file__).parent.parent / "data"
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存文件路径
        self.cache_file = self.data_dir / "news_cache.json"
    
    def fetch(self, days: int = 1, categories: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        获取财经新闻（多源聚合，确保来源多样性）
        
        Args:
            days: 获取最近 N 天的新闻
            categories: 新闻类别（如：['宏观', '政策', '市场']）
            
        Returns:
            Dict[str, Any]: {
                'news': List[Dict],  # 新闻列表
                'count': int,  # 新闻总数
                'sources': List[str],  # 数据来源
                'metadata': {...}
            }
        """
        logger.info(f"[多源聚合] 获取最近{days}天财经新闻...")
        
        all_news = []
        sources = []
        
        # 策略：并行获取多个来源，确保多样性
        # 1. 本地缓存（快速）
        local_news = self._fetch_local_news(days)
        if local_news:
            all_news.extend(local_news)
            sources.append('本地缓存')
            logger.info(f"[本地缓存] 获取到{len(local_news)}条新闻")
        
        # 2. 腾讯新闻（百度搜索）
        qq_news = self._fetch_tencent_news(days)
        if qq_news:
            all_news.extend(qq_news)
            sources.append('腾讯新闻')
            logger.info(f"[腾讯新闻] 获取到{len(qq_news)}条新闻")
        
        # 3. 百度新闻
        baidu_news = self._fetch_baidu_news(days)
        if baidu_news:
            all_news.extend(baidu_news)
            sources.append('百度搜索')
            logger.info(f"[百度搜索] 获取到{len(baidu_news)}条新闻")
        
        # 4. 浏览器抓取（东方财富、和讯、新浪）
        browser_news = self._fetch_browser_news(days)
        if browser_news:
            all_news.extend(browser_news)
            sources.append('浏览器抓取')
            logger.info(f"[浏览器抓取] 获取到{len(browser_news)}条新闻")
        
        # 去重
        seen_urls = set()
        unique_news = []
        for news in all_news:
            url = news.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(news)
        
        logger.info(f"[去重后] 剩余{len(unique_news)}条唯一新闻")
        
        # 按来源多样性优化（确保每个来源至少有 2 条）
        optimized_news = self._optimize_source_diversity(unique_news)
        
        # 保存到缓存
        self._save_to_cache(optimized_news)
        
        result = {
            'news': optimized_news[:20],  # 最多 20 条
            'count': len(optimized_news),
            'sources': list(set(sources)),  # 去重来源列表
            'date_range': {
                'start': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d'),
            },
            'metadata': self.get_standard_metadata()
        }
        
        logger.info(f"[多源聚合] 获取到{result['count']}条新闻，来源：{result['sources']}")
        return result
    
    def _optimize_source_diversity(self, news_list: List[Dict]) -> List[Dict]:
        """
        优化来源多样性
        
        策略：
        1. 按来源分组
        2. 过滤低质量新闻（首页链接、导航页）
        3. 每个来源至少取 2 条
        4. 如果某来源不足 2 条，从其他来源补充
        5. 最终按时间排序
        """
        if not news_list:
            return []
        
        # 过滤低质量新闻
        filtered_news = []
        for news in news_list:
            title = news.get('title', '')
            url = news.get('url', '')
            
            # 过滤首页链接
            if self._is_homepage_link(url, title):
                logger.debug(f"[过滤] 首页链接：{title}")
                continue
            
            # 过滤标题过短或过长
            if len(title) < 10 or len(title) > 60:
                logger.debug(f"[过滤] 标题长度不合适：{title}")
                continue
            
            # 过滤广告性质标题
            if any(kw in title for kw in ['首页', '专题', '汇总', '微博', 'CCTV']):
                logger.debug(f"[过滤] 广告性质：{title}")
                continue
            
            filtered_news.append(news)
        
        logger.info(f"[过滤后] 剩余{len(filtered_news)}条新闻")
        
        # 按来源分组
        by_source = {}
        for news in filtered_news:
            source = news.get('source', '未知')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(news)
        
        logger.info(f"[来源分布] {[(k, len(v)) for k, v in by_source.items()]}")
        
        # 每个来源至少取 2 条，最多 5 条
        result = []
        for source, items in by_source.items():
            count = min(len(items), 5)  # 每个来源最多 5 条
            count = max(count, 2) if len(items) >= 2 else len(items)  # 至少 2 条（如果有）
            result.extend(items[:count])
        
        # 如果总数不足 10 条，保留所有过滤后的
        if len(result) < 10:
            result = filtered_news[:20]
        
        # 按发布时间排序（最新的在前）
        result.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
        
        logger.info(f"[优化后] {len(result)}条新闻，来源数：{len(by_source)}")
        return result
    
    def _is_homepage_link(self, url: str, title: str) -> bool:
        """判断是否为首页链接"""
        if not url:
            return False
        
        # 首页特征
        homepage_keywords = [
            '首页', 'home', 'index', 'www.',
            '财经首页', '全球财经', '专题汇总'
        ]
        
        # 检查 URL 是否简短（可能是首页）
        if url.count('/') <= 3:
            return True
        
        # 检查标题是否包含首页关键词
        for kw in homepage_keywords:
            if kw in title.lower():
                return True
        
        return False
    
    def _save_to_cache(self, news_list: List[Dict]) -> None:
        """保存到本地缓存"""
        try:
            cache_data = {
                'news': news_list,
                'updated_at': datetime.now().isoformat(),
                'count': len(news_list)
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[缓存保存] 已保存{len(news_list)}条新闻到 {self.cache_file}")
        except Exception as e:
            logger.warning(f"[缓存保存] 失败：{e}")
    
    def _fetch_tencent_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """获取腾讯财经新闻（通过浏览器直接访问腾讯新闻）"""
        logger.info("[腾讯新闻] 获取财经新闻...")
        
        all_news = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(15000)
            
            # 腾讯财经
            url = "https://finance.qq.com/"
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
                page.wait_for_timeout(2000)
                
                # 获取所有链接
                links = page.query_selector_all("a")
                
                for link in links[:30]:
                    try:
                        title = link.inner_text().strip()
                        href = link.get_attribute('href')
                        
                        # 过滤：标题长度合适，且包含财经相关关键词
                        if title and 10 < len(title) < 50:
                            if any(kw in title for kw in ['财经', '经济', '市场', '股票', '基金', '黄金']):
                                full_url = href if href and href.startswith('http') else None
                                if full_url:
                                    news_item = {
                                        'title': title,
                                        'url': full_url,
                                        'source': '腾讯新闻',
                                        'publish_date': datetime.now().strftime('%Y-%m-%d'),
                                        'content': title[:200],
                                        'sentiment': self._analyze_sentiment(title)
                                    }
                                    all_news.append(news_item)
                    except:
                        continue
                
                # 最多取 5 条
                all_news = all_news[:5]
                logger.info(f"[腾讯新闻] 获取到{len(all_news)}条新闻")
                
            except Exception as e:
                logger.warning(f"[腾讯新闻] 抓取失败：{e}")
            
            browser.close()
            playwright.stop()
            
        except Exception as e:
            logger.error(f"[腾讯新闻] 获取失败：{e}")
        
        return all_news
    
    def _fetch_baidu_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """通过浏览器百度搜索获取财经新闻"""
        logger.info("[百度搜索] 获取财经新闻...")
        
        all_news = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(15000)
            
            # 百度搜索财经新闻
            search_url = "https://www.baidu.com/s?wd=财经新闻+最新"
            
            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=10000)
                page.wait_for_timeout(2000)
                
                # 获取搜索结果
                results = page.query_selector_all(".result.c-container")
                
                for result in results[:10]:
                    try:
                        title_elem = result.query_selector("h3 a")
                        if title_elem:
                            title = title_elem.inner_text().strip()
                            href = title_elem.get_attribute('href')
                            
                            if title and len(title) > 8 and href:
                                news_item = {
                                    'title': title,
                                    'url': href,
                                    'source': '百度搜索',
                                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                                    'content': title[:200],
                                    'sentiment': self._analyze_sentiment(title)
                                }
                                all_news.append(news_item)
                    except:
                        continue
                
                # 最多取 5 条
                all_news = all_news[:5]
                logger.info(f"[百度搜索] 获取到{len(all_news)}条新闻")
                
            except Exception as e:
                logger.warning(f"[百度搜索] 抓取失败：{e}")
            
            browser.close()
            playwright.stop()
            
        except Exception as e:
            logger.error(f"[百度搜索] 获取失败：{e}")
        
        return all_news
    
    def _fetch_local_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """从本地缓存读取新闻"""
        try:
            if not self.cache_file.exists():
                logger.debug("[本地缓存] 缓存文件不存在")
                return []
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cached_news = cache_data.get('news', [])
            if not cached_news:
                return []
            
            # 过滤日期
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_news = []
            
            for news in cached_news:
                pub_date = news.get('publish_date', '')
                if pub_date:
                    try:
                        news_date = datetime.strptime(pub_date, '%Y-%m-%d')
                        if news_date >= cutoff_date:
                            filtered_news.append(news)
                    except:
                        filtered_news.append(news)  # 日期解析失败也保留
            
            logger.info(f"[本地缓存] 获取到{len(filtered_news)}条新闻")
            return filtered_news
            
        except Exception as e:
            logger.error(f"[本地缓存] 读取失败：{e}")
            return []
    
    def _fetch_browser_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """通过浏览器抓取财经新闻（东方财富、和讯、新浪）"""
        logger.info("[浏览器] 抓取财经新闻...")
        
        all_news = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(15000)
            
            # 新闻网站（每个网站独立抓取）
            news_sites = [
                ("东方财富", "https://news.eastmoney.com/"),
                ("和讯财经", "http://www.hexun.com/"),
                ("新浪财经", "https://finance.sina.com.cn/"),
            ]
            
            for site_name, url in news_sites:
                site_news = []  # 每个网站独立收集
                logger.info(f"[浏览器] 抓取 {site_name}...")
                
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=10000)
                    page.wait_for_timeout(2000)
                    
                    # 获取所有链接
                    links = page.query_selector_all("a[href*='news']")
                    
                    for link in links[:20]:  # 每个网站最多检查 20 个链接
                        try:
                            title = link.inner_text().strip()
                            href = link.get_attribute('href')
                            
                            if title and len(title) > 8 and href:
                                full_url = href if href.startswith('http') else f"https://{url.split('/')[2]}{href}"
                                
                                news_item = {
                                    'title': title,
                                    'url': full_url,
                                    'source': site_name,
                                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                                    'content': title[:200],
                                    'sentiment': self._analyze_sentiment(title)
                                }
                                site_news.append(news_item)
                        except:
                            continue
                    
                    # 每个网站至少取 3 条（如果有）
                    site_news = site_news[:5]  # 每个网站最多 5 条
                    all_news.extend(site_news)
                    logger.info(f"[浏览器] {site_name} 获取到{len(site_news)}条新闻")
                    
                except Exception as e:
                    logger.warning(f"[浏览器] 抓取{site_name}失败：{e}")
                    continue
            
            browser.close()
            playwright.stop()
            
        except Exception as e:
            logger.error(f"[浏览器] 抓取失败：{e}")
        
        return all_news
    
    def _analyze_sentiment(self, text: str) -> float:
        """简单情绪分析"""
        positive_keywords = ['上涨', '利好', '增长', '突破', '创新高', '复苏', '回暖', '牛市']
        negative_keywords = ['下跌', '利空', '下滑', '暴跌', '风险', '衰退', '亏损', '熊市']
        
        score = 0
        for kw in positive_keywords:
            if kw in text:
                score += 0.2
        for kw in negative_keywords:
            if kw in text:
                score -= 0.2
        
        return max(-1, min(1, score))
    
    def fetch_sentiment(self, news_list: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """获取新闻情绪分析"""
        if not news_list:
            # 如果没有传入新闻列表，先获取
            result = self.fetch(days=1)
            news_list = result.get('news', [])
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            text = f"{title} {content}"
            
            score = self._analyze_sentiment(text)
            total_score += score
            
            if score > 0.1:
                positive_count += 1
            elif score < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        avg_score = total_score / len(news_list) if news_list else 0
        
        # 生成解读
        if avg_score > 0.2:
            interpretation = "市场情绪偏正面，主要受政策利好驱动"
        elif avg_score < -0.2:
            interpretation = "市场情绪偏负面，需谨慎观望"
        else:
            interpretation = "市场情绪中性，观望为主"
        
        return {
            'score': round(avg_score, 3),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'interpretation': interpretation,
        }
    
    def get_latest_headlines(self, limit: int = 10) -> List[str]:
        """获取最新头条"""
        result = self.fetch(days=1)
        news_list = result.get('news', [])
        return [news.get('title', '') for news in news_list[:limit]]


if __name__ == '__main__':
    # 测试
    source = NewsDataSource()
    result = source.fetch(days=1)
    
    print(f"\n{'='*60}")
    print(f"获取到 {result['count']} 条新闻")
    print(f"数据来源：{result['sources']}")
    print(f"{'='*60}")
    
    # 按来源分组显示
    by_source = {}
    for news in result['news']:
        src = news.get('source', '未知')
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(news)
    
    for src, items in by_source.items():
        print(f"\n【{src}】 ({len(items)}条)")
        for i, news in enumerate(items[:3], 1):
            print(f"  {i}. {news['title']}")
    
    print(f"\n{'='*60}")
