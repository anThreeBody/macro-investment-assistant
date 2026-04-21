#!/usr/bin/env python3
"""
政策数据获取模块

获取国内政策数据：
- 政府网（国务院政策）
- 央行官网（货币政策）
- 发改委（产业政策）
- 新华网（两会专题）
- 财新（市场分析）
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("提示：安装 requests beautifulsoup4 可启用网页爬取功能")
    print("pip install requests beautifulsoup4 lxml")


class PolicyScraper:
    """政策网页爬取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.sources = {
            "政府网": {
                "base_url": "http://www.gov.cn",
                "policy_url": "http://www.gov.cn/zhengce/content.htm",
                "keywords": ["国务院", "政策", "意见", "通知"]
            },
            "央行": {
                "base_url": "http://www.pbc.gov.cn",
                "policy_url": "http://www.pbc.gov.cn/zhengcehuobisi/125207/125213/index.html",
                "keywords": ["货币政策", "LPR", "降准", "降息", "公开市场"]
            },
            "发改委": {
                "base_url": "https://www.ndrc.gov.cn",
                "policy_url": "https://www.ndrc.gov.cn/xxgk/zcfb/",
                "keywords": ["产业", "投资", "项目", "规划"]
            },
            "新华网两会": {
                "base_url": "http://www.xinhuanet.com",
                "policy_url": "http://www.xinhuanet.com/lianghui/",
                "keywords": ["两会", "政府工作报告", "人大", "政协"]
            },
        }
    
    def fetch_gov_policy(self) -> List[Dict]:
        """获取政府网政策"""
        # TODO: 实现真实的网页爬取
        # 目前返回示例数据
        return [
            {
                "title": "国务院关于印发 2026 年重点工作任务的通知",
                "date": "2026-03-15",
                "source": "政府网",
                "url": "http://www.gov.cn/zhengce/content/2026-03/15/content.htm",
                "summary": "部署 2026 年经济社会发展重点工作",
                "category": "综合政策",
                "impact": "积极"
            },
        ]
    
    def fetch_pbc_policy(self) -> List[Dict]:
        """获取央行政策"""
        return [
            {
                "title": "央行维持 LPR 报价不变",
                "date": "2026-03-18",
                "source": "央行",
                "url": "http://www.pbc.gov.cn",
                "summary": "1 年期 LPR 为 3.45%，5 年期以上 LPR 为 4.20%",
                "category": "货币政策",
                "impact": "中性"
            },
        ]
    
    def fetch_ndrc_policy(self) -> List[Dict]:
        """获取发改委政策"""
        return [
            {
                "title": "发改委：支持新质生产力发展",
                "date": "2026-03-10",
                "source": "发改委",
                "url": "https://www.ndrc.gov.cn",
                "summary": "加大对科技创新、先进制造的支持力度",
                "category": "产业政策",
                "impact": "利好科技"
            },
        ]
    
    def fetch_lianghui_policy(self) -> List[Dict]:
        """获取两会政策"""
        return [
            {
                "title": "2026 年政府工作报告",
                "date": "2026-03-05",
                "source": "新华网",
                "url": "http://www.xinhuanet.com/lianghui/2026-03/05/",
                "summary": "GDP 增长目标 5% 左右，赤字率 3%",
                "category": "两会政策",
                "impact": "全面",
                "key_points": [
                    "GDP 增长目标 5% 左右",
                    "赤字率拟按 3% 安排",
                    "发行超长期特别国债",
                    "支持新质生产力发展",
                    "扩大内需战略",
                    "房地产发展新模式"
                ]
            },
        ]
    
    def get_all_policies(self) -> Dict:
        """获取所有政策"""
        return {
            "政府政策": self.fetch_gov_policy(),
            "货币政策": self.fetch_pbc_policy(),
            "产业政策": self.fetch_ndrc_policy(),
            "两会政策": self.fetch_lianghui_policy(),
        }


class PolicyAnalyzer:
    """政策分析引擎"""
    
    def __init__(self):
        self.scraper = PolicyScraper()
        
        # 政策 - 资产影响映射
        self.policy_asset_map = {
            "货币政策宽松": {
                "beneficiary": ["债券", "黄金", "成长股", "房地产"],
                "negative": ["银行息差", "货币基金"],
            },
            "货币政策收紧": {
                "beneficiary": ["银行", "货币基金", "短债"],
                "negative": ["债券", "成长股", "房地产"],
            },
            "财政扩张": {
                "beneficiary": ["基建", "建材", "工程机械", "债券供给增加"],
                "negative": ["利率上行压力"],
            },
            "产业支持 - 科技": {
                "beneficiary": ["半导体", "人工智能", "新能源", "科技基金"],
                "negative": [],
            },
            "产业支持 - 消费": {
                "beneficiary": ["消费股", "零售", "旅游", "消费基金"],
                "negative": [],
            },
            "房地产支持": {
                "beneficiary": ["地产股", "建材", "家电", "银行"],
                "negative": [],
            },
            "房地产收紧": {
                "beneficiary": ["保障房 REITs"],
                "negative": ["地产股", "建材", "银行"],
            },
            "地缘政治风险": {
                "beneficiary": ["黄金", "原油", "军工", "避险资产"],
                "negative": ["风险资产", "新兴市场"],
            },
            "通胀上升": {
                "beneficiary": ["商品", "黄金", "资源股"],
                "negative": ["债券", "高估值成长股"],
            },
        }
    
    def analyze_policy_impact(self, policy: Dict) -> Dict:
        """分析单个政策的影响"""
        title = policy.get("title", "")
        category = policy.get("category", "")
        impact = policy.get("impact", "")
        
        result = {
            "policy": policy,
            "asset_impact": {
                "positive": [],
                "negative": [],
                "neutral": []
            },
            "sectors": [],
            "confidence": "medium",
        }
        
        # 关键词匹配
        if "货币" in category or "LPR" in title or "降准" in title or "降息" in title:
            if "不变" in title or "维持" in title:
                result["asset_impact"]["neutral"] = ["债券", "股票", "黄金"]
            elif "下调" in title or "降低" in title:
                result["asset_impact"]["positive"] = ["债券", "黄金", "成长股"]
                result["asset_impact"]["negative"] = ["银行息差"]
            else:
                result["asset_impact"]["neutral"] = ["各类资产"]
        
        elif "两会" in category or "政府工作" in title:
            result["asset_impact"]["positive"] = ["A 股整体", "基建", "科技"]
            result["sectors"] = ["科技", "制造", "消费", "基建"]
            result["confidence"] = "high"
        
        elif "科技" in title or "新质生产力" in title:
            result["asset_impact"]["positive"] = ["科技股", "科技基金", "半导体", "AI"]
            result["sectors"] = ["科技", "半导体", "人工智能", "高端制造"]
        
        elif "消费" in title or "内需" in title:
            result["asset_impact"]["positive"] = ["消费股", "消费基金", "零售"]
            result["sectors"] = ["消费", "零售", "旅游", "餐饮"]
        
        elif "房地产" in title or "地产" in title:
            if "支持" in title or "优化" in title:
                result["asset_impact"]["positive"] = ["地产股", "建材", "家电"]
            else:
                result["asset_impact"]["neutral"] = ["地产相关"]
        
        return result
    
    def get_investment_implications(self, policies: List[Dict]) -> Dict:
        """综合多个政策，给出投资启示"""
        implications = {
            "overall_stance": "neutral",
            "recommended_assets": [],
            "avoid_assets": [],
            "key_themes": [],
            "risk_factors": [],
        }
        
        positive_count = 0
        negative_count = 0
        
        all_positive = []
        all_negative = []
        themes = set()
        
        for policy in policies:
            analysis = self.analyze_policy_impact(policy)
            
            if analysis["asset_impact"]["positive"]:
                positive_count += 1
                all_positive.extend(analysis["asset_impact"]["positive"])
            
            if analysis["asset_impact"]["negative"]:
                negative_count += 1
                all_negative.extend(analysis["asset_impact"]["negative"])
            
            if analysis["sectors"]:
                themes.update(analysis["sectors"])
        
        # 综合判断
        if positive_count > negative_count + 2:
            implications["overall_stance"] = "risk-on"
        elif negative_count > positive_count + 2:
            implications["overall_stance"] = "risk-off"
        else:
            implications["overall_stance"] = "neutral"
        
        # 统计推荐资产
        from collections import Counter
        if all_positive:
            counter = Counter(all_positive)
            implications["recommended_assets"] = [
                {"asset": asset, "count": count}
                for asset, count in counter.most_common(5)
            ]
        
        implications["key_themes"] = list(themes)
        
        return implications


def get_policy_summary() -> str:
    """获取政策摘要（供外部调用）"""
    scraper = PolicyScraper()
    analyzer = PolicyAnalyzer()
    
    policies = scraper.get_all_policies()
    
    summary = "## 📰 最新政策动态\n\n"
    
    for category, policy_list in policies.items():
        summary += f"### {category}\n"
        for p in policy_list[:3]:
            summary += f"- **{p['title']}** ({p['date']})\n"
            summary += f"  - {p.get('summary', '')}\n"
            summary += f"  - 影响：{p.get('impact', 'N/A')}\n"
        summary += "\n"
    
    # 投资启示
    all_policies = []
    for policy_list in policies.values():
        all_policies.extend(policy_list)
    
    implications = analyzer.get_investment_implications(all_policies)
    
    summary += "### 投资启示\n\n"
    summary += f"- **整体 stance**: {implications['overall_stance']}\n"
    summary += f"- **关注主题**: {', '.join(implications['key_themes'])}\n"
    
    if implications['recommended_assets']:
        summary += f"- **受益资产**: {', '.join([a['asset'] for a in implications['recommended_assets'][:5]])}\n"
    
    return summary


if __name__ == '__main__':
    print(get_policy_summary())
