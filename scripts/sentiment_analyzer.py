#!/usr/bin/env python3
"""
情绪分析模块 V1.0

Phase 3.2: 情绪分析
- 新闻情绪量化
- 情绪-价格关联分析
"""

import json
import sqlite3
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.policy_db = self.data_dir / "policies.db"
        
        # 加载情绪词典
        self.positive_words = self._load_sentiment_dict('positive')
        self.negative_words = self._load_sentiment_dict('negative')
        
        # 政策领域权重
        self.sector_weights = {
            '科技': 1.5,
            'AI': 1.5,
            '人工智能': 1.5,
            '新能源': 1.3,
            '芯片': 1.3,
            '半导体': 1.3,
            '环保': 1.2,
            '黄金': 1.2,
            '金融': 1.0,
            '房地产': 0.8,
            '基建': 1.0
        }
    
    def _load_sentiment_dict(self, sentiment: str) -> set:
        """加载情绪词典"""
        # 内置基础词典
        positive = {
            '利好', '支持', '促进', '发展', '增长', '上涨', '突破', '创新', '改革',
            '优化', '提升', '加强', '扩大', '稳定', '复苏', '繁荣', '利好', '积极',
            '看好', '推荐', '买入', '增持', '强劲', '超预期', '亮眼', '优异',
            '推动', '助力', '受益', '机遇', '优势', '领先', '成功', '达成',
            '降息', '宽松', '刺激', '扶持', '鼓励', '放开', '准入', '减税'
        }
        
        negative = {
            '利空', '限制', '收紧', '下降', '下跌', '跌破', '风险', '危机', '衰退',
            '萎缩', '下滑', '放缓', '承压', '拖累', '冲击', '波动', '震荡', '调整',
            '看空', '减持', '卖出', '回避', '疲软', '不及预期', '亏损', '下滑',
            '阻碍', '制约', '挑战', '困难', '问题', '担忧', '警惕', '防范',
            '加息', '紧缩', '抑制', '调控', '监管', '处罚', '违规', '暴雷'
        }
        
        return positive if sentiment == 'positive' else negative
    
    def load_recent_news(self, days: int = 3) -> List[Dict]:
        """加载最近新闻"""
        if not self.policy_db.exists():
            logger.error("政策数据库不存在")
            return []
        
        conn = sqlite3.connect(self.policy_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM policies
            WHERE date >= ?
            ORDER BY date DESC
        ''', (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析单条文本情绪
        
        Returns:
            {
                'score': -1.0 to 1.0,
                'positive_count': int,
                'negative_count': int,
                'sentiment': 'positive'/'negative'/'neutral'
            }
        """
        if not text:
            return {'score': 0, 'positive_count': 0, 'negative_count': 0, 'sentiment': 'neutral'}
        
        text = str(text)
        
        # 统计正负词
        pos_count = sum(1 for word in self.positive_words if word in text)
        neg_count = sum(1 for word in self.negative_words if word in text)
        
        # 计算得分
        total = pos_count + neg_count
        if total == 0:
            score = 0
        else:
            score = (pos_count - neg_count) / max(total, 1)
        
        # 判断情绪
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'score': round(score, 2),
            'positive_count': pos_count,
            'negative_count': neg_count,
            'sentiment': sentiment
        }
    
    def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """批量分析新闻情绪"""
        results = []
        
        for news in news_list:
            # 合并标题和内容
            text = f"{news.get('title', '')} {news.get('content', '')}"
            
            sentiment = self.analyze_sentiment(text)
            
            # 识别相关板块
            sectors = []
            for sector in self.sector_weights.keys():
                if sector in text:
                    sectors.append(sector)
            
            # 从impact字段提取影响分
            impact_str = news.get('impact', '中性')
            impact_score = 5
            if '高' in impact_str or '强' in impact_str:
                impact_score = 8
            elif '中' in impact_str:
                impact_score = 5
            elif '低' in impact_str:
                impact_score = 3
            
            results.append({
                'date': news.get('date'),
                'title': news.get('title', '')[:50],
                'sentiment_score': sentiment['score'],
                'sentiment': sentiment['sentiment'],
                'sectors': sectors,
                'impact_score': impact_score
            })
        
        return results
    
    def calculate_daily_sentiment(self, analyzed_news: List[Dict]) -> Dict:
        """计算每日情绪指数"""
        if not analyzed_news:
            return {'score': 0, 'trend': 'neutral'}
        
        # 按日期分组
        daily_scores = defaultdict(list)
        for news in analyzed_news:
            date = news.get('date', datetime.now().strftime('%Y-%m-%d'))
            # 加权：情绪分 * 影响分
            weighted_score = news['sentiment_score'] * (news.get('impact_score', 5) / 5)
            daily_scores[date].append(weighted_score)
        
        # 计算每日平均
        daily_avg = {}
        for date, scores in daily_scores.items():
            daily_avg[date] = sum(scores) / len(scores)
        
        # 总体情绪
        all_scores = [s for scores in daily_scores.values() for s in scores]
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # 趋势
        if overall_score > 0.2:
            trend = '乐观'
        elif overall_score < -0.2:
            trend = '悲观'
        else:
            trend = '中性'
        
        return {
            'score': round(overall_score, 2),
            'trend': trend,
            'daily_avg': {k: round(v, 2) for k, v in sorted(daily_avg.items())},
            'news_count': len(analyzed_news)
        }
    
    def sector_sentiment_analysis(self, analyzed_news: List[Dict]) -> Dict:
        """板块情绪分析"""
        sector_sentiments = defaultdict(list)
        
        for news in analyzed_news:
            for sector in news.get('sectors', []):
                weighted_score = news['sentiment_score'] * (news.get('impact_score', 5) / 5)
                sector_sentiments[sector].append(weighted_score)
        
        # 计算板块平均情绪
        result = {}
        for sector, scores in sector_sentiments.items():
            avg_score = sum(scores) / len(scores)
            weight = self.sector_weights.get(sector, 1.0)
            
            if avg_score > 0.2:
                sentiment = '利好'
            elif avg_score < -0.2:
                sentiment = '利空'
            else:
                sentiment = '中性'
            
            result[sector] = {
                'score': round(avg_score, 2),
                'sentiment': sentiment,
                'news_count': len(scores),
                'weight': weight
            }
        
        # 按情绪得分排序
        return dict(sorted(result.items(), key=lambda x: x[1]['score'], reverse=True))
    
    def generate_sentiment_report(self) -> str:
        """生成情绪分析报告"""
        report = "# 😊 市场情绪分析报告\n\n"
        report += f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**分析周期**: 最近3天\n\n"
        
        # 加载新闻
        news_list = self.load_recent_news(days=3)
        
        if not news_list:
            report += "⚠️ 暂无新闻数据\n\n"
            return report
        
        report += f"**新闻总数**: {len(news_list)} 条\n\n"
        
        # 分析情绪
        analyzed = self.analyze_news_batch(news_list)
        
        # 每日情绪
        daily_sentiment = self.calculate_daily_sentiment(analyzed)
        report += "## 📊 市场情绪指数\n\n"
        report += f"**综合得分**: {daily_sentiment['score']:.2f} (-1.0到+1.0)\n"
        report += f"**情绪趋势**: {daily_sentiment['trend']}\n"
        report += f"**分析新闻**: {daily_sentiment['news_count']} 条\n\n"
        
        if daily_sentiment['daily_avg']:
            report += "### 每日情绪变化\n\n"
            report += "| 日期 | 情绪得分 | 解读 |\n"
            report += "|------|----------|------|\n"
            for date, score in daily_sentiment['daily_avg'].items():
                if score > 0.2:
                    interpretation = "乐观"
                elif score < -0.2:
                    interpretation = "悲观"
                else:
                    interpretation = "中性"
                report += f"| {date} | {score:+.2f} | {interpretation} |\n"
            report += "\n"
        
        # 板块情绪
        sector_sentiment = self.sector_sentiment_analysis(analyzed)
        if sector_sentiment:
            report += "## 🏭 板块情绪排行\n\n"
            report += "| 板块 | 情绪得分 | 判断 | 相关新闻 |\n"
            report += "|------|----------|------|----------|\n"
            for sector, data in list(sector_sentiment.items())[:10]:
                emoji = "🟢" if data['sentiment'] == '利好' else "🔴" if data['sentiment'] == '利空' else "⚪"
                report += f"| {sector} | {data['score']:+.2f} | {emoji} {data['sentiment']} | {data['news_count']}条 |\n"
            report += "\n"
        
        # 重要新闻
        report += "## 📰 重要新闻情绪\n\n"
        report += "| 日期 | 标题 | 情绪 | 得分 |\n"
        report += "|------|------|------|------|\n"
        
        # 按影响分排序
        important_news = sorted(analyzed, key=lambda x: abs(x['sentiment_score']), reverse=True)[:10]
        for news in important_news:
            emoji = "🟢" if news['sentiment'] == 'positive' else "🔴" if news['sentiment'] == 'negative' else "⚪"
            title = news['title'][:30] + "..." if len(news['title']) > 30 else news['title']
            report += f"| {news['date']} | {title} | {emoji} | {news['sentiment_score']:+.2f} |\n"
        report += "\n"
        
        # 投资建议
        report += "## 💡 投资建议\n\n"
        
        overall = daily_sentiment['score']
        if overall > 0.3:
            report += "**情绪判断**: 市场过度乐观，需警惕回调风险\n\n"
            report += "- 建议: 逢高减仓，锁定利润\n"
            report += "- 关注: 获利盘抛压\n"
        elif overall > 0.1:
            report += "**情绪判断**: 市场情绪积极，趋势向好\n\n"
            report += "- 建议: 持有为主，精选个股\n"
            report += "- 关注: 政策受益板块\n"
        elif overall > -0.1:
            report += "**情绪判断**: 市场情绪中性，方向不明\n\n"
            report += "- 建议: 观望为主，控制仓位\n"
            report += "- 关注: 等待明确信号\n"
        elif overall > -0.3:
            report += "**情绪判断**: 市场情绪偏悲观，谨慎操作\n\n"
            report += "- 建议: 减仓避险，现金为王\n"
            report += "- 关注: 支撑位能否守住\n"
        else:
            report += "**情绪判断**: 市场过度悲观，或现反弹机会\n\n"
            report += "- 建议: 逢低布局优质资产\n"
            report += "- 关注: 超跌反弹机会\n"
        
        # 板块建议
        if sector_sentiment:
            top_positive = [k for k, v in sector_sentiment.items() if v['sentiment'] == '利好'][:3]
            top_negative = [k for k, v in sector_sentiment.items() if v['sentiment'] == '利空'][:3]
            
            if top_positive:
                report += f"\n**利好板块**: {', '.join(top_positive)}\n"
            if top_negative:
                report += f"**利空板块**: {', '.join(top_negative)}\n"
        
        report += "\n---\n\n"
        report += "**注意**: 情绪分析基于新闻文本，可能存在偏差\n"
        report += "**建议**: 结合技术分析和基本面综合判断\n"
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("😊 市场情绪分析系统")
    print("="*70)
    
    analyzer = SentimentAnalyzer()
    
    # 生成报告
    report = analyzer.generate_sentiment_report()
    
    print("\n" + report)
    
    # 保存报告
    report_dir = Path(__file__).parent.parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"sentiment_report_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_path}")


if __name__ == '__main__':
    main()
