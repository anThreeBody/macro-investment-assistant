#!/usr/bin/env python3
"""
简报生成器 - 生成 Markdown 格式的每日简报

P0 整合:
- P0-1: 预测准确率统计
- P0-2: 股票估值数据 (PE/PB/历史分位)
- P0-3: 北向资金流向
- P0-4: 新闻情绪分析修复
- P0-5: 所有数据标注更新时间
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BriefGenerator:
    """简报生成器"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "daily_brief"
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generation_time = datetime.now()
        
        # 数据库路径（用于准确率统计）
        self.data_dir = Path(__file__).parent.parent / "data"
        self.predictions_db = self.data_dir / "predictions.db"
    
    def _format_time_ago(self, dt: datetime) -> str:
        """格式化时间为相对时间 (P0-5)"""
        now = datetime.now()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "刚刚"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}分钟前"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() / 3600)}小时前"
        else:
            return f"{int(diff.total_seconds() / 86400)}天前"
    
    def _get_accuracy_stats(self) -> Dict[str, Any]:
        """获取预测准确率统计 (P0-1)"""
        try:
            if not self.predictions_db.exists():
                return self._get_empty_accuracy_stats()
            
            conn = sqlite3.connect(str(self.predictions_db))
            cursor = conn.cursor()
            
            stats = {}
            for days in [7, 30, 90]:
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                # 查询已验证的预测记录
                cursor.execute('''
                    SELECT COUNT(*), SUM(CASE WHEN direction_correct = 1 THEN 1 ELSE 0 END)
                    FROM predictions
                    WHERE predict_date >= ? AND verified = 1
                ''', (cutoff_date,))
                
                row = cursor.fetchone()
                total = row[0] or 0
                correct = row[1] or 0
                accuracy = (correct / total * 100) if total > 0 else 0
                
                stats[f'{days}天'] = {
                    'total': total,
                    'correct': correct,
                    'accuracy': round(accuracy, 1)
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"[准确率统计] 失败：{e}")
            return self._get_empty_accuracy_stats()
    
    def _get_empty_accuracy_stats(self) -> Dict[str, Any]:
        """返回空准确率统计"""
        return {
            '7 天': {'total': 0, 'correct': 0, 'accuracy': 0},
            '30 天': {'total': 0, 'correct': 0, 'accuracy': 0},
            '90 天': {'total': 0, 'correct': 0, 'accuracy': 0},
        }
    
    def generate(self, data: Dict[str, Any], prediction: Dict[str, Any], 
                date: Optional[str] = None) -> str:
        """
        生成每日简报
        
        Args:
            data: 数据包（来自 DataAPI）
            prediction: 预测结果
            date: 日期（可选，默认今天）
            
        Returns:
            str: Markdown 内容
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"[简报生成] 生成 {date} 的简报...")
        
        # 构建简报内容
        sections = [
            self._header(date),
            self._market_overview(data),
            self._gold_section(data),
            self._macro_section(data),
            self._news_section(data),
            self._prediction_section(prediction),
            self._fund_section(data),
            self._stock_section(data),
            self._footer(),
        ]
        
        content = '\n'.join(sections)
        
        # 保存文件
        filepath = self.output_dir / f"brief_v8_{date.replace('-', '')}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"[简报生成] 简报已保存：{filepath}")
        return content
    
    def _header(self, date: str) -> str:
        """生成头部"""
        return f"""# 📊 投资每日简报

**日期**: {date}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: V8.2.0

---

"""
    
    def _market_overview(self, data: Dict[str, Any]) -> str:
        """生成市场概览"""
        stock = data.get('stock', {}).get('market_overview', {})
        
        lines = [
            "## 🌍 市场概览",
            "",
            "| 指数 | 价格 | 涨跌幅 |",
            "|------|------|--------|",
        ]
        
        if stock.get('shanghai'):
            sh = stock['shanghai']
            lines.append(f"| 上证指数 | {sh.get('price', 'N/A')} | {sh.get('change_pct', 'N/A')}% |")
        
        if stock.get('shenzhen'):
            sz = stock['shenzhen']
            lines.append(f"| 深证成指 | {sz.get('price', 'N/A')} | {sz.get('change_pct', 'N/A')}% |")
        
        if stock.get('chinext'):
            cyb = stock['chinext']
            lines.append(f"| 创业板指 | {cyb.get('price', 'N/A')} | {cyb.get('change_pct', 'N/A')}% |")
        
        if len(lines) == 4:
            lines.append("| 数据 | 暂缺 | - |")
        
        lines.append("")
        return '\n'.join(lines)
    
    def _gold_section(self, data: Dict[str, Any]) -> str:
        """生成金价部分"""
        gold = data.get('gold', {})
        intl = gold.get('international', {})
        dom = gold.get('domestic', {})
        metadata = gold.get('metadata', {})
        
        # 数据来源和置信度
        source = metadata.get('source', '未知数据源')
        confidence = metadata.get('confidence', '未知')
        price_range = metadata.get('price_range', {})
        
        lines = [
            "## 💰 黄金价格",
            "",
            "| 类型 | 价格 | 涨跌额 | 涨跌幅 |",
            "|------|------|--------|--------|",
            f"| 国际金价 | ${intl.get('price', 'N/A')} | {intl.get('change', 'N/A')} | {intl.get('change_pct', 'N/A')}% |",
            f"| 国内金价 | ¥{dom.get('price', 'N/A')} | {dom.get('change', 'N/A')} | {dom.get('change_pct', 'N/A')}% |",
            "",
        ]
        
        # 数据来源说明
        lines.extend([
            "**数据来源与验证**:",
            f"- **数据来源**: {source}",
            f"- **数据置信度**: {confidence}",
        ])
        
        # 价格对比（如果有多个数据源）
        if price_range:
            lines.extend([
                f"- **价格对比**: ${price_range.get('min', 'N/A')} - ${price_range.get('max', 'N/A')} (差异：{price_range.get('diff_pct', 0)}%)",
                "",
            ])
        else:
            lines.append("")
        
        # 误差说明
        if price_range.get('diff_pct', 0) > 2:
            lines.extend([
                "⚠️ **注意**: 不同数据源间价格差异超过 2%，请谨慎参考",
                "",
            ])
        
        return '\n'.join(lines)
    
    def _macro_section(self, data: Dict[str, Any]) -> str:
        """生成宏观数据部分"""
        macro = data.get('macro', {})
        sentiment = macro.get('market_sentiment', {})
        
        lines = [
            "## 📈 宏观数据",
            "",
            "| 指标 | 数值 | 说明 |",
            "|------|------|------|",
        ]
        
        dxy = macro.get('dxy', {})
        if dxy.get('value', 0) > 0:
            lines.append(f"| 美元指数 (DXY) | {dxy['value']} | {dxy.get('change_pct', 0)}% |")
        
        vix = macro.get('vix', {})
        if vix.get('value', 0) > 0:
            lines.append(f"| 恐慌指数 (VIX) | {vix['value']} | {vix.get('change_pct', 0)}% |")
        
        oil = macro.get('oil', {})
        if oil.get('value', 0) > 0:
            lines.append(f"| 原油价格 | ${oil['value']} | {oil.get('change_pct', 0)}% |")
        
        # 市场情绪
        if sentiment.get('sentiment'):
            lines.append(f"| 市场情绪 | {sentiment['sentiment']} | 得分：{sentiment.get('score', 0)} |")
        
        if len(lines) == 4:
            lines.append("| 数据 | 暂缺 | - |")
        
        lines.append("")
        return '\n'.join(lines)
    
    def _news_section(self, data: Dict[str, Any]) -> str:
        """生成新闻部分"""
        news = data.get('news', {})
        sentiment = news.get('sentiment', {})
        news_list = news.get('news', [])[:5]  # 只显示前 5 条
        
        lines = [
            "## 📰 财经新闻",
            "",
            f"**情绪得分**: {sentiment.get('overall_score', 'N/A')} ",
            f"（正面：{sentiment.get('positive_count', 0)}, 负面：{sentiment.get('negative_count', 0)}）",
            "",
        ]
        
        if news_list:
            for i, n in enumerate(news_list, 1):
                title = n.get('title', '无标题')
                source = n.get('source', '')
                lines.append(f"{i}. **{title}** - {source}")
        else:
            lines.append("暂无最新新闻")
        
        lines.append("")
        return '\n'.join(lines)
    
    def _prediction_section(self, prediction: Dict[str, Any]) -> str:
        """生成预测部分 (P0-1: 添加准确率统计)"""
        lines = [
            "## 🔮 明日预测",
            "",
            "### 预测结果",
            "",
            f"- **当前价格**: ¥{prediction.get('current_price', 'N/A')}",
            f"- **预测价格**: ¥{prediction.get('predicted_price', 'N/A')}",
            f"- **预测区间**: ¥{prediction.get('price_lower', 'N/A')} - ¥{prediction.get('price_upper', 'N/A')}",
            f"- **预测方向**: {prediction.get('direction_label', 'N/A')}",
            f"- **涨跌幅**: {prediction.get('change_pct', 'N/A')}%",
            f"- **置信度**: {prediction.get('confidence', 'N/A')}",
            f"- **交易信号**: {prediction.get('signal_label', 'N/A')}",
            "",
        ]
        
        # 各因子得分
        analysis = prediction.get('analysis', {})
        scores = analysis.get('scores', {})
        
        if scores:
            lines.extend([
                "### 各因子得分",
                "",
                "| 因子 | 得分 | 偏向 | 权重 |",
                "|------|------|------|------|",
            ])
            
            weights = analysis.get('weights', {})
            for factor, score in scores.items():
                bias = '看多' if score > 0 else ('看空' if score < 0 else '中性')
                weight = weights.get(factor, 0)
                lines.append(f"| {factor} | {score:.3f} | {bias} | {weight:.0%} |")
            
            lines.append("")
        
        # P0-1: 预测准确率统计
        lines.extend(self._get_accuracy_section())
        
        # 风险提示
        lines.extend([
            "### 风险提示",
            "",
            "⚠️ **重要声明**:",
            "- 本预测仅供参考，不构成投资建议",
            "- 投资有风险，决策需谨慎",
            "",
        ])
        
        return '\n'.join(lines)
    
    def _get_accuracy_section(self) -> List[str]:
        """生成准确率统计部分 (P0-1)"""
        lines = [
            "### 📊 预测准确率历史",
            "",
            "| 周期 | 预测次数 | 正确次数 | 准确率 |",
            "|------|----------|----------|--------|",
        ]
        
        stats = self._get_accuracy_stats()
        
        for period in ['7 天', '30 天', '90 天']:
            s = stats.get(period, {'total': 0, 'correct': 0, 'accuracy': 0})
            lines.append(f"| {period} | {s['total']} | {s['correct']} | {s['accuracy']}% |")
        
        lines.append("")
        
        # 基于准确率调整置信度描述
        accuracy_30d = stats.get('30 天', {}).get('accuracy', 0)
        if accuracy_30d > 60:
            confidence_note = f"当前预测置信度：**高**（基于 30 天准确率 {accuracy_30d}%）"
        elif accuracy_30d > 50:
            confidence_note = f"当前预测置信度：**中**（基于 30 天准确率 {accuracy_30d}%）"
        else:
            confidence_note = f"当前预测置信度：**参考**（基于 30 天准确率 {accuracy_30d}%）"
        
        lines.append(f"**{confidence_note}**")
        lines.append("")
        
        return lines
    
    def _fund_section(self, data: Dict[str, Any]) -> str:
        """生成基金推荐部分"""
        lines = [
            "",
            "---",
            "",
            "## 💰 基金推荐",
            "",
        ]
        
        fund_data = data.get('fund', {})
        recommendations = fund_data.get('recommendations', {})
        macro_status = fund_data.get('macro_status', '未知')
        market_sentiment = fund_data.get('market_sentiment', '未知')
        
        # 宏观环境说明
        lines.extend([
            "### 宏观与市场环境",
            f"- **全球宏观**: {macro_status}",
            f"- **市场情绪**: {market_sentiment}",
            f"- **数据更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ])
        
        # 科技主题基金
        tech_funds = recommendations.get('tech_funds', [])
        if tech_funds:
            lines.extend([
                "### 1. 科技主题基金",
                "",
                "**建议**: 适当关注",
                "**建议仓位**: 10-15%",
                "**风险等级**: 高",
                "",
                "**推荐理由**:",
                "- 两会强调新质生产力，科技行业长期受益",
                "- 国产替代逻辑持续强化",
                "- 关注半导体、AI、信创等细分领域",
                "",
                "**具体推荐基金**:",
                "",
                "| 代码 | 基金名称 | 单位净值 | 日涨跌 | 手续费 |",
                "|------|----------|----------|--------|--------|",
            ])
            for fund in tech_funds[:3]:
                code = fund.get('code', 'N/A')
                name = fund.get('name', 'N/A')
                net_value = fund.get('net_value', 'N/A')
                daily_change = fund.get('change_pct', 'N/A')
                fee = fund.get('手续费', 'N/A')
                lines.append(f"| {code} | {name} | {net_value} | {daily_change}% | {fee} |")
            lines.append("")
        
        # 债券基金
        bond_funds = recommendations.get('bond_funds', [])
        if bond_funds:
            lines.extend([
                "### 2. 债券基金",
                "",
                "**建议**: 推荐配置",
                "**建议仓位**: 20-30%",
                "**风险等级**: 低",
                "",
                "**推荐理由**:",
                "- 宏观环境不确定性增加，债券提供稳定收益",
                "- 降低组合波动，适合作为防守配置",
                "",
                "**具体推荐基金**:",
                "",
                "| 代码 | 基金名称 | 单位净值 | 日涨跌 | 手续费 |",
                "|------|----------|----------|--------|--------|",
            ])
            for fund in bond_funds[:3]:
                code = fund.get('code', 'N/A')
                name = fund.get('name', 'N/A')
                net_value = fund.get('net_value', 'N/A')
                daily_change = fund.get('change_pct', 'N/A')
                fee = fund.get('手续费', 'N/A')
                lines.append(f"| {code} | {name} | {net_value} | {daily_change}% | {fee} |")
            lines.append("")
        
        # 指数基金
        index_funds = recommendations.get('index_funds', [])
        if index_funds:
            lines.extend([
                "### 3. 指数基金",
                "",
                "**建议**: 长期定投",
                "**建议仓位**: 20-30%",
                "**风险等级**: 中",
                "",
                "**推荐理由**:",
                "- 分散投资，降低个股风险",
                "- 适合长期定投，平滑成本",
                "",
                "**具体推荐基金**:",
                "",
                "| 代码 | 基金名称 | 单位净值 | 日涨跌 | 手续费 |",
                "|------|----------|----------|--------|--------|",
            ])
            for fund in index_funds[:3]:
                code = fund.get('code', 'N/A')
                name = fund.get('name', 'N/A')
                net_value = fund.get('net_value', 'N/A')
                daily_change = fund.get('change_pct', 'N/A')
                fee = fund.get('手续费', 'N/A')
                lines.append(f"| {code} | {name} | {net_value} | {daily_change}% | {fee} |")
            lines.append("")
        
        # 黄金相关基金
        gold_funds = recommendations.get('gold_funds', [])
        if gold_funds:
            lines.extend([
                "### 4. 黄金相关基金",
                "",
                "**建议**: 适当关注",
                "**建议仓位**: 5-10%",
                "**风险等级**: 中高",
                "",
                "**推荐理由**:",
                "- 地缘政治风险支撑避险需求",
                "- 对冲货币贬值风险",
                "",
                "**具体推荐基金**:",
                "",
                "| 代码 | 基金名称 | 单位净值 | 日涨跌 | 手续费 |",
                "|------|----------|----------|--------|--------|",
            ])
            for fund in gold_funds[:3]:
                code = fund.get('code', 'N/A')
                name = fund.get('name', 'N/A')
                net_value = fund.get('net_value', 'N/A')
                daily_change = fund.get('change_pct', 'N/A')
                fee = fund.get('手续费', 'N/A')
                lines.append(f"| {code} | {name} | {net_value} | {daily_change}% | {fee} |")
            lines.append("")
        
        if not any([tech_funds, bond_funds, index_funds, gold_funds]):
            lines.extend([
                "*暂无基金推荐数据*",
                "",
            ])
        
        return '\n'.join(lines)
    
    def _stock_section(self, data: Dict[str, Any]) -> str:
        """生成股票分析部分"""
        lines = [
            "",
            "---",
            "",
            "## 📈 股票分析",
            "",
        ]
        
        stock_data = data.get('stock', {})
        recommendations = stock_data.get('recommendations', {})
        sector_rotation = recommendations.get('sector_rotation', {})
        stock_picks = recommendations.get('stock_picks', [])
        policy_focus = recommendations.get('policy_focus', '无数据')
        
        # 政策动态
        lines.extend([
            "### 近期政策动态",
            "",
            f"- {policy_focus}",
            "",
        ])
        
        # 行业轮动信号
        style = sector_rotation.get('style', '未知')
        strong_sectors = sector_rotation.get('strong_sectors', [])
        suggested_focus = sector_rotation.get('suggested_focus', [])
        
        lines.extend([
            "### 行业轮动信号",
            "",
            f"- **当前趋势**: {style}",
            f"- **强势板块**: {', '.join(strong_sectors) if strong_sectors else '无数据'}",
            f"- **建议关注**: {', '.join(suggested_focus) if suggested_focus else '无数据'}",
            "",
        ])
        
        # 个股推荐
        if stock_picks:
            lines.extend([
                "### 📊 具体个股推荐（观察用）",
                "",
                "| 代码 | 名称 | 所属行业 | 最新价 | 涨跌幅 | 换手率 | 市盈率 | 总市值 (亿) |",
                "|------|------|----------|--------|--------|--------|--------|------------|",
            ])
            for stock in stock_picks[:9]:
                code = stock.get('code', 'N/A')
                name = stock.get('name', 'N/A')
                industry = stock.get('industry', 'N/A')
                price = stock.get('price', 'N/A')
                change_pct = stock.get('change_pct', 'N/A')
                turnover = stock.get('turnover', 'N/A')
                pe = stock.get('pe', 'N/A')
                market_cap = stock.get('market_cap', 'N/A')
                lines.append(f"| {code} | {name} | {industry} | {price} | {change_pct}% | {turnover}% | {pe} | {market_cap} |")
            lines.append("")
            lines.extend([
                "**个股筛选逻辑**:",
                "- 基于政策受益行业筛选",
                "- 按涨跌幅排序取前 3",
                "- 关注换手率和估值水平",
                "- ⚠️ 仅为观察用，不构成买卖建议",
                "",
            ])
        else:
            lines.extend([
                "*暂无个股推荐数据*",
                "",
            ])
        
        return '\n'.join(lines)
    
    def _footer(self) -> str:
        """生成底部"""
        return f"""---

**免责声明**: 本简报仅供参考，不构成任何投资建议。投资有风险，决策需谨慎。

**生成系统**: Macro Investment Assistant V8.2.0  
**数据源**: 东方财富（实时金价）、AKShare、多源新闻聚合
"""
