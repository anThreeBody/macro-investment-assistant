#!/usr/bin/env python3
"""
宏观叙事分析器 - 实现政策→经济影响→资产价格的因果推理链

核心逻辑：
政策/事件 → 经济影响 → 资产价格 → 投资策略
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MacroNarrativeAnalyzer:
    """宏观叙事分析器"""
    
    # 政策类型映射
    POLICY_TYPES = {
        '货币政策': {
            'keywords': ['降准', '降息', 'MLF', 'LPR', '流动性', '央行', '利率'],
            'impact': {
                'gold': 'positive',      # 宽松货币政策利好黄金
                'bonds': 'positive',     # 利好债券
                'growth_stocks': 'positive',  # 利好成长股
                'usd': 'negative',       # 美元走弱
            }
        },
        '财政政策': {
            'keywords': ['财政', '基建', '专项债', '减税', '支出', '赤字'],
            'impact': {
                'infrastructure': 'positive',  # 基建相关
                'cyclical_stocks': 'positive', # 周期股
                'construction': 'positive',    # 建筑建材
            }
        },
        '产业政策': {
            'keywords': ['新质生产力', '科技创新', '半导体', 'AI', '新能源', '数字经济', '国产替代'],
            'impact': {
                'tech_stocks': 'positive',     # 科技股
                'semiconductor': 'positive',   # 半导体
                'new_energy': 'positive',      # 新能源
                'ai': 'positive',              # AI
            }
        },
        '监管政策': {
            'keywords': ['监管', '规范', '整治', '反垄断', '合规', '审查'],
            'impact': {
                'platform': 'negative',      # 平台经济
                'real_estate': 'negative',   # 房地产
                'education': 'negative',     # 教育
            }
        },
        '地缘政治': {
            'keywords': ['战争', '冲突', '制裁', '贸易摩擦', '台海', '南海'],
            'impact': {
                'gold': 'positive',      # 避险资产
                'oil': 'positive',       # 原油
                'defense': 'positive',   # 军工
                'emerging_markets': 'negative',  # 新兴市场
            }
        },
        '经济数据': {
            'keywords': ['GDP', 'CPI', 'PPI', 'PMI', '就业', '零售', '出口', '进口'],
            'impact': {
                'strong_data': 'positive',  # 数据好→经济好→股票好
                'weak_data': 'negative',    # 数据差→经济差→股票差
            }
        }
    }
    
    # 叙事强度评估
    NARRATIVE_STRENGTH = {
        'strong': {
            'keywords': ['重磅', '重大', '首次', '历史性', '突破', '超预期'],
            'weight': 1.0
        },
        'medium': {
            'keywords': ['持续', '进一步', '加强', '推进', '落实'],
            'weight': 0.6
        },
        'weak': {
            'keywords': ['提及', '表示', '关注', '研究'],
            'weight': 0.3
        }
    }
    
    def __init__(self):
        self.narrative_cache = {}
    
    def analyze(self, news_list: List[Dict], macro_data: Dict = None) -> Dict[str, Any]:
        """
        分析宏观叙事
        
        Args:
            news_list: 新闻列表
            macro_data: 宏观数据（可选）
            
        Returns:
            Dict[str, Any]: {
                'narratives': List[Dict],  # 识别的叙事
                'policy_impact': Dict,     # 政策影响评估
                'asset_implications': Dict, # 资产含义
                'investment_strategy': Dict # 投资策略建议
            }
        """
        logger.info("[宏观叙事] 开始分析...")
        
        # 1. 识别政策叙事
        narratives = self._identify_narratives(news_list)
        
        # 2. 评估政策影响
        policy_impact = self._assess_policy_impact(narratives)
        
        # 3. 推导资产含义
        asset_implications = self._derive_asset_implications(policy_impact, macro_data)
        
        # 4. 生成投资策略
        investment_strategy = self._generate_strategy(asset_implications)
        
        result = {
            'narratives': narratives,
            'policy_impact': policy_impact,
            'asset_implications': asset_implications,
            'investment_strategy': investment_strategy,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        logger.info(f"[宏观叙事] 识别到{len(narratives)}个叙事")
        return result
    
    def _identify_narratives(self, news_list: List[Dict]) -> List[Dict]:
        """识别政策叙事"""
        narratives = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            source = news.get('source', '')
            
            # 合并标题和内容
            text = f"{title} {content}"
            
            # 检测政策类型
            for policy_type, config in self.POLICY_TYPES.items():
                keywords = config['keywords']
                
                # 计算关键词匹配数
                match_count = sum(1 for kw in keywords if kw in text)
                
                if match_count >= 1:
                    # 检测叙事强度
                    strength = self._detect_strength(text)
                    
                    # 计算影响得分
                    impact_score = match_count * strength['weight']
                    
                    narrative = {
                        'type': policy_type,
                        'title': title,
                        'source': source,
                        'strength': strength['name'],
                        'impact_score': round(impact_score, 2),
                        'keywords_matched': [kw for kw in keywords if kw in text],
                        'publish_date': news.get('publish_date', ''),
                    }
                    
                    narratives.append(narrative)
        
        # 按影响得分排序
        narratives.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return narratives[:10]  # 返回 top 10
    
    def _detect_strength(self, text: str) -> Dict[str, Any]:
        """检测叙事强度"""
        for strength_name, config in self.NARRATIVE_STRENGTH.items():
            for keyword in config['keywords']:
                if keyword in text:
                    return {
                        'name': strength_name,
                        'weight': config['weight']
                    }
        
        return {'name': 'normal', 'weight': 0.5}
    
    def _assess_policy_impact(self, narratives: List[Dict]) -> Dict[str, Any]:
        """评估政策影响"""
        impact_summary = {
            'monetary': {'score': 0, 'direction': 'neutral', 'details': []},
            'fiscal': {'score': 0, 'direction': 'neutral', 'details': []},
            'industrial': {'score': 0, 'direction': 'neutral', 'details': []},
            'regulatory': {'score': 0, 'direction': 'neutral', 'details': []},
            'geopolitical': {'score': 0, 'direction': 'neutral', 'details': []},
        }
        
        for narrative in narratives:
            policy_type = narrative['type']
            score = narrative['impact_score']
            title = narrative['title']
            
            # 映射到影响类别
            if policy_type == '货币政策':
                impact_summary['monetary']['score'] += score
                impact_summary['monetary']['details'].append(title)
            elif policy_type == '财政政策':
                impact_summary['fiscal']['score'] += score
                impact_summary['fiscal']['details'].append(title)
            elif policy_type == '产业政策':
                impact_summary['industrial']['score'] += score
                impact_summary['industrial']['details'].append(title)
            elif policy_type == '监管政策':
                impact_summary['regulatory']['score'] += score
                impact_summary['regulatory']['details'].append(title)
            elif policy_type == '地缘政治':
                impact_summary['geopolitical']['score'] += score
                impact_summary['geopolitical']['details'].append(title)
        
        # 判断方向
        for category in impact_summary:
            score = impact_summary[category]['score']
            if score > 1.5:
                impact_summary[category]['direction'] = 'strong_positive'
            elif score > 0.5:
                impact_summary[category]['direction'] = 'positive'
            elif score < -1.5:
                impact_summary[category]['direction'] = 'strong_negative'
            elif score < -0.5:
                impact_summary[category]['direction'] = 'negative'
        
        return impact_summary
    
    def _derive_asset_implications(self, policy_impact: Dict, macro_data: Dict = None) -> Dict[str, Any]:
        """推导资产含义"""
        implications = {
            'gold': {'signal': 'neutral', 'confidence': 0, 'reasons': []},
            'stocks': {'signal': 'neutral', 'confidence': 0, 'reasons': []},
            'bonds': {'signal': 'neutral', 'confidence': 0, 'reasons': []},
            'usd': {'signal': 'neutral', 'confidence': 0, 'reasons': []},
            'oil': {'signal': 'neutral', 'confidence': 0, 'reasons': []},
        }
        
        # 货币政策影响
        monetary = policy_impact['monetary']
        if monetary['direction'] in ['positive', 'strong_positive']:
            implications['gold']['signal'] = 'bullish'
            implications['gold']['confidence'] += 0.3
            implications['gold']['reasons'].append('宽松货币政策利好黄金')
            implications['bonds']['signal'] = 'bullish'
            implications['bonds']['confidence'] += 0.3
            implications['bonds']['reasons'].append('宽松货币政策利好债券')
            implications['usd']['signal'] = 'bearish'
            implications['usd']['confidence'] += 0.2
            implications['usd']['reasons'].append('宽松货币政策美元走弱')
        
        # 财政政策影响
        fiscal = policy_impact['fiscal']
        if fiscal['direction'] in ['positive', 'strong_positive']:
            implications['stocks']['signal'] = 'bullish'
            implications['stocks']['confidence'] += 0.2
            implications['stocks']['reasons'].append('财政刺激利好股市')
        
        # 产业政策影响
        industrial = policy_impact['industrial']
        if industrial['direction'] in ['positive', 'strong_positive']:
            implications['stocks']['signal'] = 'bullish'
            implications['stocks']['confidence'] += 0.3
            implications['stocks']['reasons'].append('产业政策支持特定行业')
        
        # 地缘政治影响
        geopolitical = policy_impact['geopolitical']
        if geopolitical['direction'] in ['positive', 'strong_positive']:
            implications['gold']['signal'] = 'bullish'
            implications['gold']['confidence'] += 0.4
            implications['gold']['reasons'].append('地缘政治风险提升避险需求')
            implications['oil']['signal'] = 'bullish'
            implications['oil']['confidence'] += 0.3
            implications['oil']['reasons'].append('地缘政治风险推高油价')
        
        # 限制置信度在 0-1 之间
        for asset in implications:
            implications[asset]['confidence'] = min(1.0, implications[asset]['confidence'])
        
        return implications
    
    def _generate_strategy(self, asset_implications: Dict) -> Dict[str, Any]:
        """生成投资策略"""
        strategy = {
            'overall': 'neutral',
            'asset_allocation': {},
            'key_themes': [],
            'risks': [],
        }
        
        # 统计信号
        bullish_count = 0
        bearish_count = 0
        
        for asset, impl in asset_implications.items():
            if impl['signal'] == 'bullish':
                bullish_count += 1
                if impl['confidence'] > 0.3:
                    strategy['asset_allocation'][asset] = 'overweight'
                    strategy['key_themes'].extend(impl['reasons'])
            elif impl['signal'] == 'bearish':
                bearish_count += 1
                if impl['confidence'] > 0.3:
                    strategy['asset_allocation'][asset] = 'underweight'
                    strategy['risks'].extend(impl['reasons'])
            else:
                strategy['asset_allocation'][asset] = 'neutral'
        
        # 判断整体策略
        if bullish_count > bearish_count + 2:
            strategy['overall'] = 'risk_on'
        elif bearish_count > bullish_count + 2:
            strategy['overall'] = 'risk_off'
        else:
            strategy['overall'] = 'neutral'
        
        # 去重
        strategy['key_themes'] = list(set(strategy['key_themes']))[:5]
        strategy['risks'] = list(set(strategy['risks']))[:5]
        
        return strategy
    
    def to_brief_section(self, analysis_result: Dict) -> str:
        """生成简报章节"""
        narratives = analysis_result.get('narratives', [])
        asset_implications = analysis_result.get('asset_implications', {})
        strategy = analysis_result.get('investment_strategy', {})
        
        sections = []
        sections.append("## 📰 宏观叙事分析")
        sections.append("")
        
        # 叙事识别
        if narratives:
            sections.append("### 识别到的政策叙事")
            sections.append("")
            for i, narrative in enumerate(narratives[:5], 1):
                sections.append(f"{i}. **{narrative['title']}**")
                sections.append(f"   - 类型：{narrative['type']}")
                sections.append(f"   - 强度：{narrative['strength']}")
                sections.append(f"   - 来源：{narrative['source']}")
                sections.append("")
        
        # 资产含义
        sections.append("### 资产含义推导")
        sections.append("")
        sections.append("| 资产 | 信号 | 置信度 | 主要理由 |")
        sections.append("|------|------|--------|----------|")
        
        asset_names = {
            'gold': '黄金',
            'stocks': '股票',
            'bonds': '债券',
            'usd': '美元',
            'oil': '原油'
        }
        
        signal_icons = {
            'bullish': '🟢 看多',
            'bearish': '🔴 看空',
            'neutral': '⚪ 中性'
        }
        
        for asset_key, asset_name in asset_names.items():
            impl = asset_implications.get(asset_key, {})
            signal = impl.get('signal', 'neutral')
            confidence = impl.get('confidence', 0)
            reasons = impl.get('reasons', ['无明确信号'])
            
            signal_text = signal_icons.get(signal, '⚪ 中性')
            confidence_text = f"{confidence*100:.0f}%"
            reason_text = reasons[0] if reasons else '无明确信号'
            
            sections.append(f"| {asset_name} | {signal_text} | {confidence_text} | {reason_text} |")
        
        sections.append("")
        
        # 投资策略
        sections.append("### 投资策略建议")
        sections.append("")
        overall_strategy = {
            'risk_on': '🟢 偏多配置',
            'risk_off': '🔴 偏空配置',
            'neutral': '⚪ 均衡配置'
        }
        sections.append(f"**整体策略**: {overall_strategy.get(strategy.get('overall', 'neutral'), '⚪ 均衡配置')}")
        sections.append("")
        
        if strategy.get('key_themes'):
            sections.append("**核心主题**:")
            for theme in strategy['key_themes']:
                sections.append(f"- {theme}")
            sections.append("")
        
        if strategy.get('risks'):
            sections.append("**风险提示**:")
            for risk in strategy['risks']:
                sections.append(f"- {risk}")
            sections.append("")
        
        return '\n'.join(sections)


if __name__ == '__main__':
    # 测试
    analyzer = MacroNarrativeAnalyzer()
    
    # 测试新闻
    test_news = [
        {
            'title': '央行宣布降准 0.25 个百分点，释放长期资金约 5000 亿元',
            'content': '中国人民银行今日宣布...',
            'source': '腾讯新闻',
            'publish_date': '2026-04-08'
        },
        {
            'title': '两会强调新质生产力，科技创新获得政策支持',
            'content': '政府工作报告提出...',
            'source': '百度新闻',
            'publish_date': '2026-04-08'
        }
    ]
    
    result = analyzer.analyze(test_news)
    print(analyzer.to_brief_section(result))
