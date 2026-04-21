#!/usr/bin/env python3
"""
预测验证脚本 - 每日运行验证昨日预测

使用方法：
python3 scripts/verify_predictions.py [actual_price]

如果没有提供实际价格，使用当前国内金价
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from predictors.validator import PredictionValidator
from data_sources.gold_source import GoldDataSource

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_yesterday_predictions(actual_price: float = None):
    """验证昨天的预测"""
    
    # 1. 获取昨天的日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    logger.info(f"开始验证 {yesterday} 的预测")
    
    # 2. 获取实际金价（如果未提供）
    if actual_price is None:
        try:
            gold_ds = GoldDataSource()
            gold_data = gold_ds.fetch()
            actual_price = gold_data['domestic']['price']
            logger.info(f"获取到当前金价：¥{actual_price:.2f}")
        except Exception as e:
            logger.error(f"获取金价失败：{e}")
            return False
    
    # 3. 验证预测
    validator = PredictionValidator(db_path='data/predictions.db')
    result = validator.verify_prediction(yesterday, actual_price)
    
    if result:
        logger.info("="*60)
        logger.info("✅ 验证完成")
        logger.info("="*60)
        logger.info(f"预测价格：¥{result['predicted']:.2f}")
        logger.info(f"实际价格：¥{result['actual']:.2f}")
        logger.info(f"绝 对 误 差：¥{result['error']:.2f}")
        logger.info(f"相 对 误 差：{result['error_pct']:.2%}")
        logger.info(f"准 确 率：{result['accuracy']:.2%}")
        logger.info(f"方向判断：{'✅ 正确' if result['direction_correct'] else '❌ 错误'}")
        logger.info(f"区间命中：{'✅' if result['in_range'] else '❌'}")
        logger.info("="*60)
        return True
    else:
        logger.warning(f"⚠️  {yesterday} 没有需要验证的预测")
        return False


if __name__ == '__main__':
    # 支持命令行参数
    actual_price = None
    if len(sys.argv) > 1:
        try:
            actual_price = float(sys.argv[1])
        except ValueError:
            logger.error(f"无效的价格参数：{sys.argv[1]}")
            sys.exit(1)
    
    success = verify_yesterday_predictions(actual_price)
    sys.exit(0 if success else 1)
