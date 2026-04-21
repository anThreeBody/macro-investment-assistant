#!/usr/bin/env python3
"""
基金分析 CLI 工具
提供命令行接口进行基金分析和推荐
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.fund_analysis_service import FundAnalysisService
from analyzers.fund_recommender import RiskProfile


def cmd_recommend(args):
    """基金推荐"""
    print("🎯 基金个性化推荐\n")
    
    service = FundAnalysisService()
    
    # 确定风险偏好
    risk_map = {
        "conservative": RiskProfile.CONSERVATIVE,
        "moderate": RiskProfile.MODERATE,
        "balanced": RiskProfile.BALANCED,
        "aggressive": RiskProfile.AGGRESSIVE,
        "speculative": RiskProfile.SPECULATIVE
    }
    
    risk_profile = risk_map.get(args.risk, RiskProfile.MODERATE)
    
    print(f"风险偏好: {risk_profile.value}")
    print(f"推荐数量: {args.top_n}\n")
    
    # 获取推荐
    result = service.get_personalized_recommendations(risk_profile, args.top_n)
    
    print("💼 组合配置建议:")
    for fund_type, percentage in result['portfolio_suggestion'].items():
        if fund_type != 'description':
            print(f"  {fund_type}: {percentage}%")
    print(f"  说明: {result['portfolio_suggestion']['description']}\n")
    
    print(f"⭐ 推荐基金 (Top {result['total_recommended']}):\n")
    
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec['name']} ({rec['code']})")
        print(f"   类型: {rec['category']} | 风险等级: {rec['risk_level']}")
        print(f"   近1年收益: {rec['return_1y']*100:.1f}% | 波动率: {rec['volatility']*100:.1f}%")
        print(f"   最大回撤: {rec['max_drawdown']*100:.1f}% | 规模: {rec['fund_size']}亿")
        print(f"   综合得分: {rec['score']:.1f}")
        print(f"   推荐理由: {rec['reason']}\n")


def cmd_timing(args):
    """买卖点建议"""
    print(f"🎯 基金买卖点建议 - {args.code}\n")
    
    service = FundAnalysisService()
    
    # 模拟数据
    current_nav = args.nav if args.nav else 2.50
    
    nav_history = [
        2.60, 2.58, 2.59, 2.57, 2.55, 2.56, 2.54, 2.52, 2.53, 2.51,
        2.50, 2.48, 2.49, 2.47, 2.46, 2.45, 2.44, 2.45, 2.43, 2.42,
        2.44, 2.43, 2.45, 2.44, 2.46, 2.45, 2.46, 2.45, 2.47, current_nav
    ]
    
    fund_info = {
        "manager_score": 4.2,
        "fund_size": 60,
        "expense_ratio": 0.015,
        "return_1y": 0.18
    }
    
    market_data = {
        "market_sentiment": "neutral",
        "fund_flow": 50,
        "policy": "supportive"
    }
    
    result = service.get_timing_advice(
        args.code, args.code, current_nav,
        nav_history, fund_info, market_data
    )
    
    print(f"📊 分析结果:")
    print(f"  操作建议: {result['action']}")
    print(f"  信号强度: {result['strength']}")
    print(f"  置信度: {result['confidence']:.1%}")
    print(f"  当前净值: {result['current_nav']:.4f}")
    print(f"  目标价格: {result['target_price']:.4f}")
    print(f"  止损价格: {result['stop_loss']:.4f}")
    print(f"  止盈价格: {result['take_profit']:.4f}\n")
    
    print(f"💡 交易理由:")
    print(f"  {result['reason']}\n")
    
    if result['action'] == "BUY":
        print("🟢 买入策略:")
    elif result['action'] == "SELL":
        print("🔴 卖出策略:")
    else:
        print("⚪ 持有策略:")
    
    print(result['strategy'][:500] + "...")


def cmd_report(args):
    """生成基金报告"""
    print("📄 生成基金分析报告...\n")
    
    service = FundAnalysisService()
    
    risk_map = {
        "conservative": RiskProfile.CONSERVATIVE,
        "moderate": RiskProfile.MODERATE,
        "balanced": RiskProfile.BALANCED,
        "aggressive": RiskProfile.AGGRESSIVE,
        "speculative": RiskProfile.SPECULATIVE
    }
    
    risk_profile = risk_map.get(args.risk, RiskProfile.MODERATE)
    
    report = service.generate_fund_report(risk_profile)
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "daily_brief" / f"fund_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存: {report_file}\n")
    
    if args.show:
        print("="*70)
        print(report)


def cmd_assess(args):
    """风险评估"""
    print("🎯 风险偏好评估\n")
    
    service = FundAnalysisService()
    risk_profile = service.interactive_assessment()
    
    print(f"\n✅ 您的风险偏好是: {risk_profile.value}")
    print("\n可以使用以下命令获取推荐:")
    print(f"  python fund_cli.py recommend --risk {risk_profile.name.lower()}")


def main():
    parser = argparse.ArgumentParser(
        description='基金分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基金推荐
  python fund_cli.py recommend --risk moderate --top-n 5
  
  # 买卖点建议
  python fund_cli.py timing --code 005911 --nav 2.4567
  
  # 生成报告
  python fund_cli.py report --risk balanced --show
  
  # 风险评估
  python fund_cli.py assess

风险偏好选项:
  conservative  - 保守型
  moderate      - 稳健型 (默认)
  balanced      - 平衡型
  aggressive    - 进取型
  speculative   - 激进型
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # recommend 命令
    recommend_parser = subparsers.add_parser('recommend', help='基金推荐')
    recommend_parser.add_argument('--risk', default='moderate',
                                 choices=['conservative', 'moderate', 'balanced', 'aggressive', 'speculative'],
                                 help='风险偏好')
    recommend_parser.add_argument('--top-n', type=int, default=5, help='推荐数量')
    
    # timing 命令
    timing_parser = subparsers.add_parser('timing', help='买卖点建议')
    timing_parser.add_argument('--code', required=True, help='基金代码')
    timing_parser.add_argument('--nav', type=float, help='当前净值')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成基金报告')
    report_parser.add_argument('--risk', default='moderate',
                              choices=['conservative', 'moderate', 'balanced', 'aggressive', 'speculative'],
                              help='风险偏好')
    report_parser.add_argument('--show', action='store_true', help='显示报告内容')
    
    # assess 命令
    subparsers.add_parser('assess', help='风险评估')
    
    args = parser.parse_args()
    
    if args.command == 'recommend':
        cmd_recommend(args)
    elif args.command == 'timing':
        cmd_timing(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'assess':
        cmd_assess(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
