#!/usr/bin/env python3
"""
投资分析系统 V8.0 - 主入口

统一入口，提供简洁的命令行接口
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor
from predictors.validator import PredictionValidator
from presenters.brief_generator_enhanced import BriefGeneratorEnhanced
from presenters.chart_generator import ChartGenerator
from notifiers.alert_notifier import AlertNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InvestmentSystem:
    """投资分析系统主类"""
    
    def __init__(self):
        self.data_api = DataAPI()
        self.predictor = MultiFactorPredictor()
        self.validator = PredictionValidator(db_path='data/predictions.db')
        self.brief_gen = BriefGeneratorEnhanced()
        self.chart_gen = ChartGenerator()
        self.alert = AlertNotifier()
    
    def run_daily_brief(self, save: bool = True, generate_charts: bool = False) -> dict:
        """
        运行每日简报
        
        Args:
            save: 是否保存结果
            generate_charts: 是否生成图表
            
        Returns:
            dict: 简报数据
        """
        logger.info("=" * 50)
        logger.info("📊 投资分析系统 V8.0 - 每日简报")
        logger.info("=" * 50)
        
        # 1. 获取所有数据
        logger.info("\n📥 步骤 1: 获取数据...")
        data = self.data_api.get_all_data()
        
        # 2. 生成预测
        logger.info("\n🔮 步骤 2: 生成预测...")
        prediction = self.predictor.predict(data)
        
        # 2.1 保存预测到数据库（新增）
        logger.info("\n💾 步骤 2.1: 保存预测记录...")
        self.validator.save_prediction(prediction)
        
        # 3. 生成简报（Markdown）
        logger.info("\n📝 步骤 3: 生成简报...")
        brief_content = self.brief_gen.generate(data, prediction)
        
        # 4. 生成图表（可选）
        if generate_charts:
            logger.info("\n📊 步骤 4: 生成图表...")
            prices = data.get('prices', [])
            if prices:
                self.chart_gen.generate_price_chart(prices, title="金价走势")
            self.chart_gen.generate_prediction_chart(
                data.get('gold', {}).get('domestic', {}).get('price', 0),
                prediction
            )
            analysis = prediction.get('analysis', {})
            self.chart_gen.generate_factor_heatmap(
                analysis.get('scores', {}),
                analysis.get('weights', {})
            )
        
        # 5. 检查告警
        logger.info("\n🔔 步骤 5: 检查告警...")
        self._check_alerts(data, prediction)
        
        # 6. 组装数据
        brief = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'prediction': prediction,
            'brief_content': brief_content,
        }
        
        # 7. 保存 JSON（可选）
        if save:
            logger.info("\n💾 步骤 6: 保存数据...")
            filename = f"brief_v8_{datetime.now().strftime('%Y%m%d')}"
            filepath = self.data_api.save_snapshot(brief, filename)
            logger.info(f"简报数据已保存：{filepath}")
        
        # 8. 输出摘要
        self._print_summary(brief)
        
        return brief
    
    def run_prediction(self, save: bool = True) -> dict:
        """
        仅运行预测
        
        Args:
            save: 是否保存结果
            
        Returns:
            dict: 预测结果
        """
        logger.info("=" * 50)
        logger.info("🔮 投资分析系统 V8.0 - 预测")
        logger.info("=" * 50)
        
        # 获取数据
        logger.info("\n📥 步骤 1: 获取数据...")
        data = self.data_api.get_all_data()
        
        # 生成预测
        logger.info("\n🔮 步骤 2: 生成预测...")
        prediction = self.predictor.predict(data)
        
        # 2.1 保存预测到数据库（新增）
        if save:
            logger.info("\n💾 步骤 2.1: 保存预测记录到数据库...")
            self.validator.save_prediction(prediction)
        
        # 3. 保存 JSON（可选）
        if save:
            logger.info("\n💾 步骤 3: 保存预测到 JSON...")
            filename = f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.data_api.save_snapshot(prediction, filename)
            logger.info(f"预测已保存：{filepath}")
        
        # 输出
        self._print_prediction(prediction)
        
        return prediction
    
    def get_data(self, data_type: str = 'all') -> dict:
        """
        获取数据
        
        Args:
            data_type: 数据类型（gold/fund/stock/news/macro/all）
            
        Returns:
            dict: 数据
        """
        logger.info(f"📥 获取 {data_type} 数据...")
        
        if data_type == 'gold':
            return self.data_api.get_gold_price()
        elif data_type == 'news':
            return self.data_api.get_news(days=1)
        elif data_type == 'macro':
            return self.data_api.get_macro()
        elif data_type == 'all':
            return self.data_api.get_all_data()
        else:
            logger.error(f"未知数据类型：{data_type}")
            return {}
    
    def _check_alerts(self, data: dict, prediction: dict):
        """检查并发送告警"""
        # 低置信度告警
        confidence = prediction.get('confidence', '')
        if confidence == '低':
            self.alert.alert_low_confidence(prediction)
        
        # 价格大幅波动告警
        change_pct = abs(prediction.get('change_pct', 0))
        if change_pct > 2:  # 预测涨跌幅超过 2%
            direction = 'up' if prediction.get('change_pct', 0) > 0 else 'down'
            current = prediction.get('current_price', 0)
            threshold = current * (1 + 0.02 if direction == 'up' else -0.02)
            self.alert.alert_price_breakout(current, threshold, direction)
    
    def _print_summary(self, brief: dict):
        """打印简报摘要"""
        print("\n" + "=" * 50)
        print("📊 每日简报摘要")
        print("=" * 50)
        
        # 金价
        gold = brief['data'].get('gold', {})
        print(f"\n💰 金价:")
        print(f"  国际：${gold.get('international', {}).get('price', 'N/A')}")
        print(f"  国内：¥{gold.get('domestic', {}).get('price', 'N/A')}")
        
        # 宏观
        macro = brief['data'].get('macro', {})
        print(f"\n🌍 宏观:")
        print(f"  DXY: {macro.get('dxy', {}).get('value', 'N/A')}")
        print(f"  VIX: {macro.get('vix', {}).get('value', 'N/A')}")
        
        # 新闻情绪
        news = brief['data'].get('news', {})
        sentiment = news.get('sentiment', {})
        print(f"\n📰 新闻情绪:")
        print(f"  得分：{sentiment.get('overall_score', 'N/A')}")
        
        # 预测
        pred = brief.get('prediction', {})
        print(f"\n🔮 预测:")
        print(f"  当前价格：¥{pred.get('current_price', 'N/A')}")
        print(f"  预测价格：¥{pred.get('predicted_price', 'N/A')}")
        print(f"  预测方向：{pred.get('direction_label', 'N/A')}")
        print(f"  置信度：{pred.get('confidence', 'N/A')}")
        print(f"  交易信号：{pred.get('signal_label', 'N/A')}")
        
        print("\n" + "=" * 50)
    
    def _print_prediction(self, prediction: dict):
        """打印预测详情"""
        print("\n" + "=" * 50)
        print("🔮 预测详情")
        print("=" * 50)
        
        print(f"\n当前价格：¥{prediction.get('current_price', 'N/A')}")
        print(f"预测价格：¥{prediction.get('predicted_price', 'N/A')}")
        print(f"预测区间：¥{prediction.get('price_lower', 'N/A')} - ¥{prediction.get('price_upper', 'N/A')}")
        print(f"预测方向：{prediction.get('direction_label', 'N/A')}")
        print(f"涨跌幅：{prediction.get('change_pct', 'N/A')}%")
        print(f"置信度：{prediction.get('confidence', 'N/A')}")
        print(f"交易信号：{prediction.get('signal_label', 'N/A')}")
        
        # 各因子得分
        analysis = prediction.get('analysis', {})
        scores = analysis.get('scores', {})
        if scores:
            print(f"\n各因子得分:")
            for factor, score in scores.items():
                bias = '看多' if score > 0 else ('看空' if score < 0 else '中性')
                print(f"  {factor}: {score:.3f} ({bias})")
        
        print("\n" + "=" * 50)
    
    def close(self):
        """关闭系统"""
        self.data_api.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='投资分析系统 V8.0')
    
    parser.add_argument(
        'command',
        choices=['brief', 'predict', 'data'],
        help='命令：brief(每日简报), predict(预测), data(获取数据)'
    )
    
    parser.add_argument(
        '--data-type',
        choices=['gold', 'fund', 'stock', 'news', 'macro', 'all'],
        default='all',
        help='数据类型（仅 data 命令使用）'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='不保存结果'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    system = InvestmentSystem()
    
    try:
        if args.command == 'brief':
            system.run_daily_brief(save=not args.no_save)
        elif args.command == 'predict':
            system.run_prediction(save=not args.no_save)
        elif args.command == 'data':
            data = system.get_data(args.data_type)
            print(f"\n数据已获取：{len(str(data))} 字节")
    finally:
        system.close()


if __name__ == '__main__':
    main()
