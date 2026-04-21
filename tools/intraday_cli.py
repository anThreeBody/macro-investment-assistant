#!/usr/bin/env python3
"""
黄金日内交易 CLI 工具
提供命令行接口进行日内分析和实时推送
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.gold_intraday_service import GoldIntradayService
from analyzers.accuracy_tracker import AccuracyTracker


def cmd_analyze(args):
    """分析当前交易机会"""
    print("🔍 分析当前黄金交易机会...")
    
    service = GoldIntradayService()
    
    # 使用实时数据或示例数据
    current_price = args.price if args.price else 4576.30
    
    # 模拟小时数据
    hourly_prices = [
        4550.0, 4560.0, 4565.0, 4570.0, 4568.0,
        4572.0, 4575.0, 4578.0, 4576.0, 4574.0,
        4576.30, 4575.0, 4574.0, 4573.0, 4572.0
    ]
    
    result = service.analyze_current_opportunity(current_price, hourly_prices)
    
    print(f"\n📊 分析结果:")
    print(f"  当前价格: ${result['current_price']:.2f}")
    print(f"  信号类型: {result['signal']['signal_type']}")
    print(f"  置信度: {result['signal']['confidence']} ({result['signal']['confidence_score']:.2f})")
    print(f"  目标价格: ${result['signal']['target_price']:.2f}")
    print(f"  止损价格: ${result['signal']['stop_loss']:.2f}")
    print(f"  止盈价格: ${result['signal']['take_profit']:.2f}")
    print(f"  最佳机会: {'是' if result['is_best_opportunity'] else '否'}")
    
    print(f"\n💡 建议:")
    print(result['recommendation'])


def cmd_report(args):
    """生成日内交易报告"""
    print("📄 生成日内交易报告...")
    
    service = GoldIntradayService()
    report = service.generate_intraday_report()
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "daily_brief" / f"intraday_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {report_file}")
    
    if args.show:
        print("\n" + "="*70)
        print(report)


def cmd_accuracy(args):
    """显示准确率统计"""
    print("📊 预测准确率统计...")
    
    tracker = AccuracyTracker()
    
    if args.days:
        # 显示指定天数
        stats = tracker.calculate_accuracy(args.days)
        print(f"\n📈 {args.days}天准确率:")
        print(f"  总预测: {stats['total_predictions']}")
        print(f"  正确: {stats['correct_predictions']}")
        print(f"  准确率: {stats['accuracy_rate']}%")
        print(f"  平均误差: {stats['avg_error_rate']}%")
    else:
        # 显示所有周期
        stats = tracker.get_all_accuracy_stats()
        
        print("\n📈 准确率统计:")
        print(f"\n  7天:")
        print(f"    预测数: {stats['7_days']['total_predictions']}")
        print(f"    准确率: {stats['7_days']['accuracy_rate']}%")
        
        print(f"\n  30天:")
        print(f"    预测数: {stats['30_days']['total_predictions']}")
        print(f"    准确率: {stats['30_days']['accuracy_rate']}%")
        
        print(f"\n  90天:")
        print(f"    预测数: {stats['90_days']['total_predictions']}")
        print(f"    准确率: {stats['90_days']['accuracy_rate']}%")
    
    tracker.close()


def cmd_best_hours(args):
    """显示最佳交易时段"""
    print("⏰ 黄金最佳交易时段:")
    print()
    print("  亚洲时段: 09:00-17:00 (波动: 中)")
    print("  欧洲时段: 15:00-23:00 (波动: 高)")
    print("  美洲时段: 21:00-05:00 (波动: 最高)")
    print()
    print("  💡 最佳时段:")
    print("    • 欧美重叠: 21:00-23:00 (高波动)")
    print("    • 亚欧重叠: 15:00-17:00 (中波动)")
    print()
    print("  📌 建议:")
    print("    • 优先关注 21:00-23:00 欧美重叠时段")
    print("    • 避免 05:00-09:00 低波动时段")


def main():
    parser = argparse.ArgumentParser(
        description='黄金日内交易分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python intraday_cli.py analyze              # 分析当前机会
  python intraday_cli.py analyze --price 4600 # 指定价格分析
  python intraday_cli.py report               # 生成报告
  python intraday_cli.py accuracy             # 显示准确率
  python intraday_cli.py accuracy --days 7    # 显示7天准确率
  python intraday_cli.py best-hours           # 显示最佳时段
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析当前交易机会')
    analyze_parser.add_argument('--price', type=float, help='指定当前金价')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成日内交易报告')
    report_parser.add_argument('--show', action='store_true', help='显示报告内容')
    
    # accuracy 命令
    accuracy_parser = subparsers.add_parser('accuracy', help='显示准确率统计')
    accuracy_parser.add_argument('--days', type=int, help='指定天数(7/30/90)')
    
    # best-hours 命令
    subparsers.add_parser('best-hours', help='显示最佳交易时段')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'accuracy':
        cmd_accuracy(args)
    elif args.command == 'best-hours':
        cmd_best_hours(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
