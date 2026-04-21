#!/usr/bin/env python3
"""
数据 API - 统一数据访问接口

提供简洁的 API 供分析层调用
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources import (
    GoldDataSource,
    FundDataSource,
    StockDataSource,
    NewsDataSource,
    MacroDataSource,
)
from data_pipeline import DataCleaner, DataValidator, DataStorage
from analyzers.fund_recommender import FundRecommender, RiskProfile
from analyzers.stock_recommender import StockRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAPI:
    """统一数据 API"""
    
    def __init__(self):
        # 初始化数据源
        self.gold_source = GoldDataSource()
        self.fund_source = FundDataSource()
        self.stock_source = StockDataSource()
        self.news_source = NewsDataSource()
        self.macro_source = MacroDataSource()
        
        # 初始化数据管道
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.storage = DataStorage()
        
        # 初始化分析器
        self.fund_recommender = FundRecommender()
        self.stock_recommender = StockRecommender()
    
    # ==================== 金价数据 ====================
    
    def get_gold_price(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        获取金价数据
        
        Args:
            use_cache: 是否使用缓存
            
        Returns:
            Dict[str, Any]: 金价数据
        """
        if use_cache:
            raw_data = self.gold_source.fetch_with_cache()
        else:
            raw_data = self.gold_source.fetch()
        
        # 清洗
        cleaned = self.cleaner.clean(raw_data, 'gold')
        
        # 验证
        is_valid, errors = self.validator.validate(cleaned, 'gold')
        if not is_valid:
            logger.warning(f"金价数据验证失败：{errors}")
        
        return cleaned
    
    def get_gold_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取金价历史数据"""
        return self.gold_source.fetch_history(days)
    
    # ==================== 基金数据 ====================
    
    def get_fund(self, fund_code: str) -> Dict[str, Any]:
        """
        获取基金数据
        
        Args:
            fund_code: 基金代码
            
        Returns:
            Dict[str, Any]: 基金数据
        """
        raw_data = self.fund_source.fetch(fund_code)
        cleaned = self.cleaner.clean(raw_data, 'fund')
        
        is_valid, errors = self.validator.validate(cleaned, 'fund')
        if not is_valid:
            logger.warning(f"基金数据验证失败：{errors}")
        
        return cleaned
    
    def get_funds(self, fund_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取基金列表"""
        return self.fund_source.fetch_all(fund_type)
    
    def get_fund_history(self, fund_code: str, days: int = 90) -> List[Dict[str, Any]]:
        """获取基金历史净值"""
        return self.fund_source.fetch_history(fund_code, days)
    
    # ==================== 股票数据 ====================
    
    def get_stock(self, stock_code: str) -> Dict[str, Any]:
        """获取股票数据"""
        raw_data = self.stock_source.fetch(stock_code)
        cleaned = self.cleaner.clean(raw_data, 'stock')
        
        is_valid, errors = self.validator.validate(cleaned, 'stock')
        if not is_valid:
            logger.warning(f"股票数据验证失败：{errors}")
        
        return cleaned
    
    def get_stock_industry(self, industry_name: str) -> List[Dict[str, Any]]:
        """获取行业板块数据"""
        return self.stock_source.fetch_industry(industry_name)
    
    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        return self.stock_source.fetch_market_overview()
    
    def get_stock_history(self, stock_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取股票历史 K 线"""
        return self.stock_source.fetch_history(stock_code, start_date, end_date)
    
    # ==================== 新闻数据 ====================
    
    def get_news(self, days: int = 1, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取财经新闻"""
        raw_data = self.news_source.fetch(days, categories)
        cleaned = self.cleaner.clean(raw_data, 'news')
        
        is_valid, errors = self.validator.validate(cleaned, 'news')
        if not is_valid:
            logger.warning(f"新闻数据验证失败：{errors}")
        
        return cleaned
    
    def get_news_sentiment(self, news_list: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """获取新闻情绪分析"""
        return self.news_source.fetch_sentiment(news_list)
    
    def get_headlines(self, limit: int = 10) -> List[str]:
        """获取最新头条"""
        return self.news_source.get_latest_headlines(limit)
    
    # ==================== 宏观数据 ====================
    
    def get_macro(self, indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取宏观指标数据"""
        raw_data = self.macro_source.fetch(indicators)
        cleaned = self.cleaner.clean(raw_data, 'macro')
        
        is_valid, errors = self.validator.validate(cleaned, 'macro')
        if not is_valid:
            logger.warning(f"宏观数据验证失败：{errors}")
        
        return cleaned
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪"""
        return self.macro_source.get_market_sentiment()
    
    # ==================== 综合数据 ====================
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        获取所有数据（用于生成每日简报）
        
        Returns:
            Dict[str, Any]: 完整数据包
        """
        logger.info("[数据 API] 获取所有数据...")
        
        # 获取宏观和市场情绪（用于基金和股票推荐）
        macro = self.get_macro()
        market_sentiment = self.get_market_sentiment()
        news = self.get_news(days=1)
        
        # 添加情绪分析
        news_list = news.get('news', [])
        news['sentiment'] = self.get_news_sentiment(news_list)
        
        # 获取基金推荐
        fund_recommendations = self._get_fund_recommendations(macro, market_sentiment)
        
        # 获取股票推荐
        stock_recommendations = self._get_stock_recommendations(macro, market_sentiment, news)
        
        result = {
            'gold': self.get_gold_price(),
            'fund': fund_recommendations,
            'stock': {
                'market_overview': self.get_market_overview(),
                'recommendations': stock_recommendations,
            },
            'news': news,
            'macro': macro,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
        }
        
        result['macro']['market_sentiment'] = market_sentiment
        
        logger.info("[数据 API] 数据获取完成")
        return result
    
    def _get_fund_recommendations(self, macro: Dict, market_sentiment: Dict) -> Dict[str, Any]:
        """
        获取基金推荐
        
        Args:
            macro: 宏观数据
            market_sentiment: 市场情绪数据
            
        Returns:
            Dict[str, Any]: 基金推荐数据
        """
        try:
            # 获取所有基金
            all_funds = self.fund_source.fetch_all()
            if not all_funds:
                logger.warning("[基金推荐] 未获取到基金数据")
                return self._get_empty_fund_recommendations()
            
            # 根据宏观环境判断推荐倾向
            macro_status = macro.get('overall', 'neutral')
            
            # 推荐不同风险类型的基金
            recommendations = {
                'tech_funds': self._get_funds_by_category(all_funds, '科技', 3),
                'bond_funds': self._get_funds_by_category(all_funds, '债券', 3),
                'index_funds': self._get_funds_by_category(all_funds, '指数', 3),
                'gold_funds': self._get_funds_by_category(all_funds, '黄金', 3),
            }
            
            return {
                'recommendations': recommendations,
                'macro_status': macro_status,
                'market_sentiment': market_sentiment.get('overall', '中性'),
            }
        except Exception as e:
            logger.error(f"[基金推荐] 获取失败：{e}")
            return self._get_empty_fund_recommendations()
    
    def _get_funds_by_category(self, all_funds: List[Dict], category: str, limit: int = 3) -> List[Dict]:
        """按类别获取基金"""
        try:
            # 筛选包含关键词的基金（支持名称和类型）
            matched = [f for f in all_funds if category in f.get('name', '') or category in f.get('type', '')]
            # 按日涨跌幅排序（不过滤净值为 0 的，因为有些 QDII 可能净值更新延迟）
            matched.sort(key=lambda x: float(x.get('change_pct', 0) or 0), reverse=True)
            return matched[:limit]
        except Exception as e:
            logger.error(f"[基金筛选] {category} 失败：{e}")
            return []
    
    def _get_empty_fund_recommendations(self) -> Dict[str, Any]:
        """返回空的基金推荐结构"""
        return {
            'recommendations': {
                'tech_funds': [],
                'bond_funds': [],
                'index_funds': [],
                'gold_funds': [],
            },
            'macro_status': 'unknown',
            'market_sentiment': 'unknown',
        }
    
    def _get_stock_recommendations(self, macro: Dict, market_sentiment: Dict, news: Dict) -> Dict[str, Any]:
        """
        获取股票推荐
        
        Args:
            macro: 宏观数据
            market_sentiment: 市场情绪数据
            news: 新闻数据
            
        Returns:
            Dict[str, Any]: 股票推荐数据
        """
        try:
            # 获取行业轮动信号
            sector_rotation = self._get_sector_rotation(macro, market_sentiment)
            
            # 获取个股推荐（简化版，实际应该调用 stock_recommender）
            stock_picks = self._get_stock_picks(sector_rotation)
            
            return {
                'sector_rotation': sector_rotation,
                'stock_picks': stock_picks,
                'policy_focus': self._get_policy_focus(news),
            }
        except Exception as e:
            logger.error(f"[股票推荐] 获取失败：{e}")
            return self._get_empty_stock_recommendations()
    
    def _get_sector_rotation(self, macro: Dict, market_sentiment: Dict) -> Dict[str, Any]:
        """获取行业轮动信号"""
        # 基于宏观和市场情绪判断风格
        sentiment = market_sentiment.get('overall', '中性')
        
        if sentiment in ['乐观', '积极']:
            style = '成长风格占优'
            sectors = ['半导体', '人工智能', '新能源', '生物医药', '白酒']
        elif sentiment in ['悲观', '消极']:
            style = '防御风格占优'
            sectors = ['银行', '公用事业', '黄金', '医药', '消费']
        else:
            style = '平衡风格'
            sectors = ['科技', '新能源', '创新药', '消费', '金融']
        
        return {
            'style': style,
            'strong_sectors': sectors,
            'suggested_focus': sectors[:3] if sectors else [],
        }
    
    def _get_stock_picks(self, sector_rotation: Dict) -> List[Dict]:
        """获取个股推荐（示例数据）"""
        # 这里返回示例数据，实际应该从数据源获取
        sectors = sector_rotation.get('strong_sectors', [])
        
        # 示例股票池
        stock_pool = [
            {'code': '688981', 'name': '中芯国际', 'industry': '科技', 'price': 85.32, 'change_pct': 3.25, 'turnover': 2.1, 'pe': 65.8, 'market_cap': 6800},
            {'code': '000938', 'name': '紫光股份', 'industry': '科技', 'price': 45.68, 'change_pct': 2.89, 'turnover': 1.8, 'pe': 58.2, 'market_cap': 3600},
            {'code': '002371', 'name': '北方华创', 'industry': '科技', 'price': 298.5, 'change_pct': 4.12, 'turnover': 3.2, 'pe': 72.5, 'market_cap': 1580},
            {'code': '300750', 'name': '宁德时代', 'industry': '新能源', 'price': 198.6, 'change_pct': 2.15, 'turnover': 1.5, 'pe': 25.3, 'market_cap': 8700},
            {'code': '601012', 'name': '隆基绿能', 'industry': '新能源', 'price': 22.35, 'change_pct': 1.85, 'turnover': 2.8, 'pe': 18.6, 'market_cap': 1690},
            {'code': '002594', 'name': '比亚迪', 'industry': '新能源', 'price': 268.8, 'change_pct': 3.42, 'turnover': 2.1, 'pe': 32.8, 'market_cap': 7820},
            {'code': '000858', 'name': '五粮液', 'industry': '消费', 'price': 152.3, 'change_pct': 1.25, 'turnover': 0.8, 'pe': 22.5, 'market_cap': 5910},
            {'code': '600519', 'name': '贵州茅台', 'industry': '消费', 'price': 1680.0, 'change_pct': 0.85, 'turnover': 0.3, 'pe': 28.6, 'market_cap': 21100},
            {'code': '000333', 'name': '美的集团', 'industry': '消费', 'price': 68.5, 'change_pct': 1.12, 'turnover': 0.9, 'pe': 15.2, 'market_cap': 4780},
        ]
        
        # 根据行业轮动筛选
        focus_sectors = sector_rotation.get('suggested_focus', [])
        if focus_sectors:
            filtered = [s for s in stock_pool if any(fs in s['industry'] for fs in focus_sectors)]
            if filtered:
                return filtered[:9]
        
        return stock_pool[:9]
    
    def _get_policy_focus(self, news: Dict) -> str:
        """获取政策焦点"""
        # 简化实现
        return '近 7 天无明确政策指向'
    
    def _get_empty_stock_recommendations(self) -> Dict[str, Any]:
        """返回空的股票推荐结构"""
        return {
            'sector_rotation': {'style': '未知', 'strong_sectors': [], 'suggested_focus': []},
            'stock_picks': [],
            'policy_focus': '数据获取失败',
        }
    
    def save_snapshot(self, data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        保存数据快照
        
        Args:
            data: 数据
            filename: 文件名（可选）
            
        Returns:
            Path: 保存路径
        """
        if filename is None:
            from datetime import datetime
            filename = f"data_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return self.storage.save_json(data, filename)
    
    def close(self):
        """关闭所有连接"""
        self.storage.close_all()


# 便捷函数
def get_data_api() -> DataAPI:
    """获取数据 API 实例"""
    return DataAPI()


if __name__ == '__main__':
    # 测试
    api = DataAPI()
    
    print("=" * 50)
    print("数据 API 测试")
    print("=" * 50)
    
    # 测试金价
    print("\n📈 金价数据:")
    gold = api.get_gold_price()
    print(f"  国际：${gold['international']['price']}")
    print(f"  国内：¥{gold['domestic']['price']}")
    
    # 测试宏观
    print("\n🌍 宏观数据:")
    macro = api.get_macro()
    print(f"  DXY: {macro['dxy']['value']}")
    print(f"  VIX: {macro['vix']['value']}")
    
    # 测试新闻
    print("\n📰 新闻数据:")
    news = api.get_news(days=1)
    print(f"  新闻数：{news['count']}")
    print(f"  情绪得分：{news.get('sentiment', {}).get('overall_score', 'N/A')}")
    
    # 测试市场情绪
    print("\n📊 市场情绪:")
    sentiment = api.get_market_sentiment()
    print(f"  情绪：{sentiment['sentiment']}")
    print(f"  得分：{sentiment['score']}")
    
    api.close()
    
    print("\n✅ 测试完成")
