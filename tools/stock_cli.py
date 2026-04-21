#!/usr/bin/env python3
"""
股票分析 CLI 工具
提供命令行接口进行股票分析
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.stock_analysis_service import StockAnalysisService


def cmd_analyze(args):
    """分析个股"""
    print(f"🎯 分析个股: {args.code}\n")
    
    service = StockAnalysisService()
    
    # 模拟数据
    stock_data = {
        "code": args.code,
        "name": args.name if args.name else args.code,
        "industry": args.industry if args.industry else "未知",
        "current_price": args.price if args.price else 10.0,
        "price_history": [10.0 + i * 0.02 for i in range(60)],
        "volume_history": [1000000 + i * 500 for i in range(60)],
        "fundamental_data": {
            "pe": args.pe if args.pe else 20.0,
            "pb": args.pb if args.pb else 2.0,
            "roe": 12.0,
            "revenue_growth": 10.0,
            "profit_growth": 15.0,
            "debt_ratio": 50.0
        },
        "capital_data": {
            "main_force": 1.0,
            "north_bound": 0.5,
            "turnover": 5.0,
            "margin": 10.0
        }
    }
    
    result = service.analyze_stock(**stock_data)
    
    print(f"📊 分析结果:")
    print(f"  股票: {result['name']} ({result['code']})")
    print(f"  行业: {result['industry']}")
    print(f"  当前价格: ¥{result['current_price']:.2f}")
    print(f"  信号: {result['signal']}")
    print(f"  置信度: {result['confidence']:.1%}")
    print(f"  目标价格: ¥{result['target_price']:.2f}")
    print(f"  止损价格: ¥{result['stop_loss']:.2f}")
    print(f"  止盈价格: ¥{result['take_profit']:.2f}")
    print(f"  建议仓位: {result['position_size']}")
    print(f"  风险等级: {result['risk_level']}")
    
    print(f"\n评分:")
    print(f"  技术面: {result['technical_score']:.1%}")
    print(f"  基本面: {result['fundamental_score']:.1%}")
    print(f"  资金面: {result['capital_score']:.1%}")
    
    print(f"\n💡 核心逻辑:")
    print(f"  {result['overall_reason']}")
    
    if args.detail:
        print(f"\n{'='*70}")
        print("📊 详细分析")
        print(f"{'='*70}")
        print(result['detailed_analysis']['technical'][:800])


def cmd_picks(args):
    """今日精选"""
    print("⭐ 今日精选股票\n")
    
    service = StockAnalysisService()
    picks = service.get_top_picks(top_n=args.top_n)
    
    for i, pick in enumerate(picks, 1):
        print(f"{i}. {pick['name']} ({pick['code']})")
        print(f"   行业: {pick['industry']}")
        print(f"   信号: {pick['signal']} | 置信度: {pick['confidence']:.1%}")
        print(f"   理由: {pick['reason']}\n")


def cmd_report(args):
    """生成股票报告"""
    print("📄 生成股票分析报告...\n")
    
    service = StockAnalysisService()
    
    # 模拟多只股票
    stocks_data = [
        {
            "code": "000001",
            "name": "平安银行",
            "industry": "银行",
            "current_price": 12.50,
            "price_history": [10.0 + i * 0.05 for i in range(60)],
            "volume_history": [1000000 + i * 1000 for i in range(60)],
            "fundamental_data": {"pe": 8.5, "pb": 0.9, "roe": 12.5, "revenue_growth": 8.0, "profit_growth": 10.0, "debt_ratio": 92.0},
            "capital_data": {"main_force": 1.5, "north_bound": 0.8, "turnover": 5.0, "margin": 15.0}
        },
        {
            "code": "000858",
            "name": "五粮液",
            "industry": "白酒",
            "current_price": 150.0,
            "price_history": [140.0 + i * 0.2 for i in range(60)],
            "volume_history": [500000 + i * 200 for i in range(60)],
            "fundamental_data": {"pe": 25.0, "pb": 8.0, "roe": 25.0, "revenue_growth": 15.0, "profit_growth": 20.0, "debt_ratio": 20.0},
            "capital_data": {"main_force": 2.0, "north_bound": 1.2, "turnover": 3.0, "margin": 20.0}
        }
    ]
    
    report = service.generate_stock_report(stocks_data)
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "daily_brief" / f"stock_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存: {report_file}\n")
    
    if args.show:
        print("="*70)
        print(report[:1000] + "...")


def main():
    parser = argparse.ArgumentParser(
        description='股票分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析个股
  python stock_cli.py analyze --code 000001 --name 平安银行 --price 12.50
  
  # 今日精选
  python stock_cli.py picks --top-n 5
  
  # 生成报告
  python stock_cli.py report --show
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析个股')
    analyze_parser.add_argument('--code', required=True, help='股票代码')
    analyze_parser.add_argument('--name', help='股票名称')
    analyze_parser.add_argument('--industry', help='所属行业')
    analyze_parser.add_argument('--price', type=float, help='当前价格')
    analyze_parser.add_argument('--pe', type=float, help='市盈率')
    analyze_parser.add_argument('--pb', type=float, help='市净率')
    analyze_parser.add_argument('--detail', action='store_true', help='显示详细分析')
    
    # picks 命令
    picks_parser = subparsers.add_parser('picks', help='今日精选')
    picks_parser.add_argument('--top-n', type=int, default=5, help='数量')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成股票报告')
    report_parser.add_argument('--show', action='store_true', help='显示报告内容')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'picks':
        cmd_picks(args)
    elif args.command == 'report':
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
