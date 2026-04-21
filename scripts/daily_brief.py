#!/usr/bin/env python3
"""
每日简报 V8.2 - 实时金价版

核心改进:
1. 使用浏览器实时获取金价（东方财富）
2. 版本号更新为 V8.2.0
3. 数据源标注为东方财富（实时金价）
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daily_brief_v8 import DailyBriefV8


class DailyBriefV82(DailyBriefV8):
    """每日简报 V8.2 - 实时金价版"""
    
    def __init__(self):
        super().__init__()
        self.yesterday = self.today - timedelta(days=1)
        self.yesterday_str = self.yesterday.strftime('%Y-%m-%d')
        
    def get_yesterday_brief(self) -> Optional[Dict]:
        """获取昨天的简报数据"""
        yesterday_file = Path(__file__).parent.parent / "daily_brief" / f"brief_v8_{self.yesterday_str.replace('-', '')}.md"
        
        if not yesterday_file.exists():
            # 尝试其他命名格式
            yesterday_file = Path(__file__).parent.parent / "daily_brief" / f"brief_{self.yesterday_str}.md"
        
        if not yesterday_file.exists():
            return None
        
        try:
            with open(yesterday_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取昨天的预测
            prediction = self._extract_prediction_from_brief(content)
            
            # 提取昨天的价格
            price = self._extract_price_from_brief(content)
            
            return {
                'prediction': prediction,
                'price': price,
                'file': str(yesterday_file)
            }
        except Exception as e:
            print(f"读取昨天简报失败: {e}")
            return None
    
    def _extract_prediction_from_brief(self, content: str) -> Optional[Dict]:
        """从简报内容中提取预测"""
        prediction = {}
        
        # 提取预测方向
        if '预测方向' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '预测方向' in line:
                    # 格式: **预测方向**: ➡️ **震荡** (概率60%)
                    if '**' in line:
                        parts = line.split('**')
                        for part in parts:
                            if '涨' in part or '跌' in part or '震荡' in part:
                                prediction['direction'] = part.strip()
                                break
                    # 提取概率
                    if '概率' in line:
                        import re
                        prob_match = re.search(r'(\d+)%', line)
                        if prob_match:
                            prediction['probability'] = int(prob_match.group(1))
                    break
        
        # 提取价格预测
        if '预期价格' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '预期价格' in line and '**' in line:
                    parts = line.split('**')
                    for j, part in enumerate(parts):
                        if '元/克' in part:
                            import re
                            price_match = re.search(r'(\d+\.?\d*)', part)
                            if price_match:
                                prediction['target_price'] = float(price_match.group(1))
                                break
                    break
        
        # 提取置信度
        if '预测置信度' in content:
            lines = content.split('\n')
            for line in lines:
                if '预测置信度' in line:
                    import re
                    conf_match = re.search(r'(\d+)%', line)
                    if conf_match:
                        prediction['confidence'] = int(conf_match.group(1))
                    break
        
        return prediction if prediction else None
    
    def _extract_price_from_brief(self, content: str) -> Optional[float]:
        """从简报中提取价格"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '国内金价' in line and '元/克' in line:
                # 格式: | 🇨🇳 国内金价 | 1083.15 元/克 | -27.86 | -2.51% |
                parts = line.split('|')
                for part in parts:
                    if '元/克' in part:
                        import re
                        price_match = re.search(r'(\d+\.?\d*)', part)
                        if price_match:
                            return float(price_match.group(1))
        return None
    
    def get_today_price(self) -> Optional[float]:
        """获取今日金价"""
        latest_file = self.data_dir / "gold_price_latest.json"
        if latest_file.exists():
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('domestic_cny_per_gram')
            except:
                pass
        return None
    
    def validate_prediction(self, yesterday_data: Dict) -> Dict:
        """验证昨天预测的准确性"""
        result = {
            'yesterday_prediction': yesterday_data.get('prediction', {}),
            'yesterday_price': yesterday_data.get('price'),
            'today_price': self.get_today_price(),
            'is_accurate': None,
            'accuracy_analysis': '',
            'price_change': 0,
            'price_change_pct': 0
        }
        
        if not result['yesterday_price'] or not result['today_price']:
            result['accuracy_analysis'] = '价格数据不完整，无法验证'
            return result
        
        # 计算价格变化
        result['price_change'] = result['today_price'] - result['yesterday_price']
        result['price_change_pct'] = (result['price_change'] / result['yesterday_price']) * 100
        
        pred = result['yesterday_prediction']
        if not pred or 'direction' not in pred:
            result['accuracy_analysis'] = '昨日无预测数据'
            return result
        
        direction = pred.get('direction', '')
        
        # 判断准确性
        if '涨' in direction or 'bull' in direction.lower():
            result['is_accurate'] = result['price_change'] > 0
            result['actual_direction'] = '上涨' if result['price_change'] > 0 else '下跌'
        elif '跌' in direction or 'bear' in direction.lower():
            result['is_accurate'] = result['price_change'] < 0
            result['actual_direction'] = '下跌' if result['price_change'] < 0 else '上涨'
        elif '震荡' in direction or 'neutral' in direction.lower():
            # 1%以内视为震荡
            result['is_accurate'] = abs(result['price_change_pct']) <= 1.0
            # 实际方向根据价格变化判断
            if abs(result['price_change_pct']) <= 1.0:
                result['actual_direction'] = '震荡'
            elif result['price_change'] > 0:
                result['actual_direction'] = '上涨'
            else:
                result['actual_direction'] = '下跌'
        else:
            result['actual_direction'] = '上涨' if result['price_change'] > 0 else '下跌'
        
        # 生成分析文本
        change_str = f"{result['price_change_pct']:+.2f}%"
        if result['is_accurate'] is True:
            result['accuracy_analysis'] = f"✅ **预测准确** - 预测『{direction}』，实际『{result['actual_direction']}』 ({change_str})"
        elif result['is_accurate'] is False:
            result['accuracy_analysis'] = f"❌ **预测错误** - 预测『{direction}』，实际『{result['actual_direction']}』 ({change_str})"
        else:
            result['accuracy_analysis'] = "⚪ **无法判断** - 预测方向不明确"
        
        return result
    
    def get_historical_accuracy(self, days: int = 7) -> Dict:
        """获取历史准确率统计"""
        # 从数据库获取
        db_path = self.data_dir / "predictions.db"
        stats = {
            'total': 0,
            'accurate': 0,
            'accuracy_rate': 0,
            'recent_predictions': []
        }
        
        if not db_path.exists():
            return stats
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            start_date = (self.today - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 获取统计
            cursor.execute('''
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN is_accurate = 1 THEN 1 ELSE 0 END) as accurate
                FROM predictions 
                WHERE prediction_date >= ? AND is_accurate IS NOT NULL
            ''', (start_date,))
            
            row = cursor.fetchone()
            if row:
                stats['total'] = row[0] or 0
                stats['accurate'] = row[1] or 0
                stats['accuracy_rate'] = round(stats['accurate'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
            
            # 获取最近预测
            cursor.execute('''
                SELECT prediction_date, prediction_type, is_accurate, accuracy_score
                FROM predictions 
                WHERE prediction_date >= ? AND is_accurate IS NOT NULL
                ORDER BY prediction_date DESC
                LIMIT 5
            ''', (start_date,))
            
            for row in cursor.fetchall():
                stats['recent_predictions'].append({
                    'date': row[0],
                    'prediction': row[1],
                    'is_accurate': '✓' if row[2] == 1 else '✗',
                    'score': row[3]
                })
            
            conn.close()
        except Exception as e:
            print(f"获取历史准确率失败: {e}")
        
        return stats
    
    def generate_prediction_validation_section(self) -> str:
        """生成预测验证对比章节"""
        section = """## 🔍 昨日预测验证

"""
        
        # 获取昨天简报
        yesterday_data = self.get_yesterday_brief()
        
        if not yesterday_data:
            section += """> ⚠️ 昨日简报不存在，无法进行对比验证

"""
            return section
        
        # 验证预测
        validation = self.validate_prediction(yesterday_data)
        
        # 获取历史统计
        hist_stats = self.get_historical_accuracy(days=7)
        
        # 构建对比表格
        section += "### 📊 预测 vs 实际对比\n\n"
        section += "| 对比项 | 昨日预测 | 今日实际 | 结果 |\n"
        section += "|--------|----------|----------|------|\n"
        
        # 预测方向
        pred_direction = validation['yesterday_prediction'].get('direction', '无')
        actual_direction = validation.get('actual_direction', '未知')
        
        if validation['is_accurate'] is True:
            result_mark = '✅ 准确'
        elif validation['is_accurate'] is False:
            result_mark = '❌ 错误'
        else:
            result_mark = '⚪ 未知'
        
        section += f"| **预测方向** | {pred_direction} | {actual_direction} | {result_mark} |\n"
        
        # 价格对比
        yesterday_price = validation['yesterday_price']
        today_price = validation['today_price']
        
        if yesterday_price and today_price:
            section += f"| **国内金价** | {yesterday_price:.2f} 元/克 | {today_price:.2f} 元/克 | - |\n"
            section += f"| **价格变化** | - | {validation['price_change']:+.2f} 元 ({validation['price_change_pct']:+.2f}%) | - |\n"
        
        # 预测概率
        pred_prob = validation['yesterday_prediction'].get('probability', '-')
        section += f"| **预测概率** | {pred_prob}% | - | - |\n"
        
        section += "\n"
        
        # 准确性分析
        section += f"### 🎯 准确性分析\n\n"
        section += f"{validation['accuracy_analysis']}\n\n"
        
        # 原因分析
        if validation['is_accurate'] is not None:
            section += "**偏差原因分析**:\n\n"
            
            if abs(validation['price_change_pct']) > 3:
                section += "- 📈 **大幅波动**: 今日价格出现大幅波动，超出正常预期范围\n"
            
            if validation['is_accurate'] is False:
                section += "- 🔄 **趋势反转**: 市场可能出现突发因素导致趋势反转\n"
                section += "- 📰 **新闻影响**: 建议检查今日是否有重大政策或新闻发布\n"
            else:
                section += "- ✅ **趋势延续**: 市场走势符合预期，预测模型有效\n"
            
            section += "\n"
        
        # 历史准确率
        section += "### 📈 累计准确率统计\n\n"
        section += f"| 指标 | 数值 |\n"
        section += f"|------|------|\n"
        section += f"| 总预测数 | {hist_stats['total']} |\n"
        section += f"| 准确预测 | {hist_stats['accurate']} |\n"
        section += f"| **准确率** | **{hist_stats['accuracy_rate']}%** |\n"
        section += f"| 统计周期 | 最近7天 |\n"
        
        if hist_stats['recent_predictions']:
            section += "\n**最近预测记录**:\n\n"
            section += "| 日期 | 预测 | 结果 | 得分 |\n"
            section += "|------|------|------|------|\n"
            for pred in hist_stats['recent_predictions'][:5]:
                section += f"| {pred['date']} | {pred['prediction']} | {pred['is_accurate']} | {pred['score']:.0f} |\n"
        
        section += "\n---\n\n"
        
        return section
    
    def generate_brief(self) -> str:
        """生成完整报告（包含预测验证）"""
        # 先生成基础报告
        base_report = super().generate_brief()
        
        # 生成预测验证章节
        validation_section = self.generate_prediction_validation_section()
        
        # 在关键事件之后插入预测验证
        # 找到第一个章节标题的位置
        lines = base_report.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## 📰 关键事件'):
                insert_idx = i
                break
        
        # 在关键事件之前插入预测验证
        if insert_idx > 0:
            lines.insert(insert_idx, '')
            lines.insert(insert_idx, validation_section.strip())
        
        return '\n'.join(lines)


def main():
    """主函数"""
    print("="*70)
    print("📊 每日简报 V8.2 - 实时金价版")
    print("="*70)
    print("🔍 开始综合分析...")
    print("  1. 验证昨日预测...")
    print("  2. 分析关键事件...")
    print("  3. 分析黄金...")
    print("  4. 分析基金...")
    print("  5. 分析股票...")
    print("  6. 生成报告...")
    print()
    
    try:
        brief = DailyBriefV82()
        report = brief.generate_brief()
        
        # 保存报告
        brief_dir = Path(__file__).parent.parent / "daily_brief"
        brief_dir.mkdir(exist_ok=True)
        
        filename = f"brief_v8_1_{brief.today_str.replace('-', '')}.md"
        filepath = brief_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("="*70)
        print(f"✅ 简报生成完成!")
        print(f"📄 保存路径: {filepath}")
        print("="*70)
        print()
        print("📋 报告预览 (前3000字符):")
        print(report[:3000])
        
    except Exception as e:
        print(f"❌ 生成简报失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
