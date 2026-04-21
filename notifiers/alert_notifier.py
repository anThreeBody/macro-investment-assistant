#!/usr/bin/env python3
"""
告警通知器 - 价格突破、预测置信度低等告警
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from notifiers.base import Notifier, NotifierConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertNotifier(Notifier):
    """告警通知器"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "alerts"
        
        config = NotifierConfig(
            name='告警通知器',
            notifier_type='alert',
            enabled=True,
        )
        super().__init__(config)
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def send(self, message: str, **kwargs) -> bool:
        """
        发送告警（保存到文件）
        
        Args:
            message: 告警内容
            **kwargs: 额外参数
                - level: 告警级别（info/warning/error）
                - category: 告警类别（price/prediction/system）
                
        Returns:
            bool: 是否保存成功
        """
        level = kwargs.get('level', 'info')
        category = kwargs.get('category', 'general')
        
        logger.info(f"[告警通知] {level.upper()} - {message[:50]}...")
        
        # 生成告警记录
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"alert_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"时间：{timestamp}\n")
                f.write(f"级别：{level.upper()}\n")
                f.write(f"类别：{category}\n")
                f.write(f"\n{message}\n")
            
            logger.info(f"[告警通知] 告警已保存：{filepath}")
            return True
            
        except Exception as e:
            logger.error(f"[告警通知] 保存失败：{e}")
            return False
    
    def alert_price_breakout(self, current_price: float, threshold: float, 
                            direction: str) -> bool:
        """
        价格突破告警
        
        Args:
            current_price: 当前价格
            threshold: 突破阈值
            direction: 方向（up/down）
            
        Returns:
            bool: 是否发送成功
        """
        message = f"""
💰 价格突破告警

当前价格：¥{current_price}
突破阈值：¥{threshold}
突破方向：{'上涨' if direction == 'up' else '下跌'}

请及时关注市场变化！
"""
        return self.send(message, level='warning', category='price')
    
    def alert_low_confidence(self, prediction: Dict[str, Any]) -> bool:
        """
        低置信度告警
        
        Args:
            prediction: 预测结果
            
        Returns:
            bool: 是否发送成功
        """
        confidence = prediction.get('confidence', 'N/A')
        score = prediction.get('confidence_score', 0)
        
        message = f"""
⚠️ 低置信度预测告警

预测置信度：{confidence}
置信度得分：{score:.3f}

预测详情:
- 当前价格：¥{prediction.get('current_price', 'N/A')}
- 预测价格：¥{prediction.get('predicted_price', 'N/A')}
- 预测方向：{prediction.get('direction_label', 'N/A')}

建议：谨慎参考此预测，等待更高置信度信号。
"""
        return self.send(message, level='warning', category='prediction')
    
    def alert_system_error(self, error_message: str) -> bool:
        """
        系统错误告警
        
        Args:
            error_message: 错误信息
            
        Returns:
            bool: 是否发送成功
        """
        message = f"""
❌ 系统错误告警

错误信息：
{error_message}

请立即检查系统状态！
"""
        return self.send(message, level='error', category='system')
    
    def get_alert_history(self, days: int = 7, category: Optional[str] = None) -> list:
        """
        获取历史告警
        
        Args:
            days: 天数
            category: 类别筛选
            
        Returns:
            list: 告警列表
        """
        import glob
        
        pattern = "alert_*.txt"
        if category:
            pattern = f"alert_{category}_*.txt"
        
        files = sorted(glob.glob(str(self.output_dir / pattern)), reverse=True)
        
        alerts = []
        for filepath in files[:100]:  # 最多返回 100 条
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                alerts.append({
                    'file': Path(filepath).name,
                    'content': content,
                })
            except Exception as e:
                logger.error(f"[告警通知] 读取失败：{e}")
        
        return alerts
