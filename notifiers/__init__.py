"""
通知推送模块 - 告警、飞书、邮件推送

职责：
- 告警通知（价格突破、预测置信度低）
- 飞书推送
- 邮件推送（可选）
"""

from .base import Notifier, NotifierConfig
from .alert_notifier import AlertNotifier

__all__ = [
    'Notifier',
    'NotifierConfig',
    'AlertNotifier',
]

__version__ = '1.0.0'
