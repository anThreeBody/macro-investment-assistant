#!/usr/bin/env python3
"""
实时推送服务
当识别到最佳买卖时机时主动推送通知
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PushNotification:
    """推送通知"""
    title: str
    message: str
    signal_type: str  # BUY/SELL/HOLD
    confidence: str   # HIGH/MEDIUM/LOW
    current_price: float
    target_price: float
    stop_loss: float
    take_profit: float
    reason: str
    timestamp: str
    urgency: str      # immediate/normal/low
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class RealTimePusher:
    """实时推送服务"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 推送阈值配置
        self.push_thresholds = {
            "min_confidence": 0.7,      # 最小推送置信度
            "high_confidence": 0.85,    # 高置信度阈值
            "cooldown_minutes": 30,     # 推送冷却时间（分钟）
            "max_daily_pushes": 10,     # 每日最大推送次数
        }
        
        # 推送历史
        self.push_history: List[Dict] = []
        self.last_push_time: Optional[datetime] = None
        self.daily_push_count: int = 0
        self.last_reset_date: datetime = datetime.now().date()
        
        # 回调函数（用于外部通知）
        self.callbacks: List[Callable] = []
        
        # 推送存储
        self.push_log_dir = Path(__file__).parent.parent / "logs" / "pushes"
        self.push_log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[实时推送] 服务初始化完成")
    
    def should_push(self, signal: Dict) -> bool:
        """
        判断是否应该推送
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 是否应该推送
        """
        # 检查置信度
        confidence_score = signal.get("confidence_score", 0)
        if confidence_score < self.push_thresholds["min_confidence"]:
            logger.debug(f"[推送判断] 置信度不足: {confidence_score:.2f} < {self.push_thresholds['min_confidence']}")
            return False
        
        # 检查信号类型
        signal_type = signal.get("signal_type", "HOLD")
        if signal_type == "HOLD":
            logger.debug("[推送判断] 持有信号，不推送")
            return False
        
        # 重置每日计数
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_push_count = 0
            self.last_reset_date = current_date
            logger.info("[推送判断] 重置每日推送计数")
        
        # 检查每日推送上限
        if self.daily_push_count >= self.push_thresholds["max_daily_pushes"]:
            logger.warning(f"[推送判断] 已达到每日推送上限: {self.push_thresholds['max_daily_pushes']}")
            return False
        
        # 检查冷却时间
        if self.last_push_time:
            time_since_last = datetime.now() - self.last_push_time
            if time_since_last < timedelta(minutes=self.push_thresholds["cooldown_minutes"]):
                remaining = self.push_thresholds["cooldown_minutes"] - time_since_last.seconds // 60
                logger.debug(f"[推送判断] 冷却中，还需 {remaining} 分钟")
                return False
        
        return True
    
    def create_notification(self, signal: Dict) -> PushNotification:
        """创建推送通知"""
        
        signal_type = signal.get("signal_type", "HOLD")
        confidence = signal.get("confidence", "LOW")
        current_price = signal.get("current_price", 0)
        target_price = signal.get("target_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        take_profit = signal.get("take_profit", 0)
        reason = signal.get("reason", "")
        
        # 确定紧急程度
        confidence_score = signal.get("confidence_score", 0)
        if confidence_score >= self.push_thresholds["high_confidence"]:
            urgency = "immediate"
        elif confidence_score >= 0.75:
            urgency = "normal"
        else:
            urgency = "low"
        
        # 构建标题
        if signal_type == "BUY":
            title = f"🟢 买入信号 | 黄金 {confidence}置信度"
        elif signal_type == "SELL":
            title = f"🔴 卖出信号 | 黄金 {confidence}置信度"
        else:
            title = f"⚪ 观望信号 | 黄金"
        
        # 构建消息
        message = f"""
当前价格: ${current_price:.2f}/盎司
建议操作: {signal_type}
目标价格: ${target_price:.2f}
止损价格: ${stop_loss:.2f}
止盈价格: ${take_profit:.2f}

{reason}

⏰ {datetime.now().strftime('%H:%M:%S')}
        """.strip()
        
        return PushNotification(
            title=title,
            message=message,
            signal_type=signal_type,
            confidence=confidence,
            current_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            urgency=urgency
        )
    
    def push(self, signal: Dict) -> bool:
        """
        执行推送
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 推送是否成功
        """
        if not self.should_push(signal):
            return False
        
        try:
            # 创建通知
            notification = self.create_notification(signal)
            
            # 保存推送记录
            self._save_push(notification)
            
            # 更新状态
            self.last_push_time = datetime.now()
            self.daily_push_count += 1
            
            # 执行回调
            self._execute_callbacks(notification)
            
            # 控制台输出（模拟推送）
            self._console_output(notification)
            
            logger.info(f"[实时推送] 推送成功: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"[实时推送] 推送失败: {e}")
            return False
    
    def _save_push(self, notification: PushNotification):
        """保存推送记录"""
        # 保存到日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = self.push_log_dir / f"pushes_{date_str}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(notification.to_dict(), ensure_ascii=False) + '\n')
        
        # 添加到历史
        self.push_history.append(notification.to_dict())
    
    def _execute_callbacks(self, notification: PushNotification):
        """执行回调函数"""
        for callback in self.callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"[实时推送] 回调执行失败: {e}")
    
    def _console_output(self, notification: PushNotification):
        """控制台输出（模拟推送效果）"""
        print("\n" + "="*60)
        print("🔔 实时推送通知")
        print("="*60)
        print(f"\n{notification.title}")
        print(f"\n{notification.message}")
        print(f"\n紧急程度: {notification.urgency}")
        print(f"时间: {notification.timestamp}")
        print("="*60 + "\n")
    
    def register_callback(self, callback: Callable):
        """注册回调函数"""
        self.callbacks.append(callback)
        logger.info(f"[实时推送] 注册回调函数: {callback.__name__}")
    
    def get_push_stats(self) -> Dict:
        """获取推送统计"""
        today = datetime.now().date()
        today_pushes = [p for p in self.push_history 
                       if datetime.fromisoformat(p['timestamp']).date() == today]
        
        return {
            "total_pushes": len(self.push_history),
            "today_pushes": len(today_pushes),
            "daily_limit": self.push_thresholds["max_daily_pushes"],
            "remaining_today": self.push_thresholds["max_daily_pushes"] - len(today_pushes),
            "last_push_time": self.last_push_time.isoformat() if self.last_push_time else None,
            "cooldown_minutes": self.push_thresholds["cooldown_minutes"]
        }
    
    def get_recent_pushes(self, hours: int = 24) -> List[Dict]:
        """获取最近推送"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [p for p in self.push_history 
                if datetime.fromisoformat(p['timestamp']) > cutoff]


class PushScheduler:
    """推送调度器"""
    
    def __init__(self, pusher: RealTimePusher):
        self.pusher = pusher
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self, check_interval: int = 60):
        """启动调度器"""
        if self.running:
            logger.warning("[推送调度] 已在运行")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(check_interval,))
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"[推送调度] 已启动，检查间隔: {check_interval}秒")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[推送调度] 已停止")
    
    def _run(self, check_interval: int):
        """运行循环"""
        while self.running:
            try:
                # 这里可以集成实际的信号检查逻辑
                # 例如：从队列中获取新信号并推送
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"[推送调度] 运行错误: {e}")
                time.sleep(5)


# 便捷函数
def send_push_notification(signal: Dict, config: Optional[Dict] = None) -> bool:
    """
    发送推送通知
    
    Args:
        signal: 交易信号
        config: 推送配置
        
    Returns:
        bool: 是否成功
    """
    pusher = RealTimePusher(config)
    return pusher.push(signal)


def demo_push():
    """演示推送功能"""
    print("=== 实时推送服务演示 ===\n")
    
    # 创建推送服务
    pusher = RealTimePusher()
    
    # 模拟高置信度买入信号
    buy_signal = {
        "signal_type": "BUY",
        "confidence": "HIGH",
        "confidence_score": 0.88,
        "current_price": 4576.30,
        "target_price": 4603.18,
        "stop_loss": 4552.42,
        "take_profit": 4622.06,
        "reason": "买入信号: RSI超卖(28.5); MACD金叉; 接近支撑位(4564.85)"
    }
    
    print("1. 测试高置信度买入信号推送...")
    result = pusher.push(buy_signal)
    print(f"推送结果: {'成功' if result else '失败'}\n")
    
    # 模拟低置信度信号（不应推送）
    low_signal = {
        "signal_type": "BUY",
        "confidence": "LOW",
        "confidence_score": 0.55,
        "current_price": 4576.30,
        "target_price": 4603.18,
        "stop_loss": 4552.42,
        "take_profit": 4622.06,
        "reason": "潜在买入: RSI超卖(28.5)"
    }
    
    print("2. 测试低置信度信号（应被过滤）...")
    result = pusher.push(low_signal)
    print(f"推送结果: {'成功' if result else '失败'} (预期: 失败)\n")
    
    # 模拟持有信号（不应推送）
    hold_signal = {
        "signal_type": "HOLD",
        "confidence": "MEDIUM",
        "confidence_score": 0.70,
        "current_price": 4576.30,
        "target_price": 4576.30,
        "stop_loss": 4530.54,
        "take_profit": 4622.06,
        "reason": "观望: 信号不足"
    }
    
    print("3. 测试持有信号（应被过滤）...")
    result = pusher.push(hold_signal)
    print(f"推送结果: {'成功' if result else '失败'} (预期: 失败)\n")
    
    # 显示统计
    stats = pusher.get_push_stats()
    print("=== 推送统计 ===")
    print(f"总推送次数: {stats['total_pushes']}")
    print(f"今日推送: {stats['today_pushes']}")
    print(f"今日剩余: {stats['remaining_today']}")
    print(f"最后推送: {stats['last_push_time']}")


if __name__ == "__main__":
    demo_push()
