#!/usr/bin/env python3
"""
通知器基类
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NotifierConfig:
    """通知器配置"""
    name: str                          # 通知器名称
    notifier_type: str                 # 类型：alert/feishu/email
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


class Notifier(ABC):
    """通知器基类"""
    
    def __init__(self, config: NotifierConfig):
        self.config = config
    
    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """
        发送通知（抽象方法）
        
        Args:
            message: 通知内容
            
        Returns:
            bool: 是否发送成功
        """
        pass
    
    def format_message(self, title: str, content: str, level: str = 'info') -> str:
        """
        格式化消息
        
        Args:
            title: 标题
            content: 内容
            level: 级别（info/warning/error）
            
        Returns:
            str: 格式化后的消息
        """
        emoji = {
            'info': '📊',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
        }.get(level, '📊')
        
        return f"{emoji} **{title}**\n\n{content}"
